"""Risk-Profile & Suitability Engine — the investor-protection core.

Turns questionnaire answers into a risk score/category, and tags each alternate asset
as Suitable / Caution / Unsuitable for THAT investor.
"""
from __future__ import annotations

from app.models.schemas import (
    AltAsset,
    AltAssetView,
    AssetClass,
    RiskCategory,
    RiskProfileRequest,
    RiskProfileResult,
    RiskQuestion,
    RiskQuestionOption,
    Suitability,
)

# --------------------------------------------------------------------------- #
# Questionnaire (SEBI-style suitability inputs: horizon, capacity, tolerance,
# experience, liquidity)
# --------------------------------------------------------------------------- #
QUESTIONS: list[RiskQuestion] = [
    RiskQuestion(
        id="horizon",
        question="How long do you plan to stay invested?",
        options=[
            RiskQuestionOption(label="Less than 1 year", points=0),
            RiskQuestionOption(label="1–3 years", points=5),
            RiskQuestionOption(label="3–7 years", points=12),
            RiskQuestionOption(label="More than 7 years", points=20),
        ],
    ),
    RiskQuestion(
        id="reaction",
        question="Your portfolio drops 20% in a month. What do you do?",
        options=[
            RiskQuestionOption(label="Sell everything to avoid further loss", points=0),
            RiskQuestionOption(label="Sell some holdings", points=6),
            RiskQuestionOption(label="Do nothing and wait", points=14),
            RiskQuestionOption(label="Buy more at lower prices", points=20),
        ],
    ),
    RiskQuestion(
        id="income",
        question="How stable is your income and emergency fund?",
        options=[
            RiskQuestionOption(label="Unstable, little savings", points=0),
            RiskQuestionOption(label="Stable, small buffer", points=7),
            RiskQuestionOption(label="Stable with 6+ months buffer", points=15),
            RiskQuestionOption(label="Very secure, large buffer", points=20),
        ],
    ),
    RiskQuestion(
        id="experience",
        question="How experienced are you with investing?",
        options=[
            RiskQuestionOption(label="First-time investor", points=0),
            RiskQuestionOption(label="Some mutual funds / stocks", points=7),
            RiskQuestionOption(label="Comfortable across asset classes", points=14),
            RiskQuestionOption(label="Very experienced, understand derivatives", points=20),
        ],
    ),
    RiskQuestion(
        id="goal",
        question="What is your primary goal for this money?",
        options=[
            RiskQuestionOption(label="Protect capital, steady income", points=0),
            RiskQuestionOption(label="Modest, stable growth", points=7),
            RiskQuestionOption(label="Long-term wealth building", points=14),
            RiskQuestionOption(label="Maximum growth, accept big swings", points=20),
        ],
    ),
]

_OPTS_BY_Q = {q.id: q.options for q in QUESTIONS}


def score_profile(req: RiskProfileRequest) -> RiskProfileResult:
    total = 0
    for ans in req.answers:
        opts = _OPTS_BY_Q.get(ans.question_id)
        if opts and 0 <= ans.option_index < len(opts):
            total += opts[ans.option_index].points
    # Normalize to 0-100 (max is 5 questions x 20 = 100 already, but stay safe).
    max_points = sum(max(o.points for o in q.options) for q in QUESTIONS) or 1
    score = round(total / max_points * 100)

    if score < 20:
        cat, band, desc = (
            RiskCategory.CONSERVATIVE,
            "10–25% equity",
            "You prioritize capital protection and steady income over growth.",
        )
        classes = [AssetClass.BOND, AssetClass.CASH, AssetClass.GOLD, AssetClass.MUTUAL_FUND]
    elif score < 40:
        cat, band, desc = (
            RiskCategory.MODERATE,
            "25–45% equity",
            "You accept small fluctuations for modest, stable growth.",
        )
        classes = [AssetClass.BOND, AssetClass.MUTUAL_FUND, AssetClass.REIT, AssetClass.GOLD, AssetClass.INVIT]
    elif score < 60:
        cat, band, desc = (
            RiskCategory.BALANCED,
            "45–65% equity",
            "You seek a balance between growth and stability.",
        )
        classes = [AssetClass.EQUITY, AssetClass.MUTUAL_FUND, AssetClass.ETF, AssetClass.REIT, AssetClass.INVIT, AssetClass.BOND]
    elif score < 80:
        cat, band, desc = (
            RiskCategory.GROWTH,
            "65–80% equity",
            "You focus on long-term growth and can ride out volatility.",
        )
        classes = [AssetClass.EQUITY, AssetClass.ETF, AssetClass.MUTUAL_FUND, AssetClass.REIT, AssetClass.INVIT]
    else:
        cat, band, desc = (
            RiskCategory.AGGRESSIVE,
            "80–100% equity",
            "You pursue maximum growth and accept large swings in value.",
        )
        classes = [AssetClass.EQUITY, AssetClass.ETF, AssetClass.INVIT, AssetClass.REIT]

    return RiskProfileResult(
        score=score,
        category=cat,
        description=desc,
        recommended_equity_band=band,
        suitable_asset_classes=classes,
    )


# --------------------------------------------------------------------------- #
# Suitability tagging of alternate assets
# --------------------------------------------------------------------------- #
_RISK_RANK = {"Low": 1, "Medium": 2, "High": 3}

# Max instrument risk tolerated per investor category.
_CATEGORY_MAX_RISK = {
    RiskCategory.CONSERVATIVE: 1,
    RiskCategory.MODERATE: 2,
    RiskCategory.BALANCED: 2,
    RiskCategory.GROWTH: 3,
    RiskCategory.AGGRESSIVE: 3,
}


def tag_suitability(asset: AltAsset, profile: RiskProfileResult | None) -> AltAssetView:
    view = AltAssetView(**asset.model_dump())
    if profile is None:
        view.suitability = Suitability.SUITABLE
        view.suitability_reason = "Complete your risk profile to get a personalized suitability check."
        return view

    instrument_risk = _RISK_RANK.get(asset.risk_level, 2)
    max_risk = _CATEGORY_MAX_RISK[profile.category]
    class_ok = asset.asset_class in profile.suitable_asset_classes

    if instrument_risk > max_risk:
        view.suitability = Suitability.UNSUITABLE
        view.suitability_reason = (
            f"{asset.risk_level}-risk instrument exceeds your {profile.category.value} risk profile."
        )
    elif not class_ok:
        view.suitability = Suitability.CAUTION
        view.suitability_reason = (
            f"{asset.asset_class.value} is outside your recommended mix — consider a small allocation only."
        )
    elif instrument_risk == max_risk and profile.category in (RiskCategory.MODERATE, RiskCategory.BALANCED):
        view.suitability = Suitability.CAUTION
        view.suitability_reason = (
            f"Fits your profile but sits at the top of your risk band — size the position modestly."
        )
    else:
        view.suitability = Suitability.SUITABLE
        view.suitability_reason = (
            f"Matches your {profile.category.value} profile and recommended asset mix."
        )
    return view
