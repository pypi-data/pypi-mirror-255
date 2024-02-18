import decimal
import logging
import sys
from typing import Any

from orjson import orjson

DEFAULT_SENSITIVE_FIELDS = ("password", "client_secret", "access_token")
SENSITIVE_VALUE_REPLACEMENT = "<sensitive>"


def default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError


def log_json_data(data: dict[str, Any] | list[Any]):
    """
    Dumps dictionary or list data to json string. Values for sensitive field names are replaced with fixed value

    Args:
        data: Data to dump

    Returns:
        String representation of data if data is dictionary. If data is list returns list of string representation
    """
    if type(data) == list:
        first_element = data[0] if len(data) > 0 else None
        if first_element is None:
            return []
        if type(first_element) in (int, bool, float, str):
            return data
        return [
            _log_single_item(item) for item in data
        ]
    return _log_single_item(data)


def _log_single_item(data: dict[str, Any]) -> str:
    return orjson.dumps(
        {k: v if k not in DEFAULT_SENSITIVE_FIELDS else SENSITIVE_VALUE_REPLACEMENT for k, v in data.items()},
        option=orjson.OPT_INDENT_2, default=default).decode()


def get_stdout_logger(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("lime_trader")
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(level=level)
    return logger
