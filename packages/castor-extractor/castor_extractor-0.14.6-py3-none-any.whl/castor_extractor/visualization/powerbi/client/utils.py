from datetime import datetime, timedelta
from typing import List

from .constants import RECENT_DAYS, Assertions, Batches


def batch_size_is_valid_or_assert(ids: List) -> None:
    """
    assert that current batch is smaller than expected size
    """
    assert len(ids) <= Batches.METADATA, Assertions.BATCH_TOO_BIG


def datetime_is_recent_or_assert(dt: datetime) -> None:
    """
    assert that given datetime is recent
    """
    valid = dt > datetime.utcnow() - timedelta(RECENT_DAYS)
    assert valid, Assertions.DATETIME_TOO_OLD
