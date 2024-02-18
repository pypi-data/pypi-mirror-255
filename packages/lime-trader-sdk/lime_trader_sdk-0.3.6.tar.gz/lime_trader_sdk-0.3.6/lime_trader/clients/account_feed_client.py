import threading
import time
from logging import Logger

from orjson import orjson
from websocket import WebSocketApp

from lime_trader.converters.cattr_converter import converter
from lime_trader.models.accounts import AccountFeedAction, AccountFeedActionType


class AccountFeedClient(threading.Thread):
    """
    Client used to subscribe to account feeds.
    Should not be instantiated by end-user.
    """

    def __init__(self, websocket_app: WebSocketApp, logger: Logger):
        super().__init__()
        self._websocket_app = websocket_app
        self._logger = logger
        self._available = False

    def run(self):
        self._logger.info("Starting account feed thread")
        self._websocket_app.run_forever()

    def stop(self):
        self._logger.info("Stopping account feed thread")
        self._websocket_app.close()

    def on_account_streaming_feed_open(self, web_socket_app: WebSocketApp):
        self._logger.info("Account feed client connection opened")
        self._available = True

    def on_account_streaming_feed_close(self, web_socket_app: WebSocketApp):
        self._logger.info("Account feed client connection closed")
        self._available = False

    def _send_action(self, action: AccountFeedAction):
        self._logger.info(f"Account feed - sending action {action}")
        while not self._available or not self._websocket_app.sock:
            time.sleep(1)
        self._websocket_app.send(data=orjson.dumps(converter.dump_to_dict(action)))

    def subscribe_balance(self, account_number: str) -> None:
        """
        Subscribe to balance changes for specific account

        Args:
            account_number: Account number
        """
        action = AccountFeedAction(action=AccountFeedActionType.SUBSCRIBE_BALANCE, account=account_number)
        self._send_action(action=action)

    def subscribe_positions(self, account_number: str) -> None:
        """
        Subscribe to position changes for specific account

        Args:
            account_number: Account number
        """
        action = AccountFeedAction(action=AccountFeedActionType.SUBSCRIBE_POSITIONS, account=account_number)
        self._send_action(action=action)

    def subscribe_orders(self, account_number: str) -> None:
        """
        Subscribe to order changes for specific account

        Args:
            account_number: Account number
        """
        action = AccountFeedAction(action=AccountFeedActionType.SUBSCRIBE_ORDERS, account=account_number)
        self._send_action(action=action)

    def subscribe_trades(self, account_number: str) -> None:
        """
        Subscribe to trades changes for specific account

        Args:
            account_number: Account number
        """
        action = AccountFeedAction(action=AccountFeedActionType.SUBSCRIBE_TRADES, account=account_number)
        self._send_action(action=action)

    def unsubscribe_balance(self, account_number: str) -> None:
        """
        Unsubscribe from balance changes for specific account

        Args:
            account_number: Account number
        """
        action = AccountFeedAction(action=AccountFeedActionType.UNSUBSCRIBE_BALANCE, account=account_number)
        self._send_action(action=action)

    def unsubscribe_positions(self, account_number: str) -> None:
        """
        Unsubscribe from position changes for specific account

        Args:
            account_number: Account number
        """
        action = AccountFeedAction(action=AccountFeedActionType.UNSUBSCRIBE_POSITIONS, account=account_number)
        self._send_action(action=action)

    def unsubscribe_orders(self, account_number: str) -> None:
        """
        Unsubscribe from order changes for specific account

        Args:
            account_number: Account number
        """
        action = AccountFeedAction(action=AccountFeedActionType.UNSUBSCRIBE_ORDERS, account=account_number)
        self._send_action(action=action)

    def unsubscribe_trades(self, account_number: str) -> None:
        """
        Unsubscribe from trades changes for specific account

        Args:
            account_number: Account number
        """
        action = AccountFeedAction(action=AccountFeedActionType.UNSUBSCRIBE_TRADES, account=account_number)
        self._send_action(action=action)
