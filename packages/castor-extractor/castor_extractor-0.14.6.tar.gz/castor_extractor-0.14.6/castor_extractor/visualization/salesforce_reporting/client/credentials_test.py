from .credentials import SalesforceCredentials


def test_Credentials_token_request_payload():
    creds = SalesforceCredentials(
        username="giphy",
        password="1312",
        consumer_key="degenie",
        consumer_secret="fautpasledire",
        security_token="yo",
    )

    payload = creds.token_request_payload()

    assert payload["grant_type"] == "password"
    assert payload["username"] == "giphy"
    assert payload["client_id"] == "degenie"
    assert payload["client_secret"] == "fautpasledire"
    assert payload["password"] == "1312yo"
