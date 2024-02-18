from _decimal import Decimal
from logging import Logger

from lime_trader.api.authenticated_api_client import AuthenticatedApiClient

from lime_trader.clients.trading_client import TradingClient
from lime_trader.models.accounts import TradeSide
from lime_trader.models.trading import (Order, PlaceOrderResponse, ValidateOrderResponse, CancelOrderResponse,
                                       OrderFee, OrderDetails)
from lime_trader.constants.urls import (TRADING_GET_ACTIVE_ORDERS, TRADING_PLACE_ORDER, TRADING_VALIDATE_ORDER,
                                        TRADING_GET_ORDER_DETAILS,
                                        TRADING_CANCEL_ORDER, TRADING_ESTIMATE_FEE_CHARGES)


class AsyncTradingClient(TradingClient):

    def __init__(self, api_client: AuthenticatedApiClient, logger: Logger):
        super().__init__(api_client=api_client, logger=logger)

    async def place_order(self, order: Order) -> PlaceOrderResponse:
        return await self._api_client.post(url=TRADING_PLACE_ORDER,
                                           path_params={},
                                           json=order,
                                           response_schema=PlaceOrderResponse)

    async def validate_order(self, order: Order) -> ValidateOrderResponse:
        return await self._api_client.post(url=TRADING_VALIDATE_ORDER,
                                           path_params={},
                                           json=order,
                                           response_schema=ValidateOrderResponse)

    async def get_order_details(self, order_id: str) -> OrderDetails:
        return await self._api_client.get(url=TRADING_GET_ORDER_DETAILS,
                                          path_params={"id": order_id}, params={},
                                          response_schema=OrderDetails)

    async def cancel_order(self, order_id: str, message: str | None) -> CancelOrderResponse:
        return await self._api_client.post(url=TRADING_CANCEL_ORDER,
                                           path_params={"id": order_id},
                                           json={"message": message},
                                           response_schema=CancelOrderResponse)

    async def get_active_orders(self, account_number: str) -> list[OrderDetails]:
        return await self._api_client.get(url=TRADING_GET_ACTIVE_ORDERS,
                                          path_params={"account_number": account_number},
                                          params={},
                                          response_schema=list[OrderDetails])

    async def estimate_fee_charges(self, account_number: str, symbol: str, quantity: Decimal, side: TradeSide,
                                   price: Decimal) -> list[OrderFee]:
        return await self._api_client.post(url=TRADING_ESTIMATE_FEE_CHARGES, path_params={}, json={
            "account_number": account_number,
            "symbol": symbol,
            "quantity": quantity,
            "side": side,
            "price": price
        }, response_schema=list[OrderFee])
