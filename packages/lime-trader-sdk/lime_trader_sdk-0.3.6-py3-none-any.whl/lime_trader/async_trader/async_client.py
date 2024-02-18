import logging

from lime_trader.async_trader.clients.async_account_client import AsyncAccountClient
from lime_trader.async_trader.clients.async_market_data_client import AsyncMarketDataClient
from lime_trader.async_trader.clients.async_trading_client import AsyncTradingClient
from lime_trader.constants.config import DEFAULT_TIMEOUT
from lime_trader.converters.cattr_converter import CAttrConverter

from lime_trader import LimeClient
from lime_trader.async_trader.api.async_api_client import AsyncApiClient
from lime_trader.async_trader.api.async_authenticated_api_client import AsyncAuthenticatedApiClient
from lime_trader.models.accounts import Credentials
from lime_trader.models.token_storage import AsyncApiTokenStorage


class AsyncLimeClient(LimeClient):
    def __init__(self, base_url: str, credentials: Credentials, logger: logging.Logger, auth_url: str = None,
                 timeout: int = DEFAULT_TIMEOUT):
        super().__init__(base_url=base_url, credentials=credentials, logger=logger, auth_url=auth_url)
        self._converter = CAttrConverter()
        self._api_client = AsyncApiClient(base_url=self._base_url, converter=self._converter,
                                          use_https=self._api_use_https,
                                          use_wss=self._api_use_wss, logger=self._logger, timeout=timeout)
        self._auth_api_client = AsyncApiClient(base_url=self._auth_url, converter=self._converter,
                                               use_https=self._auth_use_https,
                                               use_wss=self._auth_use_wss, logger=self._logger, timeout=timeout)
        self._token_storage = AsyncApiTokenStorage(credentials=credentials, api_client=self._auth_api_client)
        self._authenticated_api_client = AsyncAuthenticatedApiClient(api_client=self._api_client,
                                                                     token_storage=self._token_storage,
                                                                     credentials=self._credentials, logger=self._logger)

        # instantiate clients
        self.account = AsyncAccountClient(api_client=self._authenticated_api_client, logger=self._logger)
        self.trading = AsyncTradingClient(api_client=self._authenticated_api_client, logger=self._logger)
        self.market = AsyncMarketDataClient(api_client=self._authenticated_api_client, logger=self._logger)
