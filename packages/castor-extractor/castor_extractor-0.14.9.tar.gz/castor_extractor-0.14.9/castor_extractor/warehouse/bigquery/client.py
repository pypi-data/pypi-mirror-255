import logging
from typing import List, Optional, Set, Tuple

from google.api_core.exceptions import Forbidden
from google.api_core.page_iterator import Iterator as PageIterator
from google.cloud.bigquery import Client as GoogleCloudClient  # type: ignore
from google.cloud.bigquery.dataset import Dataset  # type: ignore
from google.oauth2.service_account import Credentials  # type: ignore

from ...utils import SqlalchemyClient, retry

logger = logging.getLogger(__name__)

BIGQUERY_URI = "bigquery://"

CREDENTIALS_INFO_KEY = "credentials_info"
PROJECT_ID_KEY = "project_id"

_RETRY_NUMBER = 1
_RETRY_BASE_MS = 60_000


class BigQueryClient(SqlalchemyClient):
    """Connect to BigQuery and run SQL queries"""

    def __init__(
        self,
        credentials: dict,
        db_allowed: Optional[Set[str]] = None,
        db_blocked: Optional[Set[str]] = None,
        dataset_blocked: Optional[Set[str]] = None,
    ):
        super().__init__(credentials)
        self._db_allowed = db_allowed
        self._db_blocked = db_blocked
        self._dataset_blocked = dataset_blocked
        self.client = self._client()
        self._projects: List[str] | None = None
        self._datasets: List[Dataset] | None = None

    @staticmethod
    def name() -> str:
        return "BigQuery"

    def _keep_project(self, project: str) -> bool:
        if self._db_allowed and project not in self._db_allowed:
            return False
        if self._db_blocked and project in self._db_blocked:
            return False
        return True

    def _keep_dataset(self, dataset: str) -> bool:
        if not self._dataset_blocked:
            return True

        return dataset not in self._dataset_blocked

    def _engine_options(self, credentials: dict) -> dict:
        return {
            CREDENTIALS_INFO_KEY: credentials,
        }

    def _build_uri(self, credentials: dict) -> str:
        return BIGQUERY_URI

    def _client(self) -> GoogleCloudClient:
        assert (
            CREDENTIALS_INFO_KEY in self._options
        ), "Missing BigQuery credentials in engine's options"
        credentials = self._options[CREDENTIALS_INFO_KEY]
        return GoogleCloudClient(
            project=credentials.get(PROJECT_ID_KEY),
            credentials=Credentials.from_service_account_info(credentials),
        )

    def _list_datasets(self) -> List[Dataset]:
        """
        Returns datasets available for the given GCP client
        Cache the result in self._datasets to reduce number of API calls
        """
        if self._datasets is None:
            self._datasets = [
                dataset
                for project_id in self.get_projects()
                for dataset in self.client.list_datasets(project_id)
                if self._keep_dataset(dataset.dataset_id)
            ]
        return self._datasets

    @retry(
        (Forbidden,),
        max_retries=_RETRY_NUMBER,
        base_ms=_RETRY_BASE_MS,
        log_exc_info=True,
    )
    def get_projects(self) -> List[str]:
        """
        Returns distinct project_id available for the given GCP client
        Cache the result in self._projects to reduce number of API calls.

        Note: Calling list_projects from GoogleCloudClient causes some
        ```
        google.api_core.exceptions.Forbidden: 403 GET https://bigquery.googleapis.com/bigquery/v2/projects?prettyPrint=false
        Quota exceeded: Your user exceeded quota for concurrent project.lists requests.
        ````
        In that case, task should retry automatically.
        """
        if self._projects is None:
            self._projects = [
                p.project_id
                for p in self.client.list_projects(retry=None)  # type: ignore
                if self._keep_project(p.project_id)
            ]
        return self._projects

    def get_regions(self) -> Set[Tuple[str, str]]:
        """
        Returns distinct (project_id, region) available for the given GCP client
        """
        return {
            (ds.project, ds._properties["location"])
            for ds in self._list_datasets()
        }

    def get_datasets(self) -> Set[Tuple[str, str]]:
        """
        Returns distinct (project_id, dataset_id) available for the given GCP client
        """
        return {(ds.project, ds.dataset_id) for ds in self._list_datasets()}
