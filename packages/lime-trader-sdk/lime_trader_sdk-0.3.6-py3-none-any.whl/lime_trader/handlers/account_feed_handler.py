import logging
from abc import abstractmethod
from logging import Logger
from typing import Any

import orjson
from websocket import WebSocketApp

from lime_trader.converters.abstract_converter import AbstractConverter
from lime_trader.models.accounts import (AccountPositions, AccountDetails, AccountTrade,
                                         AccountFeedType, AccountFeedError)
from lime_trader.models.trading import OrderDetails


class AccountFeedHandler:
    def __init__(self, logger: Logger | None = None, ):
        self._logger = logger if logger is not None else logging.getLogger()

    def on_account_feed_client_internal_error(self, websocket_app: WebSocketApp, error) -> None:
        self.on_client_error(error=error)

    def on_message(self, converter: AbstractConverter, websocket_app: WebSocketApp, message: str) -> None:
        self._logger.info("Received message on account feed")
        decoded_json = orjson.loads(message)
        message_type = decoded_json.get("t", None)
        if message_type is None:
            self._logger.error("Error decoding account feed message. Missing message type.")
            return
        decoded_type = AccountFeedType(message_type)
        decoded = decoded_json.get("data", None)
        if decoded is None:
            if decoded_type == AccountFeedType.ERROR:
                self.on_stream_error(converter.load_from_dict(decoded_json, AccountFeedError))
            else:
                self._logger.error("Error decoding account feed message. Missing message data.")
            return
        if decoded_type == AccountFeedType.TRADE:
            self.on_account_trades_execution(converter.load_from_dict(decoded, list[AccountTrade]))
        elif decoded_type == AccountFeedType.BALANCE:
            self.on_account_balances(converter.load_from_dict(decoded, list[AccountDetails]))
        elif decoded_type == AccountFeedType.ORDER:
            self.on_account_order_status_changes(converter.load_from_dict(decoded, list[OrderDetails]))
        elif decoded_type == AccountFeedType.POSITION:
            self.on_account_positions(converter.load_from_dict(decoded, list[AccountPositions]))
        else:
            raise ValueError(f"Unknown message type={message_type} for account feed!")

    def on_account_balances(self, accounts: list[AccountDetails]) -> None:
        for account in accounts:
            self.on_account_balance(account=account)

    def on_account_positions(self, account_positions: list[AccountPositions]) -> None:
        for position in account_positions:
            self.on_account_position(position=position)

    def on_account_order_status_changes(self, orders: list[OrderDetails]) -> None:
        for order in orders:
            self.on_account_order_status_change(order=order)

    def on_account_trades_execution(self, trades: list[AccountTrade]) -> None:
        for trade in trades:
            self.on_account_trade_execution(trade=trade)

    @abstractmethod
    def on_account_balance(self, account: AccountDetails) -> None:
        """
        The server sends a full list of balance for all subscribed accounts on each update of any field value.
        Since during market hours the prices keep changing the update is going to be sent on each throttling period

        Args:
            account: Account details that changed
        """
        self._logger.info(f"Balance: {account}")

    @abstractmethod
    def on_account_position(self, position: AccountPositions) -> None:
        """
        The server sends a full list of positions for all subscribed accounts on each update of any field value.
        Since during market hours the prices keep changing the update is going to be sent on each throttling period

        Args:
            position: Changed position
        """
        self._logger.info(f"Position: {position}")

    @abstractmethod
    def on_account_order_status_change(self, order: OrderDetails) -> None:
        """
        The server sends a notification when an order changes status.
        After initial connection, the server sends a list of all orders in current status on current trading day.

        Args:
            order: Updated order details
        """
        self._logger.info(f"Order: {order}")

    @abstractmethod
    def on_account_trade_execution(self, trade: AccountTrade) -> None:
        """
        The server sends a notification when a trade executes.
        After initial connection, the server sends a list of all trades on current trading day.

        Args:
            trade: Executed trade
        """
        self._logger.info(f"Trade: {trade}")

    @abstractmethod
    def on_stream_error(self, error: AccountFeedError) -> None:
        """
        Handles error returned as websocket message. This error indicates that message has been received and contains
        error message.

        Args:
            error: Decoded error
        """
        self._logger.info(f"Error: {error}")

    @abstractmethod
    def on_client_error(self, error: Any) -> None:
        """
        Handles client error, this error indicates error from client or error while decoding message.
        Message is received and cannot be decoded or there was error receiving message.

        Args:
            error: Error description
        """
        self._logger.info(f"Error: {error}")
