import logging
from typing import Dict, Iterator, List, Optional, Tuple
from urllib.parse import urljoin

import requests

from ..assets import SigmaAsset
from .credentials import CredentialsKey, SigmaCredentials
from .endpoints import EndpointFactory
from .pagination import Pagination

logger = logging.getLogger()


DATA_ELEMENTS: Tuple[str, str] = ("table", "visualization")


class SigmaClient:
    """Client used for all Sigma's assets extractions"""

    def __init__(self, credentials: SigmaCredentials):
        self.host = credentials.host
        self.client_id = credentials.client_id
        self.api_token = credentials.api_token
        self.headers: Optional[Dict[str, str]] = None

    def _get_token(self, token_api_path: str) -> Dict[str, str]:
        token_response = requests.post(  # noqa: S113
            token_api_path,
            data={
                CredentialsKey.GRANT_TYPE.value: "client_credentials",
                CredentialsKey.CLIENT_ID.value: self.client_id,
                CredentialsKey.CLIENT_SECRET.value: self.api_token,
            },
        )
        if token_response.status_code != 200:
            raise ValueError("Couldn't fetch the token in the API")
        return token_response.json()

    def _get_headers(self) -> Dict[str, str]:
        if not self.headers:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            auth_endpoint = EndpointFactory.authentication()
            token_api_path = urljoin(self.host, auth_endpoint)

            token = self._get_token(token_api_path)
            headers["Authorization"] = f"Bearer {token['access_token']}"
            self.headers = headers

        return self.headers

    def _get(self, endpoint_url: str) -> dict:
        url = urljoin(self.host, endpoint_url)
        result = requests.get(url, headers=self._get_headers())  # noqa: S113
        try:
            return result.json()
        except:
            logger.debug(result)
            return dict()

    def _get_with_pagination(self, endpoint_url: str) -> Iterator[dict]:
        pagination = Pagination(next_page="0")

        while pagination.next_page is not None:
            paginated_url = pagination.generate_url(endpoint_url)
            response = self._get(paginated_url)
            pagination = Pagination(
                next_page=response.get("nextPage"),
                entries=response.get("entries"),
                total=response.get("total"),
            )
            yield from pagination.entries

    def _per_workbook_get_pages(self, workbook_id: str) -> Iterator[dict]:
        endpoint = EndpointFactory.pages(workbook_id)
        yield from self._get_with_pagination(endpoint)

    def _per_page_get_elements(
        self,
        workbook_id: str,
        page_id: str,
    ) -> Iterator[dict]:
        endpoint = EndpointFactory.elements(workbook_id, page_id)
        yield from self._get_with_pagination(endpoint)

    def _get_all_datasets(self) -> Iterator[dict]:
        endpoint = EndpointFactory.datasets()
        yield from self._get_with_pagination(endpoint)

    def _get_all_files(self) -> Iterator[dict]:
        endpoint = EndpointFactory.files()
        yield from self._get_with_pagination(endpoint)

    def _get_all_members(self) -> Iterator[dict]:
        endpoint = EndpointFactory.members()
        yield from self._get(endpoint)

    def _get_all_workbooks(self) -> Iterator[dict]:
        endpoint = EndpointFactory.workbooks()
        yield from self._get_with_pagination(endpoint)

    def _get_all_elements(self, workbooks: List[dict]) -> Iterator[dict]:
        for workbook in workbooks:
            workbook_id = workbook["workbookId"]
            pages = self._per_workbook_get_pages(workbook_id)

            for page in pages:
                page_id = page["pageId"]
                elements = self._per_page_get_elements(workbook_id, page_id)
                for element in elements:
                    if element.get("type") not in DATA_ELEMENTS:
                        continue
                    yield {
                        **element,
                        "workbook_id": workbook_id,
                        "page_id": page_id,
                    }

    def _get_all_lineages(self, elements: List[dict]) -> Iterator[dict]:
        for element in elements:
            workbook_id = element["workbook_id"]
            element_id = element["elementId"]
            endpoint = EndpointFactory.lineage(workbook_id, element_id)
            lineage = self._get(endpoint)
            yield {
                **lineage,
                "workbook_id": workbook_id,
                "element_id": element_id,
            }

    def _get_all_queries(self, workbooks: List[dict]) -> Iterator[dict]:
        for workbook in workbooks:
            workbook_id = workbook["workbookId"]
            endpoint = EndpointFactory.queries(workbook_id)
            queries = self._get_with_pagination(endpoint)
            for query in queries:
                yield {**query, "workbook_id": workbook_id}

    def fetch(
        self,
        asset: SigmaAsset,
        workbooks: Optional[List[dict]] = None,
        elements: Optional[List[dict]] = None,
    ) -> Iterator[dict]:
        """Returns the needed metadata for the queried asset"""
        if asset == SigmaAsset.DATASETS:
            yield from self._get_all_datasets()

        elif asset == SigmaAsset.ELEMENTS:
            if not workbooks:
                raise ValueError("Missing workbooks to extract elements")

            yield from self._get_all_elements(workbooks)

        elif asset == SigmaAsset.FILES:
            yield from self._get_all_files()

        elif asset == SigmaAsset.LINEAGES:
            if not elements:
                raise ValueError("Missing elements to extract lineage")
            yield from self._get_all_lineages(elements)

        elif asset == SigmaAsset.MEMBERS:
            yield from self._get_all_members()

        elif asset == SigmaAsset.QUERIES:
            if not workbooks:
                raise ValueError("Missing workbooks to extract queries")

            yield from self._get_all_queries(workbooks)

        elif asset == SigmaAsset.WORKBOOKS:
            yield from self._get_all_workbooks()

        else:
            raise ValueError(f"This asset {asset} is unknown")
