from datetime import date, datetime, timedelta
from unittest.mock import patch

import pytest
import requests

from .client import (
    FORMAT,
    DomoClient,
    DomoCredentials,
    _at_midnight,
    _is_expired,
)
from .endpoints import EndpointFactory

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


class FakeResponse:
    """
    Helper class to fake few requests Response capabilities in the test below
    """

    def __init__(self, content: dict, status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def json(self) -> dict:
        return self.content


@patch.object(DomoClient, "_get")
def test_client___get_element_with_error_status(mock_get):
    # init
    creds = DomoCredentials("bim", "bam", "boom", "lol")
    client = DomoClient(creds)
    any_endpoint = EndpointFactory("truc").datasets

    # case no error
    content = {"happy": "path"}
    mock_get.return_value = FakeResponse(content=content)
    assert client._get_element(any_endpoint) == content

    # case error not ignored, no response -> raised
    error = requests.exceptions.ConnectionError
    mock_get.side_effect = error
    with pytest.raises(error):
        client._get_element(any_endpoint)

    # case error not ignored, with response -> raised
    error = requests.exceptions.ConnectionError
    status_code = 403
    response = FakeResponse(content={}, status_code=status_code)
    mock_get.side_effect = error(response=response)
    with pytest.raises(error):
        client._get_element(any_endpoint)

    # case error is ignored -> not raised
    element = client._get_element(
        any_endpoint, ignore_error_codes=(status_code,)
    )
    assert element == dict()

    # case another error ignored -> raised
    with pytest.raises(error):
        another_status_code = status_code + 4
        client._get_element(
            any_endpoint, ignore_error_codes=(another_status_code,)
        )
