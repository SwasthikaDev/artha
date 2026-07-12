from fastapi import APIRouter

from app.models.schemas import RiskProfileRequest, RiskProfileResult, RiskQuestion
from app.services import suitability
from app.state import RISK_PROFILES

router = APIRouter(prefix="/api", tags=["risk"])


@router.get("/risk/questions", response_model=list[RiskQuestion])
def get_questions():
    """The risk-profiling questionnaire."""
    return suitability.QUESTIONS


@router.post("/risk/profile/{investor_id}", response_model=RiskProfileResult)
def submit_profile(investor_id: str, req: RiskProfileRequest):
    """Score the questionnaire, store the profile, and return the result."""
    result = suitability.score_profile(req)
    RISK_PROFILES[investor_id] = result
    return result


@router.get("/risk/profile/{investor_id}", response_model=RiskProfileResult | None)
def get_profile(investor_id: str):
    """The investor's most recent risk profile, if completed."""
    return RISK_PROFILES.get(investor_id)
