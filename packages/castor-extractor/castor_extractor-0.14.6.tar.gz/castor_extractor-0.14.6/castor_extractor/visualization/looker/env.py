import os

from .constant import (
    DEFAULT_LOOKER_PAGE_SIZE,
    DEFAULT_LOOKER_THREAD_POOL_SIZE,
    DEFAULT_LOOKER_TIMEOUT_SECOND,
    KEY_LOOKER_PAGE_SIZE,
    KEY_LOOKER_THREAD_POOL_SIZE,
    KEY_LOOKER_TIMEOUT_SECOND,
)


def _int_env(key_env_name: str, default_value: int) -> int:
    value = os.environ.get(key_env_name, default_value)
    try:
        return int(value)
    except ValueError:
        return default_value


def page_size() -> int:
    """
    Either returns the page size parameter from env or from default value
    """
    return _int_env(
        key_env_name=KEY_LOOKER_PAGE_SIZE,
        default_value=DEFAULT_LOOKER_PAGE_SIZE,
    )


def timeout_second() -> int:
    """
    Either returns the timeout second parameter from env or from default value
    """
    return _int_env(
        key_env_name=KEY_LOOKER_TIMEOUT_SECOND,
        default_value=DEFAULT_LOOKER_TIMEOUT_SECOND,
    )


def thread_pool_size() -> int:
    """
    Either returns the thread pool size from env or from default value
    """
    return _int_env(
        key_env_name=KEY_LOOKER_THREAD_POOL_SIZE,
        default_value=DEFAULT_LOOKER_THREAD_POOL_SIZE,
    )
