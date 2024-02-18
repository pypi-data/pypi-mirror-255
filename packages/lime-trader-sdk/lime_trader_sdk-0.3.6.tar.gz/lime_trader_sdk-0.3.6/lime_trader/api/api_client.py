import logging
from json import JSONDecodeError
from logging import Logger
from typing import TypeVar, Type, Any, Callable
import httpx
import websocket
from httpx import Response, HTTPStatusError
from urllib3.util import Url

from lime_trader.converters.abstract_converter import AbstractConverter
from lime_trader.models.errors import Error
from lime_trader.exceptions.api_error import ApiError
from lime_trader.utils.logging_utils import log_json_data

T = TypeVar("T")


class ApiClient:
    """
    Used for communication with the API
    """

    def __init__(self, base_url: Url, converter: AbstractConverter, use_https: bool, use_wss: bool,
                 timeout: int,
                 logger: Logger):
        """
        Args:
            base_url: Base url that will be appended to all urls
            converter: Converter to use for transforming response data to Python objects
            use_https: Indicator if https protocol should be used, http is used if False
            use_wss: Indicator if wss protocol should be used, ws is used if False
            timeout: Request timeout
            logger: Logger to use for logging messages
        """
        self._base_url = base_url
        self._converter = converter
        self._use_https = use_https
        self._use_wss = use_wss
        self._timeout = timeout
        self._logger = logger

    def _map_response(self, data: dict[str, Any] | list[str, Any], t: Type[T]) -> T:
        """
        Does conversion between API response (json converted to dictionary) and Python type

        Args:
            data: Response data that needs to be converted
            t: Type to convert to

        Returns:
            Data converted to Python type passed as t parameter
        """
        return self._converter.load_from_dict(data, t)

    def _check_for_errors(self, response: Response) -> dict[str, Any]:
        """
        Checks for errors in a response. If there is, raises exception with returned error

        Args:
            response: Response to check for errors

        Returns:
            True if there is no error

        Raises:
            ApiError if response does not have success http status code
        """
        try:
            data = response.json()
        except JSONDecodeError as e:
            raise ApiError(
                Error(status_code=response.status_code,
                      code="json_decode_error",
                      message=e.msg)
            )
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            raise ApiError(
                Error(status_code=response.status_code,
                      code=data.get("code", ""),
                      message=data.get("message", ""))
            )

        return data

    def _handle_response(self, response: Response, response_schema: Type[T]) -> T:
        """
        Handles response by checking for errors and transforming data to appropriate Python type

        Args:
            response: Response returned from API
            response_schema: Python type to which response data will be transformed

        Returns:
            Pythonic type
        """
        response_data = self._check_for_errors(response)
        self._logger.debug(f"Response: {log_json_data(response_data)}")
        return self._map_response(response_data, response_schema)

    def get(self, url: Url, path_params: dict[str, Any], params: Any, headers: dict[str, str],
            response_schema: Type[T]) -> T:
        """
        Executes GET request with specified parameters

        Args:
            url: Url path.
            path_params: URL path parameters
            params: GET parameters
            headers: Request headers
            response_schema: Python type to which response data will be transformed

        Returns:
            Response converted to Python type passed as response_schema parameter
        """
        request_url = self._get_url(url, path_params=path_params)
        dict_params = self._converter.dump_to_dict(params, remove_none=True)
        self._logger.debug(f"Executing GET request {request_url}, params={log_json_data(dict_params)}")
        try:
            response = httpx.get(url=request_url, params=dict_params, headers=headers, timeout=self._timeout)
        except httpx.TransportError as e:
            raise ApiError(
                Error(status_code=None,
                      code="transport_error",
                      message=f"Transport error: {e.__class__.__name__}.{''.join(e.args)}")
            )
        return self._handle_response(response=response, response_schema=response_schema)

    def _get_url(self, path: Url, path_params: dict[str, Any]) -> str:
        """
        Gets full url by prefixing base url to path

        Args:
            path: Path to append to base url.
            path_params: URL path parameters

        Returns:
            Full url
        """
        if path.url.startswith("http://"):
            scheme = "https" if self._use_https else "http"
        elif path.url.startswith("ws://"):
            scheme = "wss" if self._use_wss else "ws"
        else:
            raise Exception("Invalid urls specified!")
        url = Url(scheme=scheme, path=(self._base_url.path or '') + path.path, host=self._base_url.hostname).url
        return url.format(**self._converter.dump_to_dict(path_params))

    def post_form(self, url: Url, path_params: dict[str, Any], data: Any, headers: dict[str, str],
                  response_schema: Type[T]) -> T:
        """
        Executes POST request with form data

        Args:
            url: Url path.
            path_params: URL path parameters
            data: Form data
            headers: Request headers
            response_schema: Python type to which response data will be transformed

        Returns:
            Response converted to Python type passed as response_schema parameter
        """
        request_url = self._get_url(url, path_params=path_params)
        dict_data = self._converter.dump_to_dict(data, remove_none=True)
        self._logger.debug(f"Executing POST request {request_url}, data={log_json_data(dict_data)}")
        try:
            response = httpx.post(url=request_url, data=dict_data, headers=headers, timeout=self._timeout)
        except httpx.TransportError as e:
            raise ApiError(
                Error(status_code=None,
                      code="transport_error",
                      message=f"Transport error: {e.__class__.__name__}.{''.join(e.args)}")
            )
        result = self._handle_response(response=response, response_schema=response_schema)
        return result

    def _prepare_json_body(self, json: Any) -> dict[str, Any] | list[dict[str, Any]]:
        if type(json) == list:
            return [self._converter.dump_to_dict(item, remove_none=True) for item in json]
        return self._converter.dump_to_dict(json, remove_none=True)

    def post(self, url: Url, path_params: dict[str, Any], json: Any, headers: dict[str, str],
             response_schema: Type[T]) -> T:
        """
        Executes POST request with JSON data

        Args:
            url: Url path.
            path_params: URL path parameters
            json: JSON data
            headers: Request headers
            response_schema: Python type to which response data will be transformed

        Returns:
            Response converted to Python type passed as response_schema parameter
        """
        request_url = self._get_url(url, path_params=path_params)
        dict_data = self._prepare_json_body(json)
        self._logger.debug(f"Executing POST request {request_url}, json={log_json_data(dict_data)}")
        try:
            response = httpx.post(url=request_url, json=dict_data, headers=headers, timeout=self._timeout)
        except httpx.TransportError as e:
            raise ApiError(
                Error(status_code=None,
                      code="transport_error",
                      message=f"Transport error: {e.__class__.__name__}.{''.join(e.args)}")
            )
        return self._handle_response(response=response, response_schema=response_schema)

    def websocket_connection(self, url: Url, path_params: dict[str, Any], on_message: Callable,
                             on_error: Callable,
                             headers: dict[str, str]) -> websocket.WebSocketApp:
        request_url = self._get_url(url, path_params=path_params)
        self._logger.debug(f"Opening websocket connection {request_url}")
        if self._logger.level <= logging.DEBUG:
            websocket.enableTrace(True)
        ws = websocket.WebSocketApp(url=request_url,
                                    on_message=on_message, on_error=on_error,
                                    header=headers)

        return ws
