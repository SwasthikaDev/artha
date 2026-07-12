from fastapi import APIRouter, HTTPException

from app.data import alt_assets as catalog
from app.models.schemas import AltAssetView
from app.services import suitability
from app.state import RISK_PROFILES

router = APIRouter(prefix="/api", tags=["alt-assets"])


@router.get("/alt-assets/{investor_id}", response_model=list[AltAssetView])
def list_alt_assets(investor_id: str):
    """Alt-asset catalog, each tagged with suitability for this investor's risk profile."""
    profile = RISK_PROFILES.get(investor_id)
    return [suitability.tag_suitability(a, profile) for a in catalog.get_catalog()]


@router.get("/alt-assets/{investor_id}/{asset_id}", response_model=AltAssetView)
def get_alt_asset(investor_id: str, asset_id: str):
    """A single alt-asset with education content and suitability verdict."""
    asset = catalog.get_asset(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return suitability.tag_suitability(asset, RISK_PROFILES.get(investor_id))
