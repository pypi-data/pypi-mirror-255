from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple

from requests.auth import HTTPBasicAuth


class CredentialsKey(Enum):
    """Value enum object for the credentials"""

    API_TOKEN = "api_token"  # noqa: S105
    BASE_URL = "base_url"
    CLIENT_ID = "client_id"
    CLOUD_ID = "cloud_id"
    DEVELOPER_TOKEN = "developer_token"  # noqa: S105


CLIENT_ALLOWED_KEYS: Tuple[str, ...] = tuple(c.value for c in CredentialsKey)


@dataclass
class DomoCredentials:
    """Class to handle Domo rest API permissions"""

    api_token: str
    base_url: str
    client_id: str
    developer_token: str
    cloud_id: Optional[str] = None

    @classmethod
    def from_secret(cls, secret: dict) -> "DomoCredentials":
        credentials = {
            k: v for k, v in secret.items() if k in CLIENT_ALLOWED_KEYS
        }
        return cls(**credentials)

    @property
    def authentication(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.client_id, self.api_token)

    @property
    def private_headers(self) -> Dict[str, str]:
        return {"X-DOMO-Developer-Token": self.developer_token}
