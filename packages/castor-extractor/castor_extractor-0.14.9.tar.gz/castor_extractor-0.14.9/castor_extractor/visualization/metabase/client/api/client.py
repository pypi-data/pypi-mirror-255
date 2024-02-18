import logging
from typing import Dict, Iterator, List, cast

import requests
from requests import HTTPError, Response

from .....utils import JsonType, SerializedAsset
from ...assets import EXPORTED_FIELDS, MetabaseAsset
from ...errors import MetabaseLoginError, SuperuserCredentialsRequired
from ...types import IdsType
from ..shared import DETAILS_KEY, get_dbname_from_details
from .credentials import CredentialsApi, CredentialsApiKey, get_value

logger = logging.getLogger(__name__)

URL_TEMPLATE = "{base_url}/api/{endpoint}"

ROOT_KEY = "root"
CARDS_KEY = "dashcards"
CARDS_KEY_DEPRECATED = "ordered_cards"  # prior to v0.48 of Metabase
DATA_KEY = "data"


class ApiClient:
    """
    Connect to Metabase API and fetch main assets.
    Superuser credentials are required.
    https://www.metabase.com/docs/latest/api-documentation.html
    """

    def __init__(
        self,
        **kwargs,
    ):
        self._credentials = CredentialsApi(
            base_url=get_value(CredentialsApiKey.BASE_URL, kwargs),
            user=get_value(CredentialsApiKey.USER, kwargs),
            password=get_value(CredentialsApiKey.PASSWORD, kwargs),
        )
        self._session = requests.Session()
        self._session_id = self._login()
        self._check_permissions()  # verify that the given user is superuser

    @staticmethod
    def name() -> str:
        """return the name of the client"""
        return "Metabase/API"

    def base_url(self) -> str:
        """Return base_url from credentials"""
        return self._credentials.base_url

    def _url(self, endpoint: str) -> str:
        return URL_TEMPLATE.format(
            base_url=self._credentials.base_url,
            endpoint=endpoint,
        )

    def _headers(self) -> dict:
        return {
            "X-Metabase-Session": self._session_id,
            "Content-type": "application/x-www-form-urlencoded",
        }

    @staticmethod
    def _answer(response: Response):
        answer = response.json()
        if isinstance(answer, Dict) and DATA_KEY in answer:
            # v0.41 of Metabase introduced embedded data for certain calls
            # {'data': [{ }, ...] , 'total': 15, 'limit': None, 'offset': None}"
            return answer[DATA_KEY]
        return answer

    def _call(self, endpoint: str) -> JsonType:
        url = self._url(endpoint)
        headers = self._headers()
        response = self._session.get(url=url, headers=headers)
        response.raise_for_status()  # check for errors
        return self._answer(response)

    def _check_permissions(self) -> None:
        try:
            # This endpoint requires superuser credentials
            self._call("collection/graph")
        except HTTPError as err:
            if err.response.status_code == 403:  # forbidden
                raise SuperuserCredentialsRequired(
                    credentials_info=self._credentials.to_dict(hide=True),
                    error_details=err.args,
                )
            raise

    def _login(self) -> str:
        url = self._url("session")
        payload = {
            "username": self._credentials.user,
            "password": self._credentials.password,
        }
        response = self._session.post(url, json=payload)
        logger.info(f"Getting session_id: {response.json()}")

        if not response.json().get("id"):
            raise MetabaseLoginError(
                credentials_info=self._credentials.to_dict(hide=True),
                error_details=response.json(),
            )

        return response.json()["id"]

    def _fetch_ids(self, asset: MetabaseAsset) -> IdsType:
        ids: IdsType = []
        results = self._call(endpoint=asset.name.lower())
        for res in cast(List, results):
            assert isinstance(res, dict)
            ids.append(res["id"])
        return ids

    def _fetch_details(self, asset: MetabaseAsset) -> SerializedAsset:
        """Fetches list of IDS first, then iterate on api/asset/:id to fetch details"""
        result: SerializedAsset = []
        for id_ in self._fetch_ids(asset):
            details = self._call(endpoint=f"{asset.name.lower()}/{id_}")
            result.append(cast(Dict, details))
        return result

    @staticmethod
    def _collection_specifics(collections: SerializedAsset) -> SerializedAsset:
        # remove the root folder
        def _is_not_root(collection: dict) -> bool:
            return collection.get("id") != ROOT_KEY

        return list(filter(_is_not_root, collections))

    @staticmethod
    def _database_specifics(databases: SerializedAsset) -> SerializedAsset:
        for db in databases:
            # superuser privileges are mandatory, this field should be present
            assert DETAILS_KEY in db
            details = db[DETAILS_KEY]
            db["dbname"] = get_dbname_from_details(details)

        return databases

    @staticmethod
    def _dashboard_cards(dashboards: SerializedAsset) -> Iterator[Dict]:
        for d in dashboards:
            d_cards = d.get(CARDS_KEY) or d.get(CARDS_KEY_DEPRECATED) or []
            yield from d_cards

    def fetch(self, asset: MetabaseAsset) -> SerializedAsset:
        """fetches the given asset"""
        if asset == MetabaseAsset.DASHBOARD_CARDS:
            dashboards = self._fetch_details(MetabaseAsset.DASHBOARD)
            assets = list(self._dashboard_cards(dashboards))
        else:
            answer = self._call(asset.name.lower())
            assets = cast(List, answer)

        if asset == MetabaseAsset.DATABASE:
            assets = self._database_specifics(assets)

        if asset == MetabaseAsset.COLLECTION:
            assets = self._collection_specifics(assets)

        logger.info(f"Fetching {asset.name} ({len(assets)} results)")

        # keep interesting fields
        return [
            {key: e.get(key) for key in EXPORTED_FIELDS[asset]} for e in assets
        ]
