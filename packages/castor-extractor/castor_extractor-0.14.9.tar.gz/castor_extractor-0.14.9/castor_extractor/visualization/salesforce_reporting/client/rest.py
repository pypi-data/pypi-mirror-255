import logging
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

import requests
from requests import Response

from ..assets import SalesforceReportingAsset
from .constants import DEFAULT_API_VERSION, DEFAULT_PAGINATION_LIMIT
from .credentials import SalesforceCredentials
from .soql import queries

logger = logging.getLogger(__name__)


class SalesforceClient:
    """
    Salesforce API client.
    https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm
    """

    api_version = DEFAULT_API_VERSION
    pagination_limit = DEFAULT_PAGINATION_LIMIT

    def __init__(
        self,
        credentials: SalesforceCredentials,
        instance_url: Optional[str] = None,
    ):
        self.credentials = credentials
        self.instance_url = instance_url
        self._token = self._access_token()

    def _access_token(self) -> Tuple[str, str]:
        url = f"{self.instance_url}/services/oauth2/token"
        response = self._call(
            url, "POST", data=self.credentials.token_request_payload()
        )
        return response["access_token"]

    def _header(self) -> Dict:
        return {"Authorization": f"Bearer {self._token}"}

    @staticmethod
    def _call(
        url: str,
        method: str = "GET",
        *,
        header: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        processor: Optional[Callable] = None,
    ) -> Any:
        logger.debug(f"Calling {method} on {url}")
        result = requests.request(
            method,
            url,
            headers=header,
            params=params,
            data=data,
        )
        result.raise_for_status()

        if processor:
            return processor(result)

        return result.json()

    @staticmethod
    def _query_processor(response: Response) -> Tuple[dict, Optional[str]]:
        results = response.json()
        return results["records"], results.get("nextRecordsUrl")

    def _query_all(self, query: str) -> Iterator[Dict]:
        """
        Run a SOQL query over salesforce API.

        more: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm
        """
        url = f"{self.instance_url}/services/data/v{self.api_version}/query"
        records, next_page = self._call(
            url,
            params={"q": query},
            processor=self._query_processor,
            header=self._header(),
        )
        yield from records

        page_count = 0
        while next_page or page_count >= self.pagination_limit:
            logger.info(f"querying page {page_count}")
            url = f"{self.instance_url}{next_page}"
            records, next_page = self._call(
                url, processor=self._query_processor, header=self._header()
            )
            yield from records
            page_count += 1

    def _fetch_folders(self) -> Iterator[Dict]:
        """
        Fetch folders.

        Notes: We need a specific way of querying the folders because
        as of today (2024/02/06) pagination is not working, after the
        second page nextPageUrl is empty while there are still data.
        """
        folders_url = f"{self.instance_url}/services/data/v43.0/folders"
        per_page = 10

        folders = self._call(
            folders_url,
            header=self._header(),
            processor=lambda x: x.json()["folders"],
        )
        yield from folders

        for page_count in range(2, DEFAULT_PAGINATION_LIMIT):
            logger.info(f"querying page {page_count} for folders")
            folders = self._call(
                f"{folders_url}?page={page_count}&pageSize={per_page}",
                header=self._header(),
                processor=lambda x: x.json()["folders"],
            )

            if not folders:
                break
            yield from folders

    def fetch(self, asset: SalesforceReportingAsset) -> List[Dict]:
        """
        Fetch Salesforce Reporting assets
        """
        logger.info(f"Starting extraction of {asset}")

        if asset == SalesforceReportingAsset.FOLDERS:
            return list(self._fetch_folders())

        return list(self._query_all(queries[asset]))
