import logging
import time
from typing import List, Mapping, Optional

from prometheus_client import Histogram
import redis

from truera.authn.usercontext import RequestContext
from truera.utils.timing_logger import process_timer_msg

_GET_TIMER = Histogram(
    'redis_wrapper_get_time_seconds', 'Redis GET wrapper latency (in seconds)'
)
_MGET_TIMER = Histogram(
    'redis_wrapper_mget_time_seconds', 'Redis MGET wrapper latency (in seconds)'
)
_HGETALL_TIMER = Histogram(
    'redis_wrapper_hgetall_time_seconds',
    'Redis HGETALL wrapper latency (in seconds)'
)
_HSET_TIMER = Histogram(
    'redis_wrapper_hset_time_seconds', 'Redis HSET wrapper latency (in seconds)'
)
_KEYS_TIMER = Histogram(
    'redis_wrapper_keys_time_seconds', 'Redis KEYS wrapper latency (in seconds)'
)
_SET_TIMER = Histogram(
    'redis_wrapper_set_time_seconds', 'Redis SET wrapper latency (in seconds)'
)
_MSET_TIMER = Histogram(
    'redis_wrapper_mset_time_seconds', 'Redis MSET wrapper latency (in seconds)'
)
_DELETE_TIMER = Histogram(
    'redis_wrapper_delete_time_seconds',
    'Redis DELETE wrapper latency (in seconds)'
)


class PersistentKVStoreClient:

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[str] = None,
        password: Optional[str] = None,
        cluster_mode: bool = True,
        tls_connection: bool = False
    ):
        if host is not None and port is not None:
            if cluster_mode:
                self._redis_client = redis.cluster.RedisCluster(
                    host=host, port=port, password=password, ssl=tls_connection
                )
            else:
                self._redis_client = redis.Redis(
                    host=host, port=port, password=password, ssl=tls_connection
                )
        else:
            raise ValueError("Missing config to connect to Redis.")
        self._logger = logging.getLogger(__name__)

    @_GET_TIMER.time()
    def get(
        self,
        key: str,
        request_context: RequestContext,
        ttl_in_seconds: Optional[int] = None
    ) -> Optional[str]:
        """
        Returns the value associated with the key.

        Args:
            key: The key we want to retrieve the value for.
            request_context: Request context provides the tenant id to properly construct the Redis key as `tenant_id/key`.
            ttl_in_seconds: TTL for key in seconds. If set, we will reset the key ttl to make the more recently accessed keys available. Defaults to None.

        Returns:
            str: The value associated with the key.
        """
        self._redis_client.psync
        redis_key = self._get_redis_key(key, request_context)
        get_start_time = time.perf_counter()
        val = self._retry_on_error(self._redis_client.get, redis_key)
        self._logger.info(
            process_timer_msg(
                get_start_time, f"Fetched {redis_key} from cache",
                request_context
            )
        )
        if val is None:
            return None
        if ttl_in_seconds:
            self._retry_on_error(
                self._redis_client.expire, redis_key, ttl_in_seconds
            )
        return val.decode("utf-8")

    @_MGET_TIMER.time()
    def mget(
        self,
        keys: List[str],
        request_context: RequestContext,
        ttl_in_seconds: Optional[int] = None
    ) -> List[Optional[str]]:
        """
        Returns the value associated with the key.

        Args:
            keys: The set of keys we want to retrieve the values for.
            request_context: Request context provides the tenant id to properly construct the Redis key as `tenant_id/key`.
            ttl_in_seconds: TTL for key in seconds. If set, we will reset the key ttl to make the more recently accessed keys available. Defaults to None.

        Returns:
            List[Optional[str]]: The values associated with the keys.
        """
        self._redis_client.psync
        redis_keys = [self._get_redis_key(key, request_context) for key in keys]
        get_start_time = time.perf_counter()
        vals = self._retry_on_error(self._redis_client.mget, redis_keys)
        self._logger.info(
            process_timer_msg(
                get_start_time, f"Fetched {len(redis_keys)} keys from cache",
                request_context
            )
        )
        final_vals = []
        for (val, key) in zip(vals, redis_keys):
            if val is not None:
                final_vals.append(val.decode("utf-8"))
                if ttl_in_seconds:
                    self._retry_on_error(
                        self._redis_client.expire, key, ttl_in_seconds
                    )
            else:
                final_vals.append(None)
        return final_vals

    @_HGETALL_TIMER.time()
    def hgetall(
        self,
        key: str,
        request_context: RequestContext,
        ttl_in_seconds: Optional[int] = None
    ) -> Mapping[str, str]:
        """
        Returns the value associated with the key.

        Args:
            key: The hash name we want to retrieve the all the key-values pairs for.
            request_context: Request context provides the tenant id to properly construct the Redis key as `tenant_id/key`.
            ttl_in_seconds: TTL for key in seconds. If set, we will reset the key ttl to make the more recently accessed keys available. Defaults to None.

        Returns:
            Mapping[str, str]: A dictionary of all key-values present in the hash.
        """
        self._redis_client.psync
        redis_key = self._get_redis_key(key, request_context)
        get_start_time = time.perf_counter()
        val_dict = self._retry_on_error(self._redis_client.hgetall, redis_key)
        self._logger.info(
            process_timer_msg(
                get_start_time, f"Fetched {redis_key} from cache",
                request_context
            )
        )
        response_dict = {}
        for key, val in val_dict.items():
            response_dict[key.decode("utf-8")
                         ] = val.decode("utf-8") if val is not None else None
        if ttl_in_seconds:
            self._retry_on_error(
                self._redis_client.expire, redis_key, ttl_in_seconds
            )
        return response_dict

    @_HSET_TIMER.time()
    def hset(
        self,
        request_context: RequestContext,
        hash_key: str,
        key: Optional[str] = None,
        value: Optional[str] = None,
        mapping: Optional[dict] = None,
        ttl_in_seconds: Optional[int] = None
    ) -> int:
        """
        Returns the value associated with the key.

        Args:
            hash_key: The name for the hash to store multiple key-values in
            key: The key for the key-value we are setting.
            value: The val;ue for the key-value we are setting.
            request_context: Request context provides the tenant id to properly construct the Redis key as `tenant_id/key`.
            ttl_in_seconds: TTL for key in seconds. If set, we will reset the key ttl to make the more recently accessed keys available. Defaults to None.

        Returns:
            int: Number of fields that were set.
        """
        self._redis_client.psync
        redis_key = self._get_redis_key(hash_key, request_context)
        success = self._retry_on_error(
            self._redis_client.hset,
            name=redis_key,
            key=key,
            value=value,
            mapping=mapping
        )
        if ttl_in_seconds:
            self._retry_on_error(
                self._redis_client.expire, redis_key, ttl_in_seconds
            )
        return success

    @_KEYS_TIMER.time()
    def keys(self, prefix: str, request_context: RequestContext) -> list:
        """
        Returns keys matching a prefix.
        This is inefficient and slow as it will go through the entire set of keys and will match with each. We should avoid using it other than for debugging.

        Args:
            prefix: Prefix by which we want to return the keys. If prefix is `""`, it will return all keys.
            request_context: Request context provides the tenant id to properly construct the Redis key as `tenant_id/key`.

        Returns:
            list: List of keys matching this prefix.
        """
        tenant_id = request_context.get_user_context().get_tenant_id()
        # throw if tenant_id is None or empty
        if not tenant_id or len(tenant_id) == 0:
            raise ValueError("Tenant ID cannot be empty")
        redis_key = f"{tenant_id}/{prefix}*"
        self._logger.debug(f"Getting keys {redis_key}")
        return self._retry_on_error(self._redis_client.keys, redis_key)

    @_SET_TIMER.time()
    def set(
        self,
        key: str,
        value: str,
        request_context: RequestContext,
        ttl_in_seconds: Optional[int] = None
    ) -> bool:
        """
        Sets the value for the key. 
        Keys can be partitions with / for internal representation of hierarchy- Redis itself does not have any optimizations for keys.

        Args:
            key: Key we want to add to the store.
            value: Value associated with the key.
            request_context:  Request context provides the tenant id to properly construct the Redis key as `tenant_id/key`.
            ttl_in_seconds: TTL for key in seconds. If set, we will set the key ttl to value passed. Defaults to None.

        Returns:
            bool: Whether the set operation was performed or not
        """
        redis_key = self._get_redis_key(key, request_context)
        self._logger.debug(f"Setting key {redis_key} to {value}")
        return self._retry_on_error(
            self._redis_client.set, redis_key, value, ex=ttl_in_seconds
        )

    @_MSET_TIMER.time()
    def mset(
        self,
        keys: List[str],
        values: List[str],
        request_context: RequestContext,
        ttl_in_seconds: Optional[int] = None
    ) -> None:
        """
        Sets the values for multiple keys. 
        
        Args:
            keys: List of keys we want to add to the store.
            values: List of values associated with the keys. This needs to be the same length as the keys.
            request_context:  Request context provides the tenant id to properly construct the Redis key as `tenant_id/key`.
            ttl_in_seconds: TTL for key in seconds. If set, we will set the key ttl to value passed. Defaults to None.

        """
        mset_map = {}
        if len(keys) != len(values):
            raise ValueError("Invalid input for multi key set in Redis")
        for key, val in zip(keys, values):
            redis_key = self._get_redis_key(key, request_context)
            mset_map[redis_key] = val
        self._logger.debug(f"Setting {len(mset_map)} keys")
        self._retry_on_error(self._redis_client.mset, mset_map)
        if ttl_in_seconds:
            for key in mset_map.keys():
                self._retry_on_error(
                    self._redis_client.expire, key, ttl_in_seconds
                )

    @_DELETE_TIMER.time()
    def delete(self, keys: List[str], request_context: RequestContext) -> int:
        """
        Deletes given keys from the store.

        Args:
            key: Keys we want to delete from the store.
            request_context: Request context provides the tenant id to properly construct the Redis key as `tenant_id/key`.

        Returns:
            int: Number of keys deleted.
        """
        redis_keys = [self._get_redis_key(key, request_context) for key in keys]
        self._logger.debug(f"Deleting keys of length {len(redis_keys)}")
        return self._retry_on_error(self._redis_client.delete, *redis_keys)

    def _get_redis_key(self, key, request_context: RequestContext) -> str:
        tenant_id = request_context.get_user_context().get_tenant_id()
        # throw if tenant_id is None or empty
        if not tenant_id or len(tenant_id) == 0:
            raise ValueError("Tenant ID cannot be empty")
        return f"{tenant_id}/{key}"

    def _retry_on_error(
        self, func, *args, max_retries=3, retry_delay=1, **kwargs
    ):
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except (
                redis.exceptions.ConnectionError, redis.exceptions.TimeoutError
            ) as e:
                if i == max_retries - 1:
                    raise e
                self._logger.error(
                    f"Retryable error connecting to redis: {e}, retrying in {retry_delay} seconds"
                )
                time.sleep(retry_delay)
                continue
            except redis.exceptions.RedisError as e:
                self._logger.error(f"Error connecting to redis: {e}")
                raise e
