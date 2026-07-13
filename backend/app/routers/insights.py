"""Routers for the advanced 'winning' features: X-Ray, Health Score, and awareness."""
from fastapi import APIRouter, HTTPException

from app.data import alt_assets as catalog
from app.models.schemas import HealthScore, Nudge, QuizQuestion, XRay
from app.services import (
    aggregation,
    analytics as analytics_svc,
    awareness,
    health,
    xray,
)
from app.state import RISK_PROFILES

router = APIRouter(prefix="/api", tags=["insights"])


@router.get("/xray/{investor_id}", response_model=XRay)
def get_xray(investor_id: str):
    """Look-through analysis: reveal TRUE concentration hidden inside funds/ETFs."""
    portfolio = aggregation.build_portfolio(investor_id)
    return xray.compute(portfolio.holdings)


@router.get("/health-score/{investor_id}", response_model=HealthScore)
def get_health_score(investor_id: str):
    """A–F portfolio health grade + investor-protection alerts."""
    portfolio = aggregation.build_portfolio(investor_id)
    analytics = analytics_svc.compute(portfolio.holdings)
    xr = xray.compute(portfolio.holdings)
    profile = RISK_PROFILES.get(investor_id)
    return health.compute(portfolio, analytics, xr, profile)


@router.get("/nudges/{investor_id}", response_model=list[Nudge])
def get_nudges(investor_id: str):
    """Suitability-driven nudges that surface gaps in the portfolio."""
    portfolio = aggregation.build_portfolio(investor_id)
    analytics = analytics_svc.compute(portfolio.holdings)
    profile = RISK_PROFILES.get(investor_id)
    return awareness.nudges(portfolio, analytics, profile)


@router.get("/quiz/{asset_id}", response_model=QuizQuestion)
def get_quiz(asset_id: str):
    """A comprehension quiz question for an alternate asset."""
    q = awareness.quiz_for(asset_id)
    if q is None:
        raise HTTPException(status_code=404, detail="No quiz for this asset")
    return q
