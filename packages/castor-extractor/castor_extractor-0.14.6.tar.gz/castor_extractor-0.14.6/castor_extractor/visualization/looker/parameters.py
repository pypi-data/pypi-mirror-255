from typing import NamedTuple, Optional

from ...utils import OUTPUT_DIR, from_env, validate_baseurl
from .constant import (
    BASE_URL,
    CLIENT_ID,
    CLIENT_SECRET,
    LOG_TO_STDOUT,
    SEARCH_PER_FOLDER,
)
from .env import thread_pool_size


def _valid_thread_pool_size(**kwargs):
    """
    Checks that the thread pool size is between 1 and 200 inclusive.
    https://www.googlecloudcommunity.com/gc/Technical-Tips-Tricks/Is-there-a-limit-to-the-number-of-API-requests-you-can-send-at/ta-p/592612
    """
    size = kwargs.get("thread_pool_size") or thread_pool_size()
    if not 1 <= size <= 200:
        raise ValueError("Thread pool size must be between 1 and 200 inclusive")
    return size


def _bool_env_variable(key: str) -> bool:
    parameter = from_env(key, allow_missing=True)
    return str(parameter).lower() == "true"


class Parameters(NamedTuple):
    """Parameters for Looker extraction"""

    base_url: str
    client_id: str
    client_secret: str
    is_safe_mode: bool
    log_to_stdout: bool
    output_directory: str
    search_per_folder: bool
    thread_pool_size: int
    timeout: Optional[int]


def get_parameters(**kwargs) -> Parameters:
    """
    Returns parameters for Looker extraction whether they come from script
    argument, env variable or default value.
    """
    output_directory = kwargs.get("output_directory") or from_env(OUTPUT_DIR)

    base_url = validate_baseurl(kwargs.get("base_url") or from_env(BASE_URL))
    client_id = kwargs.get("client_id") or from_env(CLIENT_ID)
    client_secret = kwargs.get("client_secret") or from_env(CLIENT_SECRET)

    thread_pool_size_ = _valid_thread_pool_size(**kwargs)

    # timeout can be set with env variable however we don't use from_env because it has a default value
    timeout = kwargs.get("timeout")

    is_safe_mode = kwargs.get("safe_mode", False)
    search_per_folder = kwargs.get("search_per_folder") or _bool_env_variable(
        SEARCH_PER_FOLDER,
    )
    log_to_stdout = kwargs.get("log_to_stdout") or _bool_env_variable(
        LOG_TO_STDOUT
    )

    return Parameters(
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret,
        is_safe_mode=is_safe_mode,
        log_to_stdout=log_to_stdout,
        output_directory=output_directory,
        search_per_folder=search_per_folder,
        thread_pool_size=thread_pool_size_,
        timeout=timeout,
    )
