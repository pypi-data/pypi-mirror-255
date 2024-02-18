import datetime

DEFAULT_DATE_FORMAT = "%Y-%m-%d"


def date_to_str(date: datetime.date) -> str:
    """
    Converts date to string using specified format

    Args:
        date: Date to convert

    Returns:
        String representation of date in default format
    """
    return date.strftime(DEFAULT_DATE_FORMAT)


def str_to_date(date: str) -> datetime.date:
    """
    Converts string from default date format to date object

    Args:
        date: Date in string representation

    Returns:
        Date object
    """
    return datetime.datetime.strptime(date, DEFAULT_DATE_FORMAT).date()


def datetime_to_timestamp(date: datetime.datetime) -> int:
    """
    Converts datetime to unix timestamp

    Args:
        date: Datetime to convert

    Returns:
        Unix timestamp
    """
    return int(date.timestamp())


def timestamp_to_datetime(timestamp: int) -> datetime.datetime:
    """
    Converts unix timestamp to datetime object

    Args:
        timestamp: Unix timestamp

    Returns:
        Datetime object
    """
    if timestamp > 9999999999:
        # handle microseconds, this method will work properly till year 2899.
        timestamp = timestamp / 1000
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
