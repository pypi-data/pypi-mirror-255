from datetime import date, datetime, timedelta, timezone


def current_datetime() -> datetime:
    """Returns the current datetime"""
    return datetime.utcnow()


def current_date() -> date:
    """Returns the current datetime"""
    return current_datetime().date()


def current_timestamp() -> int:
    """
    Returns the current timestamp from epoch (rounded to the nearest second)
    """
    return int(datetime.timestamp(current_datetime()))


def _set_uct_timezone(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts


def now(tz: bool = False) -> datetime:
    """
    provide current time
    optionally localize timezone
    """
    ts = datetime.utcnow()
    return _set_uct_timezone(ts) if tz else ts


def past_date(past_days: int) -> date:
    """returns a date in the past"""
    return now().date() - timedelta(past_days)


def at_midnight(date_: date) -> datetime:
    """convert date into datetime at midnight: 00:00:00"""
    return datetime.combine(date_, datetime.min.time())
