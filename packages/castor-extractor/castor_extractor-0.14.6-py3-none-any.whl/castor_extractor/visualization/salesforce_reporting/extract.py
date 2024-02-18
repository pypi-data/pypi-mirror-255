import logging
from typing import Iterable, Optional, Tuple, Union

from ...utils import (
    OUTPUT_DIR,
    current_timestamp,
    deep_serialize,
    from_env,
    get_output_filename,
    write_json,
    write_summary,
)
from .assets import SalesforceReportingAsset
from .client import SalesforceClient, SalesforceCredentials

logger = logging.getLogger(__name__)


def iterate_all_data(
    client: SalesforceClient,
) -> Iterable[Tuple[str, Union[list, dict]]]:
    """Iterate over the extracted data from Salesforce"""

    for asset in SalesforceReportingAsset:
        logger.info(f"Extracting {asset.value.upper()} from REST API")
        data = client.fetch(asset)
        yield asset.name.lower(), deep_serialize(data)


def extract_all(
    username: str,
    password: str,
    consumer_key: str,
    consumer_secret: str,
    security_token: str,
    instance_url: str,
    output_directory: Optional[str] = None,
) -> None:
    """
    Extract data from Salesforce REST API
    Store the output files locally under the given output_directory
    """
    _output_directory = output_directory or from_env(OUTPUT_DIR)
    creds = SalesforceCredentials(
        username=username,
        password=password,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        security_token=security_token,
    )
    client = SalesforceClient(credentials=creds, instance_url=instance_url)
    ts = current_timestamp()

    for key, data in iterate_all_data(client):
        filename = get_output_filename(key, _output_directory, ts)
        write_json(filename, data)

    write_summary(_output_directory, ts)
