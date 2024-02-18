from .constants import Urls
from .credentials import Credentials


def test_credentials():
    tenant_id = "any_tenant_id"
    client_id = "any_client_id"
    secret = "🤫"

    # no scopes provided
    credentials = Credentials(
        tenant_id=tenant_id,
        client_id=client_id,
        secret=secret,
    )
    assert credentials.scopes == [Urls.DEFAULT_SCOPE]

    # empty scopes
    credentials = Credentials(
        tenant_id=tenant_id,
        client_id=client_id,
        secret=secret,
        scopes=[],
    )
    assert credentials.scopes == []

    # with scopes
    scopes = ["foo"]
    credentials = Credentials(
        tenant_id=tenant_id,
        client_id=client_id,
        secret=secret,
        scopes=scopes,
    )
    assert credentials.scopes == scopes
