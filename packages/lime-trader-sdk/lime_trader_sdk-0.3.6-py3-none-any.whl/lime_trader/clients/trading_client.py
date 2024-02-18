from _decimal import Decimal
from logging import Logger

from lime_trader.api.authenticated_api_client import AuthenticatedApiClient
from lime_trader.exceptions.api_error import ApiError
from lime_trader.models.accounts import TradeSide
from lime_trader.models.errors import Error
from lime_trader.models.trading import (Order, PlaceOrderResponse, ValidateOrderResponse, CancelOrderResponse,
                                        OrderFee, OrderDetails)
from lime_trader.constants.urls import (TRADING_GET_ACTIVE_ORDERS, TRADING_PLACE_ORDER, TRADING_VALIDATE_ORDER,
                                        TRADING_GET_ORDER_DETAILS,
                                        TRADING_CANCEL_ORDER, TRADING_ESTIMATE_FEE_CHARGES)


class TradingClient:
    """
    Contains methods related to trading
    """

    def __init__(self, api_client: AuthenticatedApiClient, logger: Logger):
        """
        Contains methods related to trading

        Args:
            api_client: API client that will be used to execute all requests
            logger: Logger used to submit client log messages
        """
        self._api_client = api_client
        self._logger = logger

    def place_order(self, order: Order) -> PlaceOrderResponse:
        """
        Places an order. The order is accepted immediately, the method returns assigned id.
        The order is still validated with exactly same logic as in validate
        method and is sent to market on successful validation pass.
        Otherwise, the order will reject asynchronously, and you can query its status by calling the details' endpoint.

        Args:
            order: Order to place

        Returns:
            Order placing response with indicator of success and placed order id
        """
        return self._api_client.post(url=TRADING_PLACE_ORDER, json=order,
                                     path_params={},
                                     response_schema=PlaceOrderResponse)

    def validate_order(self, order: Order) -> ValidateOrderResponse:
        """
        Verifies an order and responds with the validation message if the order can not be placed at the moment.
        The order is not sent to market.

        Args:
            order: Order for verification

        Returns:
            Validation response
        """
        return self._api_client.post(url=TRADING_VALIDATE_ORDER, json=order,
                                     path_params={},
                                     response_schema=ValidateOrderResponse)

    def get_order_details(self, order_id: str) -> OrderDetails:
        """
        Get the order details by the specified order id

        Args:
            order_id: Order id

        Returns:
            Order details
        """
        return self._api_client.get(url=TRADING_GET_ORDER_DETAILS,
                                    path_params={"id": order_id}, params={},
                                    response_schema=OrderDetails)

    def cancel_order(self, order_id: str, message: str | None) -> CancelOrderResponse:
        """
        Cancels specified order

        Args:
            order_id: Order id
            message: Optional cancellation details

        Returns:
            Cancellation result with indicator of success
        """
        return self._api_client.post(url=TRADING_CANCEL_ORDER, path_params={"id": order_id}, json={"message": message},
                                     response_schema=CancelOrderResponse)

    def get_active_orders(self, account_number: str) -> list[OrderDetails]:
        """
        Get list of active orders for the account

        Args:
            account_number: Account number

        Returns:
            List of active orders
        """
        return self._api_client.get(url=TRADING_GET_ACTIVE_ORDERS, path_params={"account_number": account_number},
                                    params={},
                                    response_schema=list[OrderDetails])

    def estimate_fee_charges(self, account_number: str, symbol: str, quantity: Decimal, side: TradeSide,
                             price: Decimal) -> list[OrderFee]:
        """
        Gets estimated fees for specified order parameters, breaking down all charges by type

        Args:
            account_number: Account number
            symbol: Stock or an option
            quantity: Order quantity
            side: Order side
            price: Order price

        Returns:
            Estimated fees for specified order parameters by type
        """
        return self._api_client.post(url=TRADING_ESTIMATE_FEE_CHARGES, path_params={}, json={
            "account_number": account_number,
            "symbol": symbol,
            "quantity": quantity,
            "side": side,
            "price": price
        }, response_schema=list[OrderFee])

    def validate_and_place_order(self, order: Order) -> PlaceOrderResponse:
        validation_result = self.validate_order(order=order)
        if validation_result.is_valid:
            return self.place_order(order=order)
        raise ApiError(Error(code="validation", message=validation_result.validation_message,
                             status_code=None))
