from typing import TypeVar, Type, Any
import httpx
from urllib3.util import Url

from lime_trader.api.api_client import ApiClient
from lime_trader.exceptions.api_error import ApiError
from lime_trader.models.errors import Error
from lime_trader.utils.logging_utils import log_json_data

T = TypeVar("T")


class AsyncApiClient(ApiClient):

    async def get(self, url: Url, path_params: dict[str, Any], params: Any, headers: dict[str, str],
                  response_schema: Type[T]) -> T:
        request_url = self._get_url(url, path_params=path_params)
        dict_params = self._converter.dump_to_dict(params, remove_none=True)
        self._logger.debug(f"Executing GET request {request_url}, params={log_json_data(dict_params)}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url=request_url, params=dict_params, headers=headers, timeout=self._timeout)
            except httpx.TransportError as e:
                raise ApiError(
                    Error(status_code=None,
                          code="transport_error",
                          message=f"Transport error: {e.__class__.__name__}.{''.join(e.args)}")
                )
        return self._handle_response(response=response, response_schema=response_schema)

    async def post_form(self, url: Url, path_params: dict[str, Any], data: Any, headers: dict[str, str],
                        response_schema: Type[T]) -> T:
        request_url = self._get_url(url, path_params=path_params)
        dict_data = self._converter.dump_to_dict(data, remove_none=True)
        self._logger.debug(f"Executing POST request {request_url}, data={log_json_data(dict_data)}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url=request_url, data=dict_data, headers=headers, timeout=self._timeout)
            except httpx.TransportError as e:
                raise ApiError(
                    Error(status_code=None,
                          code="transport_error",
                          message=f"Transport error: {e.__class__.__name__}.{''.join(e.args)}")
                )
        return self._handle_response(response=response, response_schema=response_schema)

    async def post(self, url: Url, path_params: dict[str, Any], json: Any, headers: dict[str, str],
                   response_schema: Type[T]) -> T:
        request_url = self._get_url(url, path_params=path_params)
        dict_data = self._prepare_json_body(json)
        self._logger.debug(f"Executing POST request {request_url}, json={log_json_data(dict_data)}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url=request_url, json=dict_data, headers=headers, timeout=self._timeout)
            except httpx.TransportError as e:
                raise ApiError(
                    Error(status_code=None,
                          code="transport_error",
                          message=f"Transport error: {e.__class__.__name__}.{''.join(e.args)}")
                )
        return self._handle_response(response=response, response_schema=response_schema)
