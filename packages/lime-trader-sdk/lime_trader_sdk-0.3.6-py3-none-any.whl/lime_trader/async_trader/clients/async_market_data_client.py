import datetime
from logging import Logger

from lime_trader.async_trader.api.async_authenticated_api_client import AsyncAuthenticatedApiClient
from lime_trader.clients.market_data_client import MarketDataClient
from lime_trader.models.market import (Quote, QuoteHistory, Period, Security, SecuritiesPage, Trade, TradesPage,
                                       CurrentSchedule)
from lime_trader.models.page import Page, PageRequest
from lime_trader.constants.urls import (MARKET_DATA_GET_CURRENT_QUOTE, MARKET_DATA_GET_QUOTES,
                                        MARKET_DATA_GET_TRADING_SCHEDULE,
                                        MARKET_DATA_LOOKUP_SECURITIES, MARKET_DATA_GET_TIME_AND_SALES,
                                        MARKET_DATA_GET_QUOTES_HISTORY)


class AsyncMarketDataClient(MarketDataClient):

    def __init__(self, api_client: AsyncAuthenticatedApiClient, logger: Logger):
        super().__init__(api_client=api_client, logger=logger)

    async def get_current_quote(self, symbol: str) -> Quote:
        return await self._api_client.get(MARKET_DATA_GET_CURRENT_QUOTE, path_params={},
                                          params={"symbol": symbol},
                                          response_schema=Quote)

    async def get_current_quotes(self, symbols: list[str]) -> list[Quote]:
        return await self._api_client.post(MARKET_DATA_GET_QUOTES, path_params={}, json=symbols,
                                           response_schema=list[Quote])

    async def get_quotes_history(self, symbol: str, period: Period, from_date: datetime.datetime,
                                 to_date: datetime.datetime) -> list[QuoteHistory]:
        return await self._api_client.get(MARKET_DATA_GET_QUOTES_HISTORY, path_params={},
                                          params={"symbol": symbol,
                                                  "period": period.value,
                                                  "from": from_date,
                                                  "to": to_date
                                                  }, response_schema=list[QuoteHistory])

    async def get_trading_schedule(self) -> CurrentSchedule:
        return await self._api_client.get(MARKET_DATA_GET_TRADING_SCHEDULE, path_params={}, params={},
                                          response_schema=CurrentSchedule)

    async def lookup_securities(self, query: str, page: PageRequest) -> Page[Security]:
        response = await self._api_client.get(MARKET_DATA_LOOKUP_SECURITIES, path_params={},
                                              params={"query": query,
                                                      "limit": page.size,
                                                      "skip": page.get_offset()},
                                              response_schema=SecuritiesPage)
        return Page(data=response.securities, number=page.page, size=page.size, total_elements=response.count)

    async def time_and_sales(self, symbol: str, from_date: datetime.datetime,
                             to_date: datetime.datetime, page: PageRequest) -> Page[Trade]:
        response = await self._api_client.get(MARKET_DATA_GET_TIME_AND_SALES, path_params={},
                                              params={"symbol": symbol,
                                                      "limit": page.size,
                                                      "skip": page.get_offset()},
                                              response_schema=TradesPage)
        return Page(data=response.trades, number=page.page, size=page.size, total_elements=response.count)
