import json
import logging
import os

import urllib3.util
from dotenv import dotenv_values

from lime_trader.clients.account_client import AccountClient
from lime_trader.constants.config import DEFAULT_TIMEOUT
from lime_trader.converters.cattr_converter import CAttrConverter
from lime_trader.models.accounts import Credentials
from lime_trader.api.api_client import ApiClient
from lime_trader.api.authenticated_api_client import AuthenticatedApiClient
from lime_trader.clients.market_data_client import MarketDataClient
from lime_trader.clients.trading_client import TradingClient
from lime_trader.models.token_storage import ApiTokenStorage
from lime_trader.utils.logging_utils import get_stdout_logger


class LimeClient:
    """
    Main client that should be used for all communication with the API.

    Attributes:
        account: Account client
        market: Market client
        trading: Trading client
    """

    def __init__(self, base_url: str, credentials: Credentials, logger: logging.Logger | None = None,
                 auth_url: str | None = None, timeout: int = DEFAULT_TIMEOUT):
        """
        Args:
            base_url: Base url of the API, this will be prepended to each url
            credentials: Credentials object used for authenticating in the API
            logger: Logger to be used
            auth_url: URL of the authorization server. Only requests related to authentication/authorization
                     will use this url
            timeout: Request timeout
        """
        self._base_url = urllib3.util.parse_url(base_url)
        self._auth_url = urllib3.util.parse_url(auth_url) if auth_url is not None else self._base_url
        self._api_use_https = self._base_url.url.startswith("https://")
        self._api_use_wss = self._api_use_https
        self._auth_use_https = self._auth_url.url.startswith("https://")
        self._auth_use_wss = self._auth_use_https
        self._credentials = credentials
        self._logger = logger or get_stdout_logger()
        self._converter = CAttrConverter()
        self._api_client = ApiClient(base_url=self._base_url, converter=self._converter, use_https=self._api_use_https,
                                     use_wss=self._api_use_wss, logger=self._logger, timeout=timeout)
        self._auth_api_client = ApiClient(base_url=self._auth_url, converter=self._converter,
                                          use_https=self._auth_use_https,
                                          use_wss=self._auth_use_wss, logger=self._logger, timeout=timeout)
        self._token_storage = ApiTokenStorage(credentials=credentials, api_client=self._auth_api_client)
        self._authenticated_api_client = AuthenticatedApiClient(api_client=self._api_client,
                                                                token_storage=self._token_storage,
                                                                credentials=self._credentials, logger=self._logger)

        # instantiate clients
        self.account = AccountClient(api_client=self._authenticated_api_client, logger=self._logger)
        self.trading = TradingClient(api_client=self._authenticated_api_client, logger=self._logger)
        self.market = MarketDataClient(api_client=self._authenticated_api_client, logger=self._logger)

    @classmethod
    def from_json(cls, json_str: str, logger: logging.Logger | None = None) -> 'LimeClient':
        """
        Instantiates client from json string.

        Required JSON keys are:
            - username
            - password
            - client_id
            - client_secret
            - grant_type
            - base_url
            - auth_url

        Args:
            json_str: JSON string
            logger: Logger to use

        Returns:
            Configured LimeClient
        """
        data = json.loads(json_str)
        return cls.from_dict(data=data, logger=logger)

    @classmethod
    def from_file(cls, file_path: str, logger: logging.Logger | None = None) -> 'LimeClient':
        """
        Instantiates client from file. Contents of the file needs to be json

        Required JSON keys are:
            - username
            - password
            - client_id
            - client_secret
            - grant_type
            - base_url
            - auth_url

        Args:
            file_path: Path to the file
            logger: Logger to use

        Returns:
            Configured LimeClient
        """
        with open(file=file_path, mode="r") as f:
            content = f.read()
        return cls.from_json(json_str=content, logger=logger)

    @classmethod
    def from_dict(cls, data: dict[str, str], logger: logging.Logger | None = None) -> 'LimeClient':
        """
        Instantiates client from dictionary.
        Dictionary must have required keys:

        - username
        - password
        - client_id
        - client_secret
        - grant_type
        - base_url
        - auth_url

        Args:
            data: Dictionary with client data and credentials
            logger: Logger to use

        Returns:
            Configured LimeClient
        """
        credentials = Credentials(username=data["username"],
                                  password=data["password"],
                                  client_id=data["client_id"],
                                  client_secret=data["client_secret"],
                                  grant_type=data["grant_type"])
        client = cls(base_url=data["base_url"],
                     credentials=credentials,
                     auth_url=data["auth_url"],
                     logger=logger)
        return client

    @classmethod
    def from_env(cls, logger: logging.Logger | None = None) -> 'LimeClient':
        """
        Configures client by getting credentials and configuration from system environment.
        Required environment variables are:

        - LIME_SDK_USERNAME
        - LIME_SDK_PASSWORD
        - LIME_SDK_CLIENT_ID
        - LIME_SDK_CLIENT_SECRET
        - LIME_SDK_GRANT_TYPE
        - LIME_SDK_BASE_URL
        - LIME_SDK_AUTH_URL

        Args:
            logger: Logger to use

        Returns:
            Configured LimeClient
        """
        credentials = {
            "username": os.environ.get("LIME_SDK_USERNAME"),
            "password": os.environ.get("LIME_SDK_PASSWORD"),
            "client_id": os.environ.get("LIME_SDK_CLIENT_ID"),
            "client_secret": os.environ.get("LIME_SDK_CLIENT_SECRET"),
            "grant_type": os.environ.get("LIME_SDK_GRANT_TYPE"),
            "base_url": os.environ.get("LIME_SDK_BASE_URL"),
            "auth_url": os.environ.get("LIME_SDK_AUTH_URL"),
        }
        return cls.from_dict(credentials, logger)

    @classmethod
    def from_env_file(cls, file_path: str, logger: logging.Logger | None = None) -> 'LimeClient':
        """
        Configures client by getting credentials and configuration from key/value file, usually named `.env`.

        Required keys are:

        - LIME_SDK_USERNAME
        - LIME_SDK_PASSWORD
        - LIME_SDK_CLIENT_ID
        - LIME_SDK_CLIENT_SECRET
        - LIME_SDK_GRANT_TYPE
        - LIME_SDK_BASE_URL
        - LIME_SDK_AUTH_URL

        Args:
            file_path: File name from which to load config
            logger: Logger to use

        Returns:
            Configured LimeClient
        """
        config = dotenv_values(file_path)
        credentials = {
            "username": config.get("LIME_SDK_USERNAME"),
            "password": config.get("LIME_SDK_PASSWORD"),
            "client_id": config.get("LIME_SDK_CLIENT_ID"),
            "client_secret": config.get("LIME_SDK_CLIENT_SECRET"),
            "grant_type": config.get("LIME_SDK_GRANT_TYPE"),
            "base_url": config.get("LIME_SDK_BASE_URL"),
            "auth_url": config.get("LIME_SDK_AUTH_URL"),
        }
        return cls.from_dict(credentials, logger)
