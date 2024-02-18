from typing import Set

from ...types import ExternalAsset, classproperty


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

    @classproperty
    def optional(cls) -> Set["PowerBiAsset"]:
        return {
            PowerBiAsset.DASHBOARDS,
            PowerBiAsset.DATASET_FIELDS,
            PowerBiAsset.TABLES,
            PowerBiAsset.USERS,
        }


# Assets extracted from the Metadata file
# They are not directly fetched from the PowerBi api.
METADATA_ASSETS = (
    PowerBiAsset.DATASET_FIELDS,
    PowerBiAsset.TABLES,
    PowerBiAsset.USERS,
)
