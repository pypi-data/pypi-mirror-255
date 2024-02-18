from urllib3.util import Url

HTTP_SCHEMA = "http"
WS_SCHEMA = "ws"

AUTHENTICATION_GET_TOKEN = Url(scheme=HTTP_SCHEMA, path="/connect/token")
AUTHENTICATION_AUTHORIZE = Url(scheme=HTTP_SCHEMA, path="/connect/authorize")

ACCOUNTS_GET_ACCOUNTS_BALANCES = Url(scheme=HTTP_SCHEMA, path="/accounts")
ACCOUNTS_STREAMING_FEED = Url(scheme=WS_SCHEMA, path="/accounts")
ACCOUNTS_GET_ACCOUNT_POSITIONS = Url(scheme=HTTP_SCHEMA, path="/accounts/{account_number}/positions")
ACCOUNTS_GET_ACCOUNT_TRADES = Url(scheme=HTTP_SCHEMA, path="/accounts/{account_number}/trades/{date}")
ACCOUNTS_GET_ROUTES = Url(scheme=HTTP_SCHEMA, path="/accounts/{account_number}/routes")
ACCOUNTS_GET_ACCOUNT_TRANSACTIONS = Url(scheme=HTTP_SCHEMA, path="/accounts/{account_number}/transactions")

TRADING_PLACE_ORDER = Url(scheme=HTTP_SCHEMA, path="/orders/place")
TRADING_VALIDATE_ORDER = Url(scheme=HTTP_SCHEMA, path="/orders/validate")
TRADING_GET_ORDER_DETAILS = Url(scheme=HTTP_SCHEMA, path="/orders/{id}")
TRADING_GET_ACTIVE_ORDERS = Url(scheme=HTTP_SCHEMA, path="/accounts/{account_number}/activeorders")
TRADING_CANCEL_ORDER = Url(scheme=HTTP_SCHEMA, path="/orders/{id}/cancel")
TRADING_ESTIMATE_FEE_CHARGES = Url(scheme=HTTP_SCHEMA, path="/pricing/fees")

MARKET_DATA_GET_CURRENT_QUOTE = Url(scheme=HTTP_SCHEMA, path="/marketdata/quote")
MARKET_DATA_GET_QUOTES = Url(scheme=HTTP_SCHEMA, path="/marketdata/quotes")
MARKET_DATA_GET_QUOTES_HISTORY = Url(scheme=HTTP_SCHEMA, path="/marketdata/history")
MARKET_DATA_GET_TRADING_SCHEDULE = Url(scheme=HTTP_SCHEMA, path="/marketdata/schedule")
MARKET_DATA_LOOKUP_SECURITIES = Url(scheme=HTTP_SCHEMA, path="/securities")
MARKET_DATA_GET_TIME_AND_SALES = Url(scheme=HTTP_SCHEMA, path="/marketdata/trades")
