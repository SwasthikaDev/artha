from fastapi import APIRouter

from app.models.schemas import AdvisorRequest, AdvisorResponse
from app.services import advisor as advisor_svc
from app.services import aggregation, analytics as analytics_svc

router = APIRouter(prefix="/api", tags=["advisor"])


@router.post("/advisor", response_model=AdvisorResponse)
def ask_advisor(req: AdvisorRequest):
    """Natural-language Q&A grounded on the investor's real portfolio + analytics."""
    portfolio = aggregation.build_portfolio(req.investor_id)
    analytics = analytics_svc.compute(portfolio.holdings)
    return advisor_svc.answer(req.message, portfolio, analytics, req.history)
