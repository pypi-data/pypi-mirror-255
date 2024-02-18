from typing import TypeVar, Type, Callable, Any

from urllib3.util import Url
from websocket import WebSocketApp

from lime_trader.api.authenticated_api_client import AuthenticatedApiClient

T = TypeVar("T")


class AsyncAuthenticatedApiClient(AuthenticatedApiClient):

    async def _get_authorization_header(self) -> dict[str, str]:
        return self._get_authorization_header_for_token(await self._token_storage.get_token())

    async def get(self, url: Url, path_params: dict[str, Any], params: Any, response_schema: Type[T]) -> T:
        return await self._api_client.get(url=url, path_params=path_params, params=params,
                                          headers=await self._get_authorization_header(),
                                          response_schema=response_schema)

    async def post_form(self, url: Url, path_params: dict[str, Any], data: Any, response_schema: Type[T]) -> T:
        return await self._api_client.post_form(url=url, path_params=path_params, data=data,
                                                headers=await self._get_authorization_header(),
                                                response_schema=response_schema)

    async def post(self, url: Url, path_params: dict[str, Any], json: Any, response_schema: Type[T]) -> T:
        return await self._api_client.post(url=url, path_params=path_params, json=json,
                                           headers=await self._get_authorization_header(),
                                           response_schema=response_schema)

    async def websocket_connection(self, url: Url, path_params: dict[str, Any], on_message: Callable,
                                   on_error: Callable,
                                   ) -> WebSocketApp:
        return self._api_client.websocket_connection(url=url, path_params=path_params,
                                                     on_message=on_message, on_error=on_error,
                                                     headers=await self._get_authorization_header(),
                                                     )
