import logging

from ..abstract import (
    CATALOG_ASSETS,
    EXTERNAL_LINEAGE_ASSETS,
    QUERIES_ASSETS,
    VIEWS_ASSETS,
    SupportedAssets,
    WarehouseAsset,
    WarehouseAssetGroup,
)

logger = logging.getLogger(__name__)

SYNAPSE_ASSETS: SupportedAssets = {
    WarehouseAssetGroup.CATALOG: CATALOG_ASSETS,
    WarehouseAssetGroup.QUERY: QUERIES_ASSETS,
    WarehouseAssetGroup.VIEW_DDL: VIEWS_ASSETS,
    WarehouseAssetGroup.ROLE: (WarehouseAsset.USER,),
    WarehouseAssetGroup.EXTERNAL_LINEAGE: EXTERNAL_LINEAGE_ASSETS,
}
