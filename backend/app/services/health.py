"""Portfolio Health Score & investor-protection alerts.

Distils the whole portfolio into one memorable A–F grade across four weighted lenses,
and surfaces investor-protection alerts (hidden concentration, suitability mismatches,
missing safety nets) in the language a regulator cares about.
"""
from __future__ import annotations

from app.models.schemas import (
    Analytics,
    HealthComponent,
    HealthScore,
    Portfolio,
    ProtectionAlert,
    RiskProfileResult,
    XRay,
)


def _grade(score: int) -> str:
    if score >= 90: return "A+"
    if score >= 80: return "A"
    if score >= 70: return "B"
    if score >= 60: return "C"
    if score >= 50: return "D"
    return "F"


def compute(
    portfolio: Portfolio,
    analytics: Analytics,
    xray: XRay,
    profile: RiskProfileResult | None,
) -> HealthScore:
    rm = analytics.risk_metrics

    # 1. Diversification (from analytics score)
    div = rm.diversification_score
    div_detail = f"Diversification score {div:.0f}/100 ({rm.hhi_rating})."

    # 2. True concentration (look-through) — penalize high single-name true exposure
    top_true = max((e.true_pct for e in xray.exposures), default=0.0)
    conc = max(0.0, 100 - (top_true - 10) * 4) if top_true > 10 else 100.0
    conc = min(100.0, conc)
    conc_detail = f"Largest true single-name exposure is {top_true:.0f}% (look-through)."

    # 3. Asset-class balance — reward diversification beyond equity
    equity = rm.equity_pct
    has_fixed = any(a.label in ("Bond",) for a in analytics.allocation_by_asset_class)
    has_alt = any(a.label in ("REIT", "InvIT") for a in analytics.allocation_by_asset_class)
    balance = 100.0
    if equity >= 85: balance -= 35
    elif equity >= 75: balance -= 22
    elif equity >= 65: balance -= 10
    if not has_fixed: balance -= 15
    if not has_alt: balance -= 8
    balance = max(0.0, balance)
    balance_detail = f"{equity:.0f}% equity; fixed income: {'yes' if has_fixed else 'no'}, REIT/InvIT: {'yes' if has_alt else 'no'}."

    # 4. Suitability — do holdings match the investor's risk profile?
    if profile is None:
        suit = 65.0
        suit_detail = "Risk profile not completed — suitability not assessed."
    else:
        suit, suit_detail = _suitability_score(portfolio, analytics, profile)

    components = [
        HealthComponent(label="Diversification", score=round(div, 1), weight=0.30, detail=div_detail),
        HealthComponent(label="True Concentration", score=round(conc, 1), weight=0.25, detail=conc_detail),
        HealthComponent(label="Asset-Class Balance", score=round(balance, 1), weight=0.25, detail=balance_detail),
        HealthComponent(label="Suitability", score=round(suit, 1), weight=0.20, detail=suit_detail),
    ]
    overall = round(sum(c.score * c.weight for c in components))
    grade = _grade(overall)

    alerts = _protection_alerts(portfolio, analytics, xray, profile)

    summary = _summary(overall, grade, alerts)
    return HealthScore(
        score=overall, grade=grade, summary=summary,
        components=components, protection_alerts=alerts,
    )


def _suitability_score(portfolio, analytics, profile: RiskProfileResult) -> tuple[float, str]:
    """Fraction of portfolio value in asset classes suitable for the profile."""
    suitable_classes = {c.value for c in profile.suitable_asset_classes}
    total = sum(h.current_value for h in portfolio.holdings) or 1.0
    suitable_val = sum(h.current_value for h in portfolio.holdings if h.asset_class.value in suitable_classes)
    frac = suitable_val / total * 100
    # Penalize equity that exceeds the recommended band ceiling.
    band_ceiling = int(profile.recommended_equity_band.split("–")[1].split("%")[0].strip()) \
        if "–" in profile.recommended_equity_band else 100
    over = max(0.0, analytics.risk_metrics.equity_pct - band_ceiling)
    score = max(0.0, frac - over * 1.5)
    detail = (
        f"{frac:.0f}% of value is in classes suitable for a {profile.category} investor; "
        f"equity {analytics.risk_metrics.equity_pct:.0f}% vs recommended {profile.recommended_equity_band}."
    )
    return min(100.0, score), detail


def _protection_alerts(portfolio, analytics, xray: XRay, profile) -> list[ProtectionAlert]:
    alerts: list[ProtectionAlert] = []

    # Hidden concentration from X-Ray
    for e in xray.top_hidden:
        if e.flag and e.apparent_pct < 15 <= e.true_pct:
            alerts.append(ProtectionAlert(
                severity="high",
                title=f"Hidden concentration in {e.name}",
                detail=(
                    f"You appear {e.apparent_pct:.0f}% exposed but are truly {e.true_pct:.0f}% "
                    f"exposed once funds ({', '.join(e.via_funds)}) are looked through. "
                    "A shock to this name would hurt more than the surface view suggests."
                ),
                holding=e.name,
            ))

    # Suitability mismatch — holdings riskier than the profile allows
    if profile is not None:
        suitable = {c.value for c in profile.suitable_asset_classes}
        total = sum(h.current_value for h in portfolio.holdings) or 1.0
        for h in portfolio.holdings:
            if h.asset_class.value not in suitable and (h.current_value / total) >= 0.05:
                alerts.append(ProtectionAlert(
                    severity="medium",
                    title=f"Possible mis-match: {h.name}",
                    detail=(
                        f"{h.asset_class.value} may not suit your {profile.category} risk profile. "
                        "If this was recommended to you, confirm it fits your goals — a hallmark check against mis-selling."
                    ),
                    holding=h.name,
                ))

    # Sector concentration
    top_sector = analytics.allocation_by_sector[0] if analytics.allocation_by_sector else None
    if top_sector and top_sector.pct >= 35:
        alerts.append(ProtectionAlert(
            severity="medium",
            title=f"{top_sector.label} sector concentration",
            detail=f"{top_sector.pct:.0f}% of your portfolio is in {top_sector.label}. Consider spreading across sectors.",
        ))

    # No fixed-income safety net
    has_fixed = any(a.label == "Bond" for a in analytics.allocation_by_asset_class)
    if not has_fixed and analytics.risk_metrics.equity_pct >= 70:
        alerts.append(ProtectionAlert(
            severity="low",
            title="No fixed-income cushion",
            detail="You hold no bonds/SGBs. A small fixed-income allocation cushions equity drawdowns.",
        ))

    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(alerts, key=lambda a: order.get(a.severity, 3))


def _summary(score: int, grade: str, alerts) -> str:
    highs = sum(1 for a in alerts if a.severity == "high")
    if grade in ("A+", "A"):
        base = "Strong, well-constructed portfolio."
    elif grade in ("B", "C"):
        base = "Reasonable portfolio with room to improve."
    else:
        base = "Portfolio needs attention on diversification and risk."
    if highs:
        base += f" {highs} high-priority protection alert{'s' if highs > 1 else ''} to review."
    return base
