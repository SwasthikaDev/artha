from fastapi import APIRouter

from app.models.schemas import Portfolio
from app.services import aggregation

router = APIRouter(prefix="/api", tags=["portfolio"])


@router.get("/investors")
def list_investors():
    """Available demo investor personas (simulated Account Aggregator accounts)."""
    return aggregation.list_investors()


@router.get("/portfolio/{investor_id}", response_model=Portfolio)
def get_portfolio(investor_id: str):
    """Consolidated, normalized portfolio across all linked brokers/depositories."""
    return aggregation.build_portfolio(investor_id)
