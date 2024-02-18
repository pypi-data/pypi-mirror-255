from datetime import date, datetime, timedelta

from .client import FORMAT, _at_midnight, _is_expired

NEVER_EXPIRING_DATE = datetime.max
TODAY_DATE = _at_midnight(date.today())
EXPIRED_DATE = _at_midnight(date.today() - timedelta(days=2))


def test__is_expired():
    test_datetimes = (
        ({"time": NEVER_EXPIRING_DATE.strftime(FORMAT)}, False),
        ({"time": TODAY_DATE.strftime(FORMAT)}, False),
        ({"time": EXPIRED_DATE.strftime(FORMAT)}, True),
    )

    for test_datetime, is_expired in test_datetimes:
        assert _is_expired(test_datetime) == is_expired
