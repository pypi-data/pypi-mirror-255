from datetime import timedelta

from lime_trader.api.api_client import ApiClient
from lime_trader.async_trader.api.async_api_client import AsyncApiClient
from lime_trader.constants.urls import AUTHENTICATION_GET_TOKEN
from lime_trader.models.accounts import Token, Credentials


class TokenStorage:

    def __init__(self):
        self._token = None

    def get_token(self) -> Token:
        return self._token

    def set_token(self, token: Token) -> None:
        self._token = token


class ApiTokenStorage(TokenStorage):

    def __init__(self, credentials: Credentials, api_client: ApiClient):
        super().__init__()
        self._credentials = credentials
        self._api_client = api_client

    def _get_token(self) -> Token:
        """
        Gets new token by executing API request

        Returns:
            Access token
        """
        return self._api_client.post_form(AUTHENTICATION_GET_TOKEN, path_params={}, data=self._credentials,
                                          response_schema=Token,
                                          headers={})

    def _validate_token(self, token: Token | None) -> bool:
        """
        Validates token by checking if it is fetched already or expires soon

        Args:
            token: Token to validate

        Returns:
            True if token is valid and can be used for authorization, False otherwise
        """
        if token is None or token.expires_in_delta() < timedelta(minutes=2):
            return False
        return True

    def get_token(self) -> Token:
        if not self._validate_token(token=self._token):
            self._token = self._get_token()
        return self._token

    def set_token(self, token: Token) -> None:
        self._token = token


class AsyncApiTokenStorage(ApiTokenStorage):

    def __init__(self, credentials: Credentials, api_client: AsyncApiClient):
        super().__init__(credentials=credentials, api_client=api_client)

    async def _get_token(self) -> Token:
        """
        Gets new token by executing API request

        Returns:
            Access token
        """
        return await self._api_client.post_form(AUTHENTICATION_GET_TOKEN, path_params={}, data=self._credentials,
                                                response_schema=Token,
                                                headers={})

    def _validate_token(self, token: Token | None) -> bool:
        """
        Validates token by checking if it is fetched already or expires soon

        Args:
            token: Token to validate

        Returns:
            True if token is valid and can be used for authorization, False otherwise
        """
        if token is None or token.expires_in_delta() < timedelta(minutes=2):
            return False
        return True

    async def get_token(self) -> Token:
        if not self._validate_token(token=self._token):
            self._token = await self._get_token()
        return self._token

    def set_token(self, token: Token) -> None:
        self._token = token
