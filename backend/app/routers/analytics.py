from fastapi import APIRouter

from app.models.schemas import Analytics
from app.services import aggregation, analytics as analytics_svc

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/analytics/{investor_id}", response_model=Analytics)
def get_analytics(investor_id: str):
    """Allocation, concentration (HHI), exposure, risk metrics, and insights."""
    portfolio = aggregation.build_portfolio(investor_id)
    return analytics_svc.compute(portfolio.holdings)
