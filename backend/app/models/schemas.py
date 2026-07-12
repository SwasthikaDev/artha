"""Pydantic schemas — the canonical data contracts shared across services and the API.

These mirror the typed interfaces consumed by the React frontend.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #
class AssetClass(str, Enum):
    EQUITY = "Equity"
    MUTUAL_FUND = "Mutual Fund"
    ETF = "ETF"
    BOND = "Bond"
    REIT = "REIT"
    INVIT = "InvIT"
    GOLD = "Gold"
    CASH = "Cash"


class Depository(str, Enum):
    NSDL = "NSDL"
    CDSL = "CDSL"


class RiskCategory(str, Enum):
    CONSERVATIVE = "Conservative"
    MODERATE = "Moderate"
    BALANCED = "Balanced"
    GROWTH = "Growth"
    AGGRESSIVE = "Aggressive"


class Suitability(str, Enum):
    SUITABLE = "Suitable"
    CAUTION = "Caution"
    UNSUITABLE = "Unsuitable"


# --------------------------------------------------------------------------- #
# Holdings & portfolio
# --------------------------------------------------------------------------- #
class Holding(BaseModel):
    """A single normalized position, post-aggregation across brokers/depositories."""
    symbol: str
    name: str
    asset_class: AssetClass
    sector: str = "Diversified"
    broker: str
    depository: Depository
    quantity: float
    avg_cost: float = Field(..., description="Average buy price per unit (INR)")
    ltp: float = Field(..., description="Last traded / current price per unit (INR)")

    @property
    def invested(self) -> float:
        return self.quantity * self.avg_cost

    @property
    def current_value(self) -> float:
        return self.quantity * self.ltp

    @property
    def pnl(self) -> float:
        return self.current_value - self.invested

    @property
    def pnl_pct(self) -> float:
        return (self.pnl / self.invested * 100) if self.invested else 0.0


class HoldingView(BaseModel):
    """Holding enriched with computed value/P&L fields for the API response."""
    symbol: str
    name: str
    asset_class: AssetClass
    sector: str
    broker: str
    depository: Depository
    quantity: float
    avg_cost: float
    ltp: float
    invested: float
    current_value: float
    pnl: float
    pnl_pct: float


class AccountSummary(BaseModel):
    broker: str
    depository: Depository
    holdings_count: int
    current_value: float


class PortfolioSummary(BaseModel):
    investor_id: str
    investor_name: str
    total_invested: float
    total_current_value: float
    total_pnl: float
    total_pnl_pct: float
    day_change: float
    day_change_pct: float
    holdings_count: int
    accounts: list[AccountSummary]


class Portfolio(BaseModel):
    investor_id: str
    investor_name: str
    summary: PortfolioSummary
    holdings: list[HoldingView]


# --------------------------------------------------------------------------- #
# Analytics
# --------------------------------------------------------------------------- #
class AllocationSlice(BaseModel):
    label: str
    value: float
    pct: float


class ConcentrationItem(BaseModel):
    label: str
    pct: float
    flag: bool = Field(False, description="True if this exceeds a prudent concentration threshold")


class RiskMetrics(BaseModel):
    hhi: float = Field(..., description="Herfindahl-Hirschman Index of holding concentration (0-10000)")
    hhi_rating: str
    diversification_score: float = Field(..., description="0-100, higher is better diversified")
    equity_pct: float
    est_volatility: float = Field(..., description="Estimated annualized portfolio volatility (%)")
    top_holding_pct: float
    concentration_flags: list[str]


class Analytics(BaseModel):
    allocation_by_asset_class: list[AllocationSlice]
    allocation_by_sector: list[AllocationSlice]
    allocation_by_broker: list[AllocationSlice]
    top_holdings: list[ConcentrationItem]
    risk_metrics: RiskMetrics
    insights: list[str]


# --------------------------------------------------------------------------- #
# Risk profiling & suitability
# --------------------------------------------------------------------------- #
class RiskAnswer(BaseModel):
    question_id: str
    option_index: int


class RiskProfileRequest(BaseModel):
    answers: list[RiskAnswer]


class RiskProfileResult(BaseModel):
    score: int = Field(..., description="0-100 risk-tolerance score")
    category: RiskCategory
    description: str
    recommended_equity_band: str
    suitable_asset_classes: list[AssetClass]


class RiskQuestionOption(BaseModel):
    label: str
    points: int


class RiskQuestion(BaseModel):
    id: str
    question: str
    options: list[RiskQuestionOption]


# --------------------------------------------------------------------------- #
# Alternate assets
# --------------------------------------------------------------------------- #
class AltAsset(BaseModel):
    id: str
    name: str
    asset_class: AssetClass
    category: str
    ticker: Optional[str] = None
    yield_pct: Optional[float] = Field(None, description="Distribution / coupon yield (%)")
    rating: Optional[str] = None
    risk_level: str = Field(..., description="Low / Medium / High")
    min_investment: float
    liquidity: str
    tenure: Optional[str] = None
    summary: str
    highlights: list[str] = []
    education: str = ""


class AltAssetView(AltAsset):
    """Alt-asset enriched with a suitability verdict for the current investor."""
    suitability: Suitability = Suitability.SUITABLE
    suitability_reason: str = ""


# --------------------------------------------------------------------------- #
# AI advisor
# --------------------------------------------------------------------------- #
class AdvisorRequest(BaseModel):
    investor_id: str
    message: str
    history: list[dict] = []


class AdvisorResponse(BaseModel):
    reply: str
    grounded_on: list[str] = Field(default_factory=list, description="Portfolio facts used to ground the answer")
    source: str = Field("rule-based", description="'claude' or 'rule-based'")
