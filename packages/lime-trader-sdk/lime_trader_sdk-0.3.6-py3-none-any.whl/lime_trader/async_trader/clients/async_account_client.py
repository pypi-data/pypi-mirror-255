import datetime
from functools import partial
from logging import Logger
from typing import Callable, AsyncIterator

from lime_trader.clients.account_client import AccountClient
from lime_trader.clients.account_feed_client import AccountFeedClient
from lime_trader.models.accounts import (AccountDetails, AccountPosition, AccountTrade, AccountTransaction,
                                         AccountTransactionsPage, AccountTradesPage, Route)
from lime_trader.api.authenticated_api_client import AuthenticatedApiClient
from lime_trader.models.page import PageRequest, Page
from lime_trader.constants.urls import (ACCOUNTS_GET_ACCOUNTS_BALANCES, ACCOUNTS_GET_ACCOUNT_POSITIONS,
                                        ACCOUNTS_GET_ACCOUNT_TRADES,
                                        ACCOUNTS_GET_ACCOUNT_TRANSACTIONS, ACCOUNTS_STREAMING_FEED, ACCOUNTS_GET_ROUTES)
from lime_trader.utils.pagination import iterate_pages_async


class AsyncAccountClient(AccountClient):

    def __init__(self, api_client: AuthenticatedApiClient, logger: Logger):
        super().__init__(api_client=api_client, logger=logger)

    async def get_balances(self) -> list[AccountDetails]:
        return await self._api_client.get(url=ACCOUNTS_GET_ACCOUNTS_BALANCES,
                                          path_params={}, params={},
                                          response_schema=list[AccountDetails])

    async def get_positions(self, account_number: str, date: datetime.date | None = None,
                            strategy: bool | None = None) -> list[AccountPosition]:
        return await self._api_client.get(url=ACCOUNTS_GET_ACCOUNT_POSITIONS,
                                          path_params={"account_number": account_number},
                                          params={"date": date, "strategy": strategy},
                                          response_schema=list[AccountPosition])

    async def get_trades(self, account_number: str, date: datetime.date, page: PageRequest) -> Page[AccountTrade]:
        response = await self._api_client.get(url=ACCOUNTS_GET_ACCOUNT_TRADES,
                                              path_params={"account_number": account_number,
                                                           "date": date},
                                              params={"limit": str(page.size),
                                                      "skip": str(page.get_offset())},
                                              response_schema=AccountTradesPage)
        return Page(data=response.trades, number=page.page, size=page.size, total_elements=response.count)

    async def get_routes(self, account_number: str) -> list[Route]:
        return await self._api_client.get(url=ACCOUNTS_GET_ROUTES,
                                          path_params={"account_number": account_number}, params={},
                                          response_schema=list[Route])

    async def get_transactions_journal(self, account_number: str, start_date: datetime.date | None,
                                       end_date: datetime.date | None,
                                       page: PageRequest) -> Page[AccountTransaction]:
        response = await self._api_client.get(
            url=ACCOUNTS_GET_ACCOUNT_TRANSACTIONS,
            path_params={"account_number": account_number},
            params={"limit": page.size,
                    "skip": page.get_offset(),
                    "start_date": start_date,
                    "end_date": end_date}, response_schema=AccountTransactionsPage)

        return Page(data=response.transactions, number=page.page, size=page.size, total_elements=response.count)

    async def start_streaming_feed(self, on_message: Callable, on_error: Callable) -> AccountFeedClient:
        websocket_app = await self._api_client.websocket_connection(url=ACCOUNTS_STREAMING_FEED,
                                                                    path_params={}, on_error=on_error,
                                                                    on_message=on_message)
        client = AccountFeedClient(websocket_app=websocket_app, logger=self._logger)
        websocket_app.on_open = client.on_account_streaming_feed_open
        websocket_app.on_close = client.on_account_streaming_feed_close
        client.start()
        return client

    async def iterate_transactions_journal(self, account_number: str, start_page: PageRequest,
                                           start_date: datetime.date | None = None,
                                           end_date: datetime.date | None = None,
                                           ) -> AsyncIterator[Page[AccountTransaction]]:
        async for page in iterate_pages_async(start_page=start_page,
                                              func=partial(self.get_transactions_journal,
                                                           account_number=account_number,
                                                           start_date=start_date, end_date=end_date)):
            yield page
