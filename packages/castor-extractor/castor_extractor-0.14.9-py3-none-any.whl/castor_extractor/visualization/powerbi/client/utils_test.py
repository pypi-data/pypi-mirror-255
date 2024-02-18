from datetime import datetime, timedelta

import pytest

from .constants import Assertions
from .utils import batch_size_is_valid_or_assert, datetime_is_recent_or_assert


def test_batch_size_is_valid_or_assert():
    valid = [1, 3, 4]
    batch_size_is_valid_or_assert(valid)

    invalid = list(range(8000))
    with pytest.raises(AssertionError, match=Assertions.BATCH_TOO_BIG):
        batch_size_is_valid_or_assert(invalid)


def test_datetime_is_recent_or_assert():
    krach = datetime(1929, 10, 29)
    with pytest.raises(AssertionError, match=Assertions.DATETIME_TOO_OLD):
        datetime_is_recent_or_assert(krach)

    yesterday = datetime.today() - timedelta(1)
    datetime_is_recent_or_assert(yesterday)
