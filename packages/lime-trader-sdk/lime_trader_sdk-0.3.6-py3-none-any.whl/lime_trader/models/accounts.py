from datetime import date, datetime, timedelta, timezone
import enum
from _decimal import Decimal
from functools import partial

from dataclasses import field, dataclass

from lime_trader.models.trading import TimeInForce, OrderType


class MarginType(enum.Enum):
    CASH = "cash"
    MARGIN_X1 = "marginx1"
    MARGIN_X2 = "marginx2"
    DAY_TRADER = "daytrader"


class RestrictionLevel(enum.Enum):
    NONE = "none"
    RESTRICTED = "restricted"
    DISABLED = "disabled"
    CLOSED = "closed"


class SecurityType(enum.Enum):
    COMMON_STOCK = "common_stock"
    PREFERRED_STOCK = "preferred_stock"
    OPTION = "option"
    STRATEGY = "strategy"


class TradeSide(enum.Enum):
    BUY = "buy"
    SELL = "sell"


class AccountFeedActionType(enum.Enum):
    SUBSCRIBE_BALANCE = "subscribeBalance"
    SUBSCRIBE_POSITIONS = "subscribePositions"
    SUBSCRIBE_ORDERS = "subscribeOrders"
    SUBSCRIBE_TRADES = "subscribeTrades"

    UNSUBSCRIBE_BALANCE = "unsubscribeBalance"
    UNSUBSCRIBE_POSITIONS = "unsubscribePositions"
    UNSUBSCRIBE_ORDERS = "unsubscribeOrders"
    UNSUBSCRIBE_TRADES = "unsubscribeTrades"


class AccountFeedType(enum.Enum):
    POSITION = "p"
    BALANCE = "b"
    ORDER = "o"
    TRADE = "t"
    ERROR = "e"


@dataclass(frozen=True)
class AccountDetails:
    """Represents account details and balances

    Attributes:
        account_number: Account number
        trade_platform: Trading platform this account is traded on
        margin_type: Margin type
        restriction: Restriction level effective on the account
        daytrades_count: Day trades counter
        account_value_total: Total account liquidation value
        cash: Account debit balance when negative, credit balance when positive
        day_trading_buying_power: Day trading buying power for marginable securities
        margin_buying_power: Buying power for marginable securities
        non_margin_buying_power: Buying power for non-marginable securities
        position_market_value: Sum of all positions current market values. The value is negative for short positions
        unsettled_cash: Unsettled cash for cash accounts
        cash_to_withdraw: Cash available to withdraw from the account
        restriction_reason: Optional description explaining why the account is restricted
    """

    account_number: str
    trade_platform: str
    margin_type: MarginType
    restriction: RestrictionLevel
    daytrades_count: int
    account_value_total: Decimal
    cash: Decimal
    day_trading_buying_power: Decimal
    margin_buying_power: Decimal
    non_margin_buying_power: Decimal

    position_market_value: Decimal

    unsettled_cash: Decimal
    cash_to_withdraw: Decimal
    restriction_reason: str | None = None


@dataclass(frozen=True)
class Leg:
    """Represents leg in the multi-leg strategy

    Attributes:
        symbol: The leg security symbol
        quantity: Signed number of shares or option contracts for the leg
        average_open_price: The leg cost basis
        current_price: The leg current price
        security_type: The leg asset type
    """
    symbol: str
    average_open_price: Decimal
    current_price: Decimal
    quantity: int
    security_type: SecurityType


@dataclass(frozen=True)
class AccountPosition:
    """Represents single account position

    Attributes:
        symbol: Security symbol
        quantity: Signed number of shares or option contracts. Negative for short positions
        average_open_price: Average historical cost basis
        current_price: Current price
        security_type: Asset type
        legs: Legs of the multi-leg strategy
    """

    symbol: str
    quantity: int
    average_open_price: Decimal
    current_price: Decimal
    security_type: SecurityType
    legs: list[Leg] | None = None


@dataclass(frozen=True)
class AccountPositions:
    """List of account positions

    Attributes:
        account: Account number
        positions: Account positions
    """

    account: str
    positions: list[AccountPosition]


@dataclass(frozen=True)
class AccountTrade:
    """Represents single account trade

    Attributes:
        symbol: Security symbol
        timestamp: Timestamp of the trade
        quantity: Number of shares or option contracts, negative for sells, positive for buys
        price: Trade price
        amount: Trade amount, which is the quantity multiplied by the lot size and price
        side: Trade side
    """

    symbol: str
    timestamp: datetime
    quantity: int
    price: Decimal
    amount: Decimal
    side: TradeSide


@dataclass(frozen=True)
class AccountTradesPage:
    """Page of account trades

    Attributes:
        trades: List of trades in page
        count: Total count of trades
    """
    trades: list[AccountTrade]
    count: int


@dataclass(frozen=True)
class Route:
    """Route available for account

    Attributes:
        exchange: Route name to use when placing order
        time_in_force: List of order duration instructions supported by a route
        order_type: List of order types supported by a route
    """
    exchange: str
    time_in_force: list[TimeInForce]
    order_type: list[OrderType]


@dataclass(frozen=True)
class TransactionCash:
    """Describes the cash side of the transaction

    Attributes:
        gross_amount: Dollar amount not including fees, can be positive or negative
        net_amount: Net dollar amount including fees charged for the transaction, can be positive or negative
    """

    gross_amount: Decimal
    net_amount: Decimal


@dataclass(frozen=True)
class TransactionAsset:
    """Describes the asset side of the transaction

    Attributes:
        symbol: Asset symbol
        symbol_description: Company name for stocks or human-readable name for options
        quantity: Transaction quantity, can be positive or negative
        price: Price for each unit
    """

    symbol: str
    symbol_description: str
    quantity: int
    price: Decimal


@dataclass(frozen=True)
class TransactionFee:
    """Represents transaction fee

    Attributes:
        name: Name of the fee.
        amount: Fee amount
    """

    name: str
    amount: Decimal


@dataclass(frozen=True)
class AccountTransaction:
    """Single account transaction

    Attributes:
        id: Internal transaction id, globally unique, and it is not necessarily sequentially incremented
        type: Transaction type
        description: Human-readable transaction description
        date: Date of transaction
        cash: Describes the cash side of the transaction
        fees: List of fees charged by the transaction
        asset: Structure describing the asset side of the transaction
    """

    id: str
    type: str
    description: str
    date: date
    cash: TransactionCash
    fees: list[TransactionFee]
    asset: TransactionAsset | None = None


@dataclass(frozen=True)
class AccountTransactionsPage:
    """Page of account transactions

    Attributes:
        transactions: List of transactions in page
        count: Total count of transactions
    """

    transactions: list[AccountTransaction]
    count: int


@dataclass(frozen=True)
class Token:
    """Represents access token

    Attributes:
        scope: The scopes this token grants access to
        token_type: Bearer means that access token should be put to the Authorization header of every web request
        access_token: Access token
        expires_in: Expiration lifetime in seconds
        date_created: Date when token was created. Used to determine expiry date
    """

    scope: str
    token_type: str
    access_token: str
    expires_in: int
    date_created: datetime = field(default_factory=partial(datetime.now, tz=timezone.utc))

    def expiry_date(self, tz: timezone = timezone.utc) -> datetime:
        """
        Returns expiry date in a specific timezone

        Args:
            tz: Timezone in which to return expiry date. Default is UTC

        Returns:
            Datetime when token expires
        """
        return self.date_created.astimezone(tz) + timedelta(seconds=self.expires_in)

    def expires_in_delta(self) -> timedelta:
        """
        Gets difference between expiry date and current date

        Returns:
            Difference between expiry date and current date
        """
        return self.expiry_date() - datetime.now(tz=timezone.utc)


@dataclass(frozen=True)
class Credentials:
    """Credentials used for API authentication

    Attributes:
        username: Username
        password: Password
        client_id: Client id issued to the service
        client_secret: Client secret issued to the service
        grant_type: OAuth authorization flow to use
    """
    username: str
    password: str
    client_id: str
    client_secret: str
    grant_type: str


@dataclass(frozen=True)
class AccountFeedAction:
    """Action that is sent to account feed websocket

    Attributes:
        action: Type of action
        account: Account number

    """
    action: AccountFeedActionType
    account: str


@dataclass(frozen=True)
class AccountFeedError:
    """Error during streaming account data

    Attributes:
        t: Type of account feed, always "e"
        code: Error code
        description: Error description
    """

    t: AccountFeedType
    code: str
    description: str
