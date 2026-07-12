"""In-process state shared across routers (prototype only — swap for a store in prod)."""
from app.models.schemas import RiskProfileResult

# investor_id -> most recent risk profile result
RISK_PROFILES: dict[str, RiskProfileResult] = {}
