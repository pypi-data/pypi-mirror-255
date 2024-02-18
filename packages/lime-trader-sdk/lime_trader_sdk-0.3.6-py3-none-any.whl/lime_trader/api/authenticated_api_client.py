from logging import Logger
from typing import TypeVar, Type, Callable, Any

from urllib3.util import Url
from websocket import WebSocketApp

from lime_trader.models.accounts import Token, Credentials
from lime_trader.api.api_client import ApiClient
from lime_trader.models.token_storage import TokenStorage

T = TypeVar("T")


class AuthenticatedApiClient:
    """
    Used for communication with the API while being authenticated. It supports using different endpoint
    for authentication to support a case when authorization server is on different domain
    """

    def __init__(self, api_client: ApiClient, token_storage: TokenStorage, credentials: Credentials, logger: Logger):
        """
        Args:
            api_client: API client used for executing all requests
            token_storage: Token storage used for getting/setting token
            param credentials: Credentials used for API authentication
            logger: Used for logging information about executed requests
        """
        self._api_client = api_client
        self._token_storage = token_storage
        self._credentials = credentials
        self._logger = logger

    def _get_authorization_header_for_token(self, token: Token) -> dict[str, str]:
        """
        Constructs headers required for authorization with existing token.

        Args:
            token: Token information

        Returns:
            Headers required for authorization
        """
        return {"Authorization": f"Bearer {token.access_token}"}

    def _get_authorization_header(self) -> dict[str, str]:
        """
        Gets required authorization header. If token is already fetched, it uses it, if not, it fetches new token.

        Returns:
            Authorization headers
        """
        return self._get_authorization_header_for_token(self._token_storage.get_token())

    def get(self, url: Url, path_params: dict[str, Any], params: Any, response_schema: Type[T]) -> T:
        """
        Forwards GET request to underlying API client

        Args:
            url: Url path.
            path_params: URL path parameters
            params: GET parameters
            response_schema: Python type to which response data will be transformed

        Returns:
            Response converted to Python type passed as response_schema parameter
        """
        return self._api_client.get(url=url, path_params=path_params, params=params,
                                    headers=self._get_authorization_header(),
                                    response_schema=response_schema)

    def post_form(self, url: Url, path_params: dict[str, Any], data: Any, response_schema: Type[T]) -> T:
        """
        Forwards POST request with form data to underlying API client

        Args:
            url: Url path.
            path_params: URL path parameters
            data: Form data
            response_schema: Python type to which response data will be transformed

        Returns:
            Response converted to Python type passed as response_schema parameter
        """
        return self._api_client.post_form(url=url, path_params=path_params, data=data,
                                          headers=self._get_authorization_header(),
                                          response_schema=response_schema)

    def post(self, url: Url, path_params: dict[str, Any], json: Any, response_schema: Type[T]) -> T:
        """
        Forwards POST request with JSON data to underlying API client

        Args:
            url: Url path.
            path_params: URL path parameters
            json: JSON data
            response_schema: Python type to which response data will be transformed

        Returns:
            Response converted to Python type passed as response_schema parameter
        """
        return self._api_client.post(url=url, path_params=path_params, json=json,
                                     headers=self._get_authorization_header(),
                                     response_schema=response_schema)

    def websocket_connection(self, url: Url, path_params: dict[str, Any], on_message: Callable, on_error: Callable,
                             ) -> WebSocketApp:
        return self._api_client.websocket_connection(url=url, path_params=path_params,
                                                     on_message=on_message, on_error=on_error,
                                                     headers=self._get_authorization_header(),
                                                     )
