import logging
from typing import Iterable, Iterator, Optional, Tuple, Union

from ...utils import (
    OUTPUT_DIR,
    current_timestamp,
    deep_serialize,
    from_env,
    get_output_filename,
    write_json,
    write_summary,
)
from .assets import DomoAsset
from .client import DomoClient, DomoCredentials
from .constants import API_TOKEN, BASE_URL, CLIENT_ID, CLOUD_ID, DEVELOPER_TOKEN

logger = logging.getLogger(__name__)


def iterate_all_data(
    client: DomoClient,
) -> Iterable[Tuple[DomoAsset, Union[list, Iterator, dict]]]:
    """Iterate over the extracted data from Domo"""

    logger.info("Extracting PAGES from API")
    pages = client.fetch(DomoAsset.PAGES)
    yield DomoAsset.PAGES, list(deep_serialize(pages))

    logger.info("Extracting DATASETS from API")
    datasets = list(client.fetch(DomoAsset.DATASETS))
    yield DomoAsset.DATASETS, list(deep_serialize(datasets))

    logger.info("Extracting USERS from API")
    users = client.fetch(DomoAsset.USERS)
    yield DomoAsset.USERS, list(deep_serialize(users))

    logger.info("Extracting AUDIT from API")
    audit = client.fetch(DomoAsset.AUDIT)
    yield DomoAsset.AUDIT, list(deep_serialize(audit))

    logging.info("Extracting DATAFLOWS data from API")
    dataflows = client.fetch(DomoAsset.DATAFLOWS)
    yield DomoAsset.DATAFLOWS, list(deep_serialize(dataflows))


def extract_all(
    api_token: Optional[str] = None,
    base_url: Optional[str] = None,
    client_id: Optional[str] = None,
    cloud_id: Optional[str] = None,
    developer_token: Optional[str] = None,
    output_directory: Optional[str] = None,
) -> None:
    """
    Extract data from Domo API
    Store the output files locally under the given output_directory
    """

    _output_directory = output_directory or from_env(OUTPUT_DIR)
    _client_id = client_id or from_env(CLIENT_ID)
    _base_url = base_url or from_env(BASE_URL)
    _api_token = api_token or from_env(API_TOKEN)
    _developer_token = developer_token or from_env(DEVELOPER_TOKEN)
    _cloud_id = cloud_id or from_env(CLOUD_ID)

    credentials = DomoCredentials(
        base_url=_base_url,
        client_id=_client_id,
        api_token=_api_token,
        developer_token=_developer_token,
        cloud_id=_cloud_id,
    )
    client = DomoClient(credentials=credentials)

    ts = current_timestamp()

    for key, data in iterate_all_data(client):
        filename = get_output_filename(key.name.lower(), _output_directory, ts)
        write_json(filename, data)

    write_summary(_output_directory, ts, base_url=_base_url)
