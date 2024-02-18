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
from .assets import SigmaAsset
from .client import SigmaClient, SigmaCredentials
from .constants import API_TOKEN, CLIENT_ID, HOST

logger = logging.getLogger(__name__)


def iterate_all_data(
    client: SigmaClient,
) -> Iterable[Tuple[SigmaAsset, Union[list, Iterator, dict]]]:
    """Iterate over the extracted data from Sigma"""

    logger.info("Extracting DATASETS from API")
    datasets = client.fetch(SigmaAsset.DATASETS)
    yield SigmaAsset.DATASETS, list(deep_serialize(datasets))

    logger.info("Extracting WORKBOOKS from API")
    workbooks = list(client.fetch(SigmaAsset.WORKBOOKS))
    yield SigmaAsset.WORKBOOKS, list(deep_serialize(workbooks))

    logger.info("Extracting FILES from API")
    files = client.fetch(SigmaAsset.FILES)
    yield SigmaAsset.FILES, list(deep_serialize(files))

    logger.info("Extracting MEMBERS from API")
    members = client.fetch(SigmaAsset.MEMBERS)
    yield SigmaAsset.MEMBERS, list(deep_serialize(members))

    logging.info("Extracting QUERIES data from API")
    queries = client.fetch(SigmaAsset.QUERIES, workbooks=workbooks)
    yield SigmaAsset.QUERIES, list(deep_serialize(queries))

    logging.info("Extracting ELEMENTS data from API")
    elements = list(client.fetch(SigmaAsset.ELEMENTS, workbooks=workbooks))
    yield SigmaAsset.ELEMENTS, list(deep_serialize(elements))

    logging.info("Extracting LINEAGES data from API")
    lineages = client.fetch(SigmaAsset.LINEAGES, elements=elements)
    yield SigmaAsset.LINEAGES, list(deep_serialize(lineages))


def extract_all(
    host: Optional[str] = None,
    client_id: Optional[str] = None,
    api_token: Optional[str] = None,
    output_directory: Optional[str] = None,
) -> None:
    """
    Extract data from Sigma API
    Store the output files locally under the given output_directory
    """

    _output_directory = output_directory or from_env(OUTPUT_DIR)
    _client_id = client_id or from_env(CLIENT_ID)
    _host = host or from_env(HOST)
    _api_token = api_token or from_env(API_TOKEN)

    credentials = SigmaCredentials(
        host=_host,
        client_id=_client_id,
        api_token=_api_token,
    )
    client = SigmaClient(credentials=credentials)

    ts = current_timestamp()

    for key, data in iterate_all_data(client):
        filename = get_output_filename(key.name.lower(), _output_directory, ts)
        write_json(filename, data)

    write_summary(_output_directory, ts, host=_host)
