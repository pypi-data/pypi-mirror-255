from dataclasses import dataclass
from typing import Optional

_DOMO_PUBLIC_URL = "https://api.domo.com"
_AUTH_URL = (
    "grant_type=client_credentials&scope=data%20dashboard%20audit%20user"
)


@dataclass
class Endpoint:
    """Contains endpoint URL and whether the API targeted is the private one"""

    base_url: str
    is_private: bool = False

    def url(self, asset_id: Optional[str] = None):
        return f"{self.base_url}/{asset_id}" if asset_id else self.base_url


class EndpointFactory:
    """List of all Endpoints used for DOMO"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    @property
    def authentication(self) -> Endpoint:
        return Endpoint(f"{_DOMO_PUBLIC_URL}/oauth/token?{_AUTH_URL}")

    @property
    def datasets(self) -> Endpoint:
        return Endpoint(f"{_DOMO_PUBLIC_URL}/v1/datasets")

    @property
    def pages(self) -> Endpoint:
        return Endpoint(f"{_DOMO_PUBLIC_URL}/v1/pages")

    @property
    def users(self) -> Endpoint:
        return Endpoint(f"{_DOMO_PUBLIC_URL}/v1/users")

    @property
    def audit(self) -> Endpoint:
        return Endpoint(f"{_DOMO_PUBLIC_URL}/v1/audit")

    @property
    def dataflows(self) -> Endpoint:
        return Endpoint(
            base_url=f"{self.base_url}/api/dataprocessing/v1/dataflows",
            is_private=True,
        )

    def lineage(self, dataflow_id: str) -> Endpoint:
        return Endpoint(
            base_url=f"{self.base_url}/api/data/v1/lineage/DATAFLOW/{dataflow_id}",
            is_private=True,
        )

    def table_lineage(self, dataset_id: str, cloud_id: str) -> Endpoint:
        return Endpoint(
            base_url=f"{self.base_url}/api/query/v1/byos/accounts/{cloud_id}/datasets/{dataset_id}/mapping",
            is_private=True,
        )

    def page_content(self, page_id: str) -> Endpoint:
        return Endpoint(
            f"{self.base_url}/api/content/v3/stacks/{page_id}/cards?parts=datasources",
            is_private=True,
        )
