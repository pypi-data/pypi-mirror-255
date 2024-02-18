from datetime import datetime, timedelta
from unittest.mock import ANY, Mock, call, patch

import pytest
from requests import HTTPError

from .constants import GET, POST, Assertions, Keys, QueryParams, Urls
from .credentials import Credentials
from .rest import Client, msal

FAKE_TENANT_ID = "IamFake"
FAKE_CLIENT_ID = "MeTwo"
FAKE_SECRET = "MeThree"


def _client() -> Client:
    creds = Credentials(
        tenant_id=FAKE_TENANT_ID,
        client_id=FAKE_CLIENT_ID,
        secret=FAKE_SECRET,
    )
    return Client(creds)


def _raise_http_error() -> None:
    raise HTTPError(request=Mock(), response=Mock())


@patch.object(msal, "ConfidentialClientApplication")
def test__access_token(mock_app):
    # init mocks
    valid_response = {"access_token": "mock_token"}
    returning_valid_token = Mock(return_value=valid_response)
    mock_app.return_value.acquire_token_silent = Mock(return_value=None)
    mock_app.return_value.acquire_token_for_client = returning_valid_token

    # init client
    client = _client()

    # generated token
    assert client._access_token() == valid_response

    # via silent endpoint token
    mock_app.return_value.acquire_token_silent = returning_valid_token
    mock_app.return_value.acquire_token_for_client = None
    assert client._access_token() == valid_response

    # token missing in response
    invalid_response = {"not_access_token": "666"}
    returning_invalid_token = Mock(return_value=invalid_response)
    mock_app.return_value.acquire_token_silent = returning_invalid_token

    with pytest.raises(ValueError):
        client._access_token()


@patch.object(Client, "_access_token")
def test__headers(mock_access_token):
    client = _client()
    mock_access_token.return_value = {Keys.ACCESS_TOKEN: "666"}
    assert client._header() == {"Authorization": "Bearer 666"}


@patch("requests.request")
@patch.object(Client, "_access_token")
def test__get(mocked_access_token, mocked_request):
    client = _client()
    mocked_access_token.return_value = {Keys.ACCESS_TOKEN: "666"}
    fact = {"fact": "Approximately 24 cat skins can make a coat.", "length": 43}
    mocked_request.return_value = Mock(json=lambda: fact)

    result = client._get("https://catfact.ninja/fact")
    assert result == fact

    result = client._get("https://catfact.ninja/fact")["length"]
    assert result == 43

    mocked_request.return_value = Mock(raise_for_status=_raise_http_error)

    with pytest.raises(HTTPError):
        result = client._get("https/whatev.er")


@patch("requests.request")
@patch.object(Client, "_access_token")
def test__workspace_ids(_, mocked_request):
    client = _client()
    mocked_request.return_value = Mock(
        json=lambda: [{"id": 1000}, {"id": 1001}, {"id": 1003}],
    )
    ids = client._workspace_ids()
    assert ids == [1000, 1001, 1003]

    with pytest.raises(AssertionError, match=Assertions.DATETIME_TOO_OLD):
        good_old_time = datetime(1998, 7, 12)
        client._workspace_ids(modified_since=good_old_time)

    yesterday = datetime.today() - timedelta(1)
    ids = client._workspace_ids(modified_since=yesterday)
    params = {
        Keys.INACTIVE_WORKSPACES: True,
        Keys.PERSONAL_WORKSPACES: True,
        Keys.MODIFIED_SINCE: f"{yesterday.isoformat()}0Z",
    }

    mocked_request.assert_called_with(
        GET,
        Urls.WORKSPACE_IDS,
        data=None,
        headers=ANY,
        params=params,
    )


@patch("requests.request")
@patch.object(Client, "_access_token")
def test__post_default(_, mocked_request):
    client = _client()
    url = "https://estcequecestbientotleweekend.fr/"
    params = QueryParams.METADATA_SCAN
    data = {"bonjour": "hello"}
    client._post(url, params=params, data=data)
    mocked_request.assert_called_with(
        POST,
        url,
        headers=ANY,
        params=QueryParams.METADATA_SCAN,
        data=data,
    )


@patch("requests.request")
@patch.object(Client, "_access_token")
def test__post_with_processor(_, mocked_request):
    client = _client()
    url = "https://estcequecestbientotleweekend.fr/"
    params = QueryParams.METADATA_SCAN
    data = {"bonjour": "hello"}
    mocked_request.return_value = Mock(json=lambda: {"id": 1000})
    result = client._post(
        url,
        params=params,
        data=data,
        processor=lambda x: x.json()["id"],
    )
    assert result == 1000


@patch("requests.request")
@patch.object(Client, "_access_token")
def test__datasets(_, mocked_request):
    client = _client()
    mocked_request.return_value = Mock(
        json=lambda: {"value": [{"id": 1, "type": "dataset"}]},
    )
    datasets = client._datasets()
    mocked_request.assert_called_with(
        GET,
        Urls.DATASETS,
        data=None,
        headers=ANY,
        params=None,
    )
    assert datasets == [{"id": 1, "type": "dataset"}]


@patch("requests.request")
@patch.object(Client, "_access_token")
def test__reports(_, mocked_request):
    client = _client()
    mocked_request.return_value = Mock(
        json=lambda: {"value": [{"id": 1, "type": "report"}]},
    )
    reports = client._reports()
    mocked_request.assert_called_with(
        GET,
        Urls.REPORTS,
        data=None,
        headers=ANY,
        params=None,
    )
    assert reports == [{"id": 1, "type": "report"}]


@patch("requests.request")
@patch.object(Client, "_access_token")
def test__dashboards(_, mocked_request):
    client = _client()
    mocked_request.return_value = Mock(
        json=lambda: {"value": [{"id": 1, "type": "dashboard"}]},
    )
    dashboards = client._dashboards()
    mocked_request.assert_called_with(
        GET,
        Urls.DASHBOARD,
        data=None,
        headers=ANY,
        params=None,
    )
    assert dashboards == [{"id": 1, "type": "dashboard"}]


@patch.object(Client, "_workspace_ids")
@patch.object(Client, "_create_scan")
@patch.object(Client, "_wait_for_scan_result")
@patch.object(Client, "_get_scan")
def test__metadata(
    mocked_get_scan,
    mocked_wait,
    mocked_create_scan,
    mocked_workspace_ids,
):
    mocked_workspace_ids.return_value = list(range(200))
    mocked_create_scan.return_value = 314
    mocked_wait.return_value = True
    mocked_get_scan.return_value = [{"workspace_id": 1871}]

    client = _client()
    result = client._metadata()

    assert list(result) == [[{"workspace_id": 1871}], [{"workspace_id": 1871}]]


_CALLS = [
    {
        Keys.ACTIVITY_EVENT_ENTITIES: ["foo", "bar"],
        Keys.LAST_RESULT_SET: False,
        Keys.CONTINUATION_URI: "https://next-call-1",
    },
    {
        Keys.ACTIVITY_EVENT_ENTITIES: ["baz"],
        Keys.LAST_RESULT_SET: False,
        Keys.CONTINUATION_URI: "https://next-call-2",
    },
    {
        Keys.ACTIVITY_EVENT_ENTITIES: ["biz"],
        Keys.LAST_RESULT_SET: True,
        Keys.CONTINUATION_URI: None,
    },
]


@patch.object(Client, "_call")
def test__activity_events(mocked):
    client = _client()
    mocked.side_effect = _CALLS

    result = client._activity_events()
    assert result == ["foo", "bar", "baz", "biz"]

    expected_calls = [
        call(ANY, GET, params=None, processor=None),
        call("https://next-call-1", GET, params=None, processor=None),
        call("https://next-call-2", GET, params=None, processor=None),
    ]
    mocked.assert_has_calls(expected_calls)
