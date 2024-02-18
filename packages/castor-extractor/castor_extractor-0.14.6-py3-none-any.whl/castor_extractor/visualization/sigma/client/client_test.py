from unittest.mock import Mock, patch

from .client import SigmaClient, SigmaCredentials

FAKE_CREDENTIALS = SigmaCredentials(  # noqa: S106
    host="IamFake",
    client_id="MeTwo",
    api_token="MeThree",
)


def _client() -> SigmaClient:
    return SigmaClient(credentials=FAKE_CREDENTIALS)


@patch("requests.get")
@patch.object(SigmaClient, "_get_headers")
def test__get(mocked_headers, mocked_request):
    client = _client()
    mocked_headers.return_value = {"header": "MyHeader"}
    fact = {
        "fact": "Lions are the only cats that live in groups, called prides. "
        "Every female within the pride is usually related.",
        "length": 109,
    }
    mocked_request.return_value = Mock(json=lambda: fact)

    result = client._get("https://catfact.ninja/fact")
    assert result == fact

    result = client._get("https://catfact.ninja/fact")["length"]
    assert result == 109

    mocked_request.return_value = "not a json"

    result = client._get("https/whatev.er")
    assert result == {}


@patch.object(SigmaClient, "_get")
@patch.object(SigmaClient, "_get_headers")
def test__get_with_pagination(mocked_headers, mocked_request):
    client = _client()
    mocked_headers.return_value = {"header": "my_header"}
    mocked_request.return_value = {
        "nextPage": None,
        "entries": ["dataset_1", "dataset_2"],
        "total": 2,
    }

    assets = client._get_with_pagination("my_endpoint")
    assert list(assets) == ["dataset_1", "dataset_2"]

    mocked_request.assert_called_with("my_endpoint?page=0")
