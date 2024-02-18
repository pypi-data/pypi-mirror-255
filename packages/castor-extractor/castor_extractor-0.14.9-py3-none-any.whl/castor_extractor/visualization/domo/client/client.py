import logging
from datetime import date, datetime, timedelta
from typing import Iterator, List, Optional, Set, Tuple

import requests
from requests.exceptions import RequestException

from ..assets import DomoAsset
from .credentials import DomoCredentials
from .endpoints import Endpoint, EndpointFactory
from .pagination import Pagination

RawData = Iterator[dict]

DOMO_PUBLIC_URL = "https://api.domo.com"
FORMAT = "%Y-%m-%d %I:%M:%S %p"
DEFAULT_TIMEOUT = 300
TOKEN_EXPIRATION_SECONDS = timedelta(seconds=3000)  # auth token lasts 1 hour
DATASOURCES_IGNORE_ERROR_CODES = (404,)

logger = logging.getLogger(__name__)


def _at_midnight(date_: date) -> datetime:
    """convert date into datetime at midnight: 00:00:00"""
    return datetime.combine(date_, datetime.min.time())


def _handle_response(response: requests.Response) -> requests.Response:
    response.raise_for_status()
    return response


def _is_expired(last_result: dict) -> bool:
    """
    Checks if the date given is expired
    i.e. date < yesterday (00:00 AM)
    """

    last_timestamp = datetime.strptime(last_result["time"], FORMAT)
    logger.info(f"Last audit input has timestamp: {last_timestamp}")
    yesterday = date.today() - timedelta(days=1)
    threshold = _at_midnight(yesterday)
    if last_timestamp < threshold:
        return True
    return False


def _ignore_or_raise(
    error: RequestException, ignore_error_codes: Optional[Tuple[int]]
) -> dict:
    """
    Raises the error unless the response status code is in the ignored error
    codes list.
    """
    if not ignore_error_codes:
        raise error

    response = error.response
    if response is None:
        raise error

    if response.status_code in ignore_error_codes:
        return {}
    raise error


class DomoClient:
    """
    Connect to Domo API and fetch main assets.
    https://developer.domo.com/portal/8ba9aedad3679-ap-is#platform-oauth-apis
    """

    def __init__(self, credentials: DomoCredentials):
        self._authentication = credentials.authentication
        self._bearer_headers: Optional[dict] = None
        self._token_creation_time: datetime = datetime.min
        self._endpoint_factory = EndpointFactory(credentials.base_url)
        self._private_headers = credentials.private_headers
        self._timeout = DEFAULT_TIMEOUT
        self.base_url = credentials.base_url
        self.cloud_id = credentials.cloud_id

    def _token_expired(self) -> bool:
        token_lifetime = datetime.now() - self._token_creation_time
        return token_lifetime > TOKEN_EXPIRATION_SECONDS

    def _bearer_auth(self) -> dict:
        if self._bearer_headers and not self._token_expired():
            return self._bearer_headers

        logger.info("Refreshing authentication token...")

        basic_authentication = self._authentication
        endpoint = self._endpoint_factory.authentication

        response = requests.get(
            endpoint.url(),
            auth=basic_authentication,
            timeout=self._timeout,
        )
        result = _handle_response(response).json()

        bearer_token = result["access_token"]
        self._bearer_headers = {"authorization": f"Bearer {bearer_token}"}
        self._token_creation_time = datetime.now()

        return self._bearer_headers

    def _get(
        self,
        endpoint: Endpoint,
        params: Optional[dict] = None,
        asset_id: Optional[str] = None,
    ) -> requests.Response:
        params = params if params else {}
        is_private = endpoint.is_private
        headers = self._private_headers if is_private else self._bearer_auth()
        response = requests.get(
            url=endpoint.url(asset_id),
            headers=headers,
            params=params,
            timeout=self._timeout,
        )
        return _handle_response(response)

    def _get_element(
        self,
        endpoint: Endpoint,
        params: Optional[dict] = None,
        asset_id: Optional[str] = None,
        ignore_error_codes: Optional[Tuple[int]] = None,
    ) -> dict:
        """Used when the response only contains one element"""
        try:
            return self._get(endpoint, params, asset_id).json()
        except requests.exceptions.RequestException as error:
            return _ignore_or_raise(error, ignore_error_codes)

    def _get_many(
        self,
        endpoint: Endpoint,
        params: Optional[dict] = None,
        asset_id: Optional[str] = None,
    ) -> List[dict]:
        """Used when the response contains multiple elements"""
        return self._get(endpoint, params, asset_id).json()

    def _get_paginated(self, endpoint: Endpoint) -> List[dict]:
        """Used when the response is paginated and need iterations"""
        pagination = Pagination()
        all_results: List[dict] = []
        while pagination.needs_increment:
            results = self._get_many(
                endpoint=endpoint,
                params={
                    "offset": pagination.offset,
                    "limit": pagination.per_page,
                },
            )
            all_results.extend(results)
            number_of_items = len(results)
            pagination.increment_offset(number_of_items)

            if endpoint == self._endpoint_factory.audit:
                last_result = results[-1]
                # We decided to fetch audits until the audit is prior to a particular date
                # defined in _is_expired function. To be more precise, we could have instead use
                # params start and end of the audit endpoint (timestamp in milliseconds).
                # https://developer.domo.com/portal/a4e18ca6a0c0b-retrieve-activity-log-entries
                # But we need then to manage properly the timezone conversion of the results
                # which adds more complexity than benefits
                if _is_expired(last_result):
                    pagination.should_stop = True
        return all_results

    def _datasources(self, page_id: str) -> RawData:
        endpoint = self._endpoint_factory.page_content(page_id)
        page_content = self._get_element(
            endpoint, ignore_error_codes=DATASOURCES_IGNORE_ERROR_CODES
        )
        if not page_content:
            logging.info(f"No datasource found for page id {page_id}")
            return
        processed: set[str] = set()
        for card in page_content["cards"]:
            for datasource in card["datasources"]:
                id_ = datasource["dataSourceId"]
                if id_ in processed:
                    continue
                yield {
                    "id": id_,
                    "name": datasource["dataSourceName"],
                    "type": datasource["dataType"],
                }
                processed.add(id_)

    def _process_pages(
        self,
        page_tree: List[dict],
        parent_path: str = "/root",
    ) -> Iterator[dict]:
        """Recursively fetch pages while building the folder architecture"""
        if not page_tree:
            return []

        for page in page_tree:
            page_id = page.get("id")
            page_name = page.get("name")
            if not (page_id and page_name):
                logger.debug(f"This page has no id nor name: {page}")
                continue

            page_children = page.get("children", list)

            detail = self._get_element(
                self._endpoint_factory.pages,
                asset_id=page_id,
            )
            datasources = self._datasources(page_id)
            yield {
                **detail,
                "datasources": list(datasources),
                "path": parent_path,
                "base_url": self.base_url,
            }
            yield from self._process_pages(
                page_tree=page_children,
                parent_path=f"{parent_path}/{page_name}",
            )

    def _link_table_to_dataset(self, dataset: dict, dataset_id: str) -> dict:
        if not self.cloud_id:
            return dataset

        lineage_endpoint = self._endpoint_factory.table_lineage(
            dataset_id=dataset_id,
            cloud_id=self.cloud_id,
        )
        dataset_table_lineage = self._get_element(lineage_endpoint)

        return {**dataset, **dataset_table_lineage}

    def _pages(self) -> RawData:
        page_hierarchy = self._get_paginated(self._endpoint_factory.pages)
        yield from self._process_pages(page_hierarchy)

    def _datasets(self) -> RawData:
        dataset_list = self._get_paginated(self._endpoint_factory.datasets)

        for dataset in dataset_list:
            dataset_id = dataset.get("id")
            if not dataset_id:
                continue

            dataset_detail = self._get_element(
                endpoint=self._endpoint_factory.datasets,
                asset_id=dataset_id,
            )

            yield {
                **self._link_table_to_dataset(
                    dataset=dataset_detail,
                    dataset_id=dataset_id,
                ),
                "base_url": self.base_url,
            }

    def _unique_datasets(self) -> RawData:
        ids_encountered: Set[str] = set()
        for dataset in self._datasets():
            dataset_id = dataset["id"]
            if dataset_id in ids_encountered:
                continue
            ids_encountered.add(dataset_id)
            yield dataset

    def _users(self) -> RawData:
        user_list = self._get_paginated(self._endpoint_factory.users)
        for user in user_list:
            user_id = user.get("id")
            if not user_id:
                continue
            yield self._get_element(
                endpoint=self._endpoint_factory.users,
                asset_id=user_id,
            )

    def _audit(self) -> RawData:
        yield from self._get_paginated(self._endpoint_factory.audit)

    def _dataflows(self) -> RawData:
        dataflows = self._get_many(self._endpoint_factory.dataflows)
        for dataflow in dataflows:
            dataflow_id = dataflow.get("id")
            if not dataflow_id:
                continue
            yield self._get_element(self._endpoint_factory.lineage(dataflow_id))

    def fetch(self, asset: DomoAsset) -> RawData:
        """Returns the needed metadata for the queried asset"""
        if asset == DomoAsset.PAGES:
            yield from self._pages()

        elif asset == DomoAsset.DATASETS:
            yield from self._unique_datasets()

        elif asset == DomoAsset.USERS:
            yield from self._users()

        elif asset == DomoAsset.AUDIT:
            yield from self._audit()

        elif asset == DomoAsset.DATAFLOWS:
            yield from self._dataflows()

        else:
            raise ValueError(f"This asset {asset} is unknown")
