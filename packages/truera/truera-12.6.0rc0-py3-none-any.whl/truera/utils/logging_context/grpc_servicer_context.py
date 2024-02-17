import json
import logging
import os
import threading

import ecs_logging

from truera.authn.usercontext import GrpcContextExtractor
from truera.authn.usercontext import RequestContext

_local = threading.local()


def initialize_grpc_servicer_context(func):
    """Decorator for grpc Servicer methods, to set Logging context on Threading local.
    Logger will log all the fields from TrueraLoggingContext within the Servicer thread.
    """

    def wrapper(self, request, context):
        context_extractor = GrpcContextExtractor(context.invocation_metadata())
        _local.logging_request_context = TrueraLoggingContext(
            context_extractor.extract_context()
        )
        result = func(self, request, context)
        if hasattr(_local, 'logging_request_context'):
            delattr(_local, 'logging_request_context')
        return result

    return wrapper


class TrueraLoggingContext:
    """Logging context for Python logging to include request level context.
    """

    def __init__(
        self,
        request_context: RequestContext,
    ):
        self.tenant_id = request_context.get_user_context().get_tenant_id()
        self.request_id = request_context.get_request_id()
        self.user_id = request_context.get_user_context().get_id()
        self.deployment_id = os.environ.get("DEPLOYMENT_ID", "no_deployment_id")

    def __str__(self):
        return f"[REQUEST_ID:{self.request_id}] [TENANT_ID:{str(self.tenant_id)}] [USER_ID:{str(self.user_id)}] [DEPLOYMENT_ID:{str(self.deployment_id)}]"

    def dict(self):
        return {
            "tenant_id": self.tenant_id,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "deployment_id": self.deployment_id
        }


class ContextFormatter(logging.Formatter):

    def format(self, record):
        if hasattr(_local, 'logging_request_context'):
            record.logging_request_context = _local.logging_request_context
        else:
            record.logging_request_context = "[NO-LOGGING-CONTEXT]"
        return super().format(record)


class StdContextFormatter(logging.Formatter):

    def format(self, record):
        if hasattr(_local, 'logging_request_context'):
            record.logging_request_context = _local.logging_request_context.dict(
            )
        else:
            record.logging_request_context = {}
        return super().format(record)


class ECSContextFormatter(ecs_logging.StdlibFormatter):

    def format(self, record):
        result = super().format_to_ecs(record)
        if hasattr(_local, 'logging_request_context'):
            result['logging_request_context'
                  ] = _local.logging_request_context.dict()
        else:
            result['logging_request_context'] = {}
        return json.dumps(result)