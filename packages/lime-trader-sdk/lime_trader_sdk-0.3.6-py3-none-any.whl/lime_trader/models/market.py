import datetime
import enum
from _decimal import Decimal
from dataclasses import dataclass


class Period(enum.Enum):
    MINUTE = "minute"
    MINUTE_5 = "minute_5"
    MINUTE_15 = "minute_15"
    MINUTE_30 = "minute_30"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class TradingSchedule(enum.Enum):
    PRE_MARKET = "pre_market"
    REGULAR_MARKET = "regular_market"
    AFTER_MARKET = "after_market"
    CLOSED = "closed"


class OptionType(enum.Enum):
    CALL = "call"
    PUT = "put"


@dataclass
class Quote:
    """
    Quote for the specified symbol.

    Attributes:
        symbol: The security symbol
        ask: Ask price
        ask_size: Ask size
        bid: Bid price
        bid_size: Bid size
        last: Last price
        last_size: Last trade size
        volume: Today total volume
        date: Last trade time
        high: Today's high price
        low: Today's low price
        open: Open price
        close: Yesterday's close price
        week52_high: 52-week high
        week52_low: 52-week low
        change: Today's price change
        change_pc: Today's percent price change
        open_interest: Open interest (options)
        implied_volatility: Implied volatility (options)
        theoretical_price: Theoretical price (options)
        delta: Delta value (options)
        gamma: Gamma value (options)
        theta: Theta value (options)
        vega: Vega value (options)
    """
    symbol: str
    ask: Decimal
    ask_size: Decimal
    bid: Decimal
    bid_size: Decimal
    last: Decimal
    last_size: Decimal
    volume: int
    date: datetime.datetime
    high: Decimal
    low: Decimal
    open: Decimal
    close: Decimal
    week52_high: Decimal
    week52_low: Decimal
    change: Decimal
    change_pc: Decimal
    open_interest: Decimal
    implied_volatility: Decimal
    theoretical_price: Decimal
    delta: Decimal
    gamma: Decimal
    theta: Decimal
    vega: Decimal


@dataclass
class QuoteHistory:
    timestamp: datetime.datetime
    period: Period
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


@dataclass
class CurrentSchedule:
    """Trading session info depending on current date and time

    Attributes:
        session: Current session info
    """

    session: TradingSchedule


@dataclass
class Security:
    """Represents security

    Attributes:
        symbol: Security symbol
        description: Description of security
    """

    symbol: str
    description: str


@dataclass
class SecuritiesPage:
    """Page of securities

    Attributes:
        trades: List of securities
        count: Total count of securities
    """

    trades: list[Security]
    count: int

    @property
    def securities(self) -> list[Security]:
        """
        Alias for returned list as API returns it as "trades". Should be used instead of "trades" attribute.

        Returns:
            List of securities
        """
        return self.trades


@dataclass
class Trade:
    timestamp: int
    quantity: int
    price: Decimal
    market: str


@dataclass
class TradesPage:
    """Represents one page of trades

    Attributes:
        trades: List of trades
        count: Total count of trades
    """

    trades: list[Trade]
    count: int
