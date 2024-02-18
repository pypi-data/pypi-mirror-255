import datetime
from functools import partial
from logging import Logger
from typing import Callable, Iterator

from lime_trader.clients.account_feed_client import AccountFeedClient
from lime_trader.converters.cattr_converter import CAttrConverter
from lime_trader.handlers.account_feed_handler import AccountFeedHandler
from lime_trader.models.accounts import (AccountDetails, AccountPosition, AccountTrade, AccountTransaction,
                                         AccountTransactionsPage, AccountTradesPage, Route)
from lime_trader.api.authenticated_api_client import AuthenticatedApiClient
from lime_trader.models.page import PageRequest, Page
from lime_trader.constants.urls import (ACCOUNTS_GET_ACCOUNTS_BALANCES, ACCOUNTS_GET_ACCOUNT_POSITIONS,
                                        ACCOUNTS_GET_ACCOUNT_TRADES,
                                        ACCOUNTS_GET_ACCOUNT_TRANSACTIONS, ACCOUNTS_STREAMING_FEED, ACCOUNTS_GET_ROUTES)
from lime_trader.utils.pagination import iterate_pages


class AccountClient:
    """
    Contains methods related to account data
    """

    def __init__(self, api_client: AuthenticatedApiClient, logger: Logger):
        """
        Contains methods related to account data

        Args:
            api_client: API client that will be used to execute all requests
            logger: Logger used to submit client log messages
        """
        self._api_client = api_client
        self._logger = logger

    def get_balances(self) -> list[AccountDetails]:
        """
        Gets balance information for all user accounts as a list

        Returns:
            List of all user accounts with balance information
        """
        self._logger.debug("Getting account balances")
        return self._api_client.get(url=ACCOUNTS_GET_ACCOUNTS_BALANCES, path_params={},
                                    params={}, response_schema=list[AccountDetails])

    def get_positions(self, account_number: str, date: datetime.date | None = None,
                      strategy: bool | None = None) -> list[AccountPosition]:
        """
        Gets account positions for specified date, or today if date is not supplied

        Args:
            account_number: Account number
            date: Date for account positions. If set, returns incoming positions for specified date.
                  If not specified, the method returns current intraday positions
            strategy: Optional. If `true`, returns current intraday positions grouped by multi-leg strategies.
                      Doesn't work together with `date` parameter

        Returns:
            Account positions for specified date, or current intraday positions if date is not supplied
        """
        return self._api_client.get(url=ACCOUNTS_GET_ACCOUNT_POSITIONS,
                                    path_params={"account_number": account_number},
                                    params={"date": date, "strategy": strategy},
                                    response_schema=list[AccountPosition])

    def get_trades(self, account_number: str, date: datetime.date, page: PageRequest) -> Page[AccountTrade]:
        """
        Gets the trades history on the specified account, ordered by descending timestamp.

        Args:
            account_number: Account number
            date: Date for which to get trades
            page: Pagination parameters

        Returns:
            Page of account trades for the specified date
        """
        response = self._api_client.get(url=ACCOUNTS_GET_ACCOUNT_TRADES,
                                        path_params={"account_number": account_number, "date": date},
                                        params={"limit": page.size,
                                                "skip": page.get_offset()},
                                        response_schema=AccountTradesPage)
        return Page(data=response.trades, number=page.page, size=page.size, total_elements=response.count)

    def iterate_trades(self, account_number: str, date: datetime.date,
                       start_page: PageRequest) -> Iterator[Page[AccountTransaction]]:
        for page in iterate_pages(start_page=start_page,
                                  func=partial(self.get_trades, account_number=account_number,
                                               date=date)):
            yield page

    def get_routes(self, account_number: str) -> list[Route]:
        """
        Gets a list of all routes available for specified account

        Args:
            account_number: Account number
        Returns:
            List of all routes available for specified account
        """
        return self._api_client.get(url=ACCOUNTS_GET_ROUTES,
                                    path_params={"account_number": account_number}, params={},
                                    response_schema=list[Route])

    def get_transactions_journal(self, account_number: str, start_date: datetime.date | None,
                                 end_date: datetime.date | None,
                                 page: PageRequest) -> Page[AccountTransaction]:
        """
        Gets list of transactions and a counter of total transactions in the specified time period

        Args:
            account_number: Account number
            start_date: The period start date. Optional
            end_date: The period end date. Optional, current date by default
            page: Pagination parameters

        Returns:
            Page of account transactions for specified date period
        """
        response = self._api_client.get(url=ACCOUNTS_GET_ACCOUNT_TRANSACTIONS,
                                        path_params={"account_number": account_number},
                                        params={"limit": page.size,
                                                "skip": page.get_offset(),
                                                "start_date": start_date,
                                                "end_date": end_date}, response_schema=AccountTransactionsPage)

        return Page(data=response.transactions, number=page.page, size=page.size, total_elements=response.count)

    def iterate_transactions_journal(self, account_number: str, start_page: PageRequest,
                                     start_date: datetime.date | None = None,
                                     end_date: datetime.date | None = None,
                                     ) -> Iterator[Page[AccountTransaction]]:
        for page in iterate_pages(start_page=start_page,
                                  func=partial(self.get_transactions_journal, account_number=account_number,
                                               start_date=start_date, end_date=end_date)):
            yield page

    def _start_streaming_feed(self, on_message: Callable, on_error: Callable) -> AccountFeedClient:
        websocket_app = self._api_client.websocket_connection(url=ACCOUNTS_STREAMING_FEED,
                                                              path_params={}, on_error=on_error, on_message=on_message)
        client = AccountFeedClient(websocket_app=websocket_app, logger=self._logger)
        websocket_app.on_open = client.on_account_streaming_feed_open
        websocket_app.on_close = client.on_account_streaming_feed_close
        client.start()
        return client

    def stream_account_feed(self, callback_client: AccountFeedHandler) -> AccountFeedClient:
        return self._start_streaming_feed(
            on_error=callback_client.on_account_feed_client_internal_error,
            on_message=partial(callback_client.on_message, CAttrConverter()))
