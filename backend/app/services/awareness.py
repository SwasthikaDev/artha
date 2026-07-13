"""Awareness engine — the education half of PS3.

Provides per-instrument quiz questions (to check comprehension before investing) and
suitability-driven nudges that surface gaps in the investor's portfolio.
"""
from __future__ import annotations

from app.data import alt_assets as catalog
from app.models.schemas import (
    Analytics,
    Nudge,
    Portfolio,
    QuizOption,
    QuizQuestion,
    RiskProfileResult,
)

# One comprehension question per asset class, keyed by asset id prefix / class.
_QUIZ_BY_CLASS = {
    "REIT": QuizQuestion(
        asset_id="",
        question="What must a SEBI-registered REIT distribute to unitholders?",
        options=[
            QuizOption(label="At least 90% of net distributable cash flow", correct=True),
            QuizOption(label="Nothing — REITs only give capital gains", correct=False),
            QuizOption(label="Exactly 50% of profits", correct=False),
        ],
        explanation="SEBI mandates REITs distribute at least 90% of net distributable cash flow — the source of their steady yields.",
    ),
    "InvIT": QuizQuestion(
        asset_id="",
        question="An InvIT primarily earns income from…",
        options=[
            QuizOption(label="Operating infrastructure like power lines, roads, pipelines", correct=True),
            QuizOption(label="Trading equity shares intraday", correct=False),
            QuizOption(label="Cryptocurrency mining", correct=False),
        ],
        explanation="InvITs own operating infrastructure assets with contracted cash flows, which they pass to unitholders.",
    ),
    "Bond": QuizQuestion(
        asset_id="",
        question="What does a higher credit rating (e.g. AAA vs AA) indicate?",
        options=[
            QuizOption(label="Lower default risk", correct=True),
            QuizOption(label="Higher guaranteed returns", correct=False),
            QuizOption(label="The bond is tax-free", correct=False),
        ],
        explanation="Ratings signal default risk: AAA is safest. Higher yields usually compensate for higher risk.",
    ),
}


def quiz_for(asset_id: str) -> QuizQuestion | None:
    asset = catalog.get_asset(asset_id)
    if not asset:
        return None
    # Special case: SGB
    if "sgb" in asset_id:
        return QuizQuestion(
            asset_id=asset_id,
            question="What advantage does a Sovereign Gold Bond have over physical gold?",
            options=[
                QuizOption(label="It pays 2.5% annual interest on top of gold price movement", correct=True),
                QuizOption(label="It can be worn as jewellery", correct=False),
                QuizOption(label="Its price never falls", correct=False),
            ],
            explanation="SGBs track gold AND pay 2.5% annual interest, with no storage/making-charge cost, and are tax-free on maturity.",
        )
    q = _QUIZ_BY_CLASS.get(asset.asset_class.value)
    if not q:
        return None
    return q.model_copy(update={"asset_id": asset_id})


def nudges(portfolio: Portfolio, analytics: Analytics, profile: RiskProfileResult | None) -> list[Nudge]:
    out: list[Nudge] = []
    classes = {a.label for a in analytics.allocation_by_asset_class}
    rm = analytics.risk_metrics

    # Gap: no fixed income
    if "Bond" not in classes:
        sgb = catalog.get_asset("sgb-2032")
        out.append(Nudge(
            kind="gap",
            title="You have no fixed income",
            detail="A small bond/SGB allocation adds stable income and cushions equity falls.",
            cta="Explore Sovereign Gold Bonds",
            asset_id=sgb.id if sgb else None,
        ))

    # Gap: no REIT/InvIT
    if "REIT" not in classes and "InvIT" not in classes:
        out.append(Nudge(
            kind="gap",
            title="No real-estate or infra exposure",
            detail="REITs and InvITs offer 6–10% yields and diversification beyond equities.",
            cta="Discover REITs & InvITs",
            asset_id="embassy-reit",
        ))

    # Concentration
    if rm.equity_pct >= 75:
        out.append(Nudge(
            kind="concentration",
            title=f"{rm.equity_pct:.0f}% of your money is in equity",
            detail="High equity concentration raises volatility. Consider rebalancing toward income assets.",
            cta="See suitable alternatives",
        ))

    # Opportunity based on profile
    if profile is not None:
        suitable = {c.value for c in profile.suitable_asset_classes}
        picks = [a for a in catalog.get_catalog() if a.asset_class.value in suitable]
        if picks:
            top = sorted(picks, key=lambda a: -(a.yield_pct or 0))[0]
            out.append(Nudge(
                kind="opportunity",
                title=f"Matched to your {profile.category} profile",
                detail=f"{top.name} ({top.yield_pct}% yield) fits your risk profile and recommended mix.",
                cta=f"Learn about {top.name}",
                asset_id=top.id,
            ))
    else:
        out.append(Nudge(
            kind="education",
            title="Complete your risk profile",
            detail="Answer 5 questions to unlock personalized suitability on every instrument.",
            cta="Take the risk assessment",
        ))

    return out
