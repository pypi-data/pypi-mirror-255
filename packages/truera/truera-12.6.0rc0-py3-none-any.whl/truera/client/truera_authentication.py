import time
from typing import Callable, Mapping, Optional

import jwt
import requests

from truera.client.public.auth_details import AuthDetails
from truera.client.public.auth_details import AuthDetailsMode


class TrueraAuthentication:

    def get_auth_details(self) -> AuthDetails:
        pass

    def set_token_endpoint(
        self, endpoint: str, append_path=True, overwrite=False
    ):
        pass


class AnonAuthentication(TrueraAuthentication):

    def __init__(self) -> None:
        self.auth_details = AuthDetails(mode=AuthDetailsMode.ANON_AUTH)

    def get_auth_details(self) -> AuthDetails:
        return self.auth_details


class BasicAuthentication(TrueraAuthentication):
    """Basic authentication for BaseTrueraWorkspace.
    """

    def __init__(self, username: str, password: str) -> None:
        """Construct `BasicAuth` for BaseTrueraWorkspace.

        Args:
            username: Username for the basic auth credentials.
            password: Password for the basic auth credentials.
        
        Note: Most users will use TokenAuthentication rather than BasicAuthentication.
        
        Examples:
        ```python

        # import BasicAuthentication and TruEraWorkspace
        >>> from truera.client.truera_authentication import BasicAuthentication
        >>> from truera.client.truera_workspace import TrueraWorkspace

        # Create authentication object
        >>> auth = BasicAuthentication(username="My Username", password="My Password")

        # Create TruEra Workspace
        >>> tru = TrueraWorkspace(connection_string="https://myconnectionstring", authentication=auth)
        ```
        """
        self.auth_details = AuthDetails(
            mode=AuthDetailsMode.BASIC_AUTH,
            username=username,
            password=password
        )

    def get_auth_details(self) -> AuthDetails:
        return self.auth_details


class TokenAuthentication(TrueraAuthentication):
    """Token authentication for BaseTrueraWorkspace.
    """

    def __init__(self, token: str) -> None:
        """Construct `TokenAuth` for BaseTrueraWorkspace.

        Args:
            token: Token containing credentials to authenticate with the services.

        Note: Most users will use TokenAuthentication rather than BasicAuthentication.

        Examples:
        ```python

        # import TokenAuthentication and TruEraWorkspace
        >>> from truera.client.truera_authentication import TokenAuthentication
        >>> from truera.client.truera_workspace import TrueraWorkspace

        # Create authentication object
        >>> auth = TokenAuthentication(token="My Token From the TruEra Web App")

        # Create TruEra Workspace
        >>> tru = TrueraWorkspace(connection_string="https://myconnectionstring", authentication=auth)
        ```
        """
        self.token = Token(value=token)
        self.auth_details = AuthDetails(
            mode=AuthDetailsMode.TOKEN_AUTH, token=self.token
        )

    def get_auth_details(self) -> AuthDetails:
        return self.auth_details


class ServiceAccountAuthentication(TrueraAuthentication):
    """Service Account Authentication for BaseTrueraWorkspace.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        token_endpoint: Optional[str] = None,
        additional_payload: Optional[Mapping[str, str]] = None,
        verify_cert: Optional[bool] = True
    ):
        """Construct `ServiceAccountAuth` for BaseTrueraWorkspace.

        Args:
            client_id: Client ID from service account credentials.
            client_secret: Client secret from service account credentials.
            token_endpoint: Optional override of the endpoint to retrieve token from.
            additional_payload: Optional payload to include in request to retrieve token.
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.token_endpoint = token_endpoint

        self.token = Token(refresh_func=self._get_token_refresh_func())
        self.additional_payload = additional_payload or {}
        self.auth_details = AuthDetails(
            mode=AuthDetailsMode.TOKEN_AUTH, token=self.token
        )
        self.verify_cert = verify_cert

    def get_auth_details(self) -> AuthDetails:
        if not self.token_endpoint:
            raise RuntimeError(
                "token_endpoint is not set, call set_token_endpoint(). Please contact TruEra support."
            )
        return self.auth_details

    def set_token_endpoint(
        self, endpoint: str, append_path=True, overwrite=False
    ):
        '''Set token endpoint.
        Appends '/oauth/token' to endpoint if append_path is True.
        Does nothing if token_endpoint is already defined unless overwrite is True.
        '''
        if self.token_endpoint is not None and not overwrite:
            return

        if endpoint:
            self.token_endpoint = f"{endpoint}/oauth/token" if append_path else endpoint
        else:
            raise ValueError("`endpoint` is empty")

    def _get_token_refresh_func(self) -> Callable[[], str]:

        # Expects self.token_endpoint to be set before refresh_func is called
        # Python scope handles class variables changing on the fly

        def refresh_func() -> str:
            payload = {
                **self.additional_payload, 'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            resp = requests.post(
                self.token_endpoint,
                data=payload,
                headers=headers,
                verify=self.verify_cert
            )
            try:
                resp.raise_for_status()
                return resp.json()['access_token']
            except requests.HTTPError as e:
                raise RuntimeError(
                    f"Could not get service account token, response status code: {e.response.status_code}"
                )

        return refresh_func


class Token:

    def __init__(
        self, value: str = None, refresh_func: Callable[[], str] = None
    ):
        if not (value or refresh_func):
            raise ValueError(
                "Either a value or a refresh_func must be provided to Token class."
            )
        self._token = value
        self.refresh_func = refresh_func

    def __str__(self):
        """Support implicit usage of this class in `str(Token)` or `f"{Token}"`.
        """
        return self.value()

    def value(self) -> str:
        if not self._token or self.is_expired():
            if self.refresh_func:
                self._token = self.refresh_func()
            else:
                raise RuntimeError("The provided token has expired.")
        return self._token

    def _get_decoded_token(self) -> dict:
        try:
            return jwt.decode(self._token, options={'verify_signature': False})
        except jwt.DecodeError:
            raise ValueError(
                "Could not decode authentication token. Please check if provided token is malformed."
            )

    def is_expired(self) -> bool:
        decoded_jwt = self._get_decoded_token()
        return time.time() > decoded_jwt['exp']
