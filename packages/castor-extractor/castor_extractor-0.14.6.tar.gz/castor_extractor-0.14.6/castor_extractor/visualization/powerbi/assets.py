from ...types import ExternalAsset


class PowerBiAsset(ExternalAsset):
    """PowerBi assets"""

    ACTIVITY_EVENTS = "activity_events"
    DASHBOARDS = "dashboards"
    DATASETS = "datasets"
    DATASET_FIELDS = "dataset_fields"
    METADATA = "metadata"
    REPORTS = "reports"
    TABLES = "tables"
    USERS = "users"


# Assets extracted from the Metadata file
# They are not directly fetched from the PowerBi api.
METADATA_ASSETS = (
    PowerBiAsset.DATASET_FIELDS,
    PowerBiAsset.TABLES,
    PowerBiAsset.USERS,
)
