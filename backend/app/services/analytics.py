"""Analytics Engine — allocation, concentration (HHI), exposure, and risk metrics.

Pure functions over normalized holdings. No external dependencies beyond the standard
library so it stays fast and deterministic for the demo.
"""
from __future__ import annotations

from collections import defaultdict

from app.models.schemas import (
    AllocationSlice,
    Analytics,
    ConcentrationItem,
    HoldingView,
    RiskMetrics,
)

# Rough annualized volatility assumptions per asset class (%), used to estimate
# a blended portfolio volatility. Indicative values for the prototype.
_VOL = {
    "Equity": 22.0,
    "ETF": 18.0,
    "Mutual Fund": 16.0,
    "REIT": 14.0,
    "InvIT": 15.0,
    "Bond": 5.0,
    "Gold": 13.0,
    "Cash": 0.5,
}

_SINGLE_STOCK_FLAG = 15.0   # % of portfolio in one holding is worth flagging
_SECTOR_FLAG = 35.0         # % in one sector
_ASSET_CLASS_FLAG = 80.0    # % in one asset class


def _alloc(pairs: dict[str, float], total: float) -> list[AllocationSlice]:
    out = [
        AllocationSlice(label=k, value=round(v, 2), pct=round(v / total * 100, 2) if total else 0)
        for k, v in pairs.items()
    ]
    return sorted(out, key=lambda s: -s.value)


def compute(holdings: list[HoldingView]) -> Analytics:
    total = sum(h.current_value for h in holdings) or 1.0

    by_asset: dict[str, float] = defaultdict(float)
    by_sector: dict[str, float] = defaultdict(float)
    by_broker: dict[str, float] = defaultdict(float)
    for h in holdings:
        by_asset[h.asset_class.value] += h.current_value
        by_sector[h.sector] += h.current_value
        by_broker[h.broker] += h.current_value

    alloc_asset = _alloc(by_asset, total)
    alloc_sector = _alloc(by_sector, total)
    alloc_broker = _alloc(by_broker, total)

    # Top holdings + concentration flags
    top = sorted(holdings, key=lambda h: -h.current_value)[:10]
    top_items = [
        ConcentrationItem(
            label=h.name,
            pct=round(h.current_value / total * 100, 2),
            flag=(h.current_value / total * 100) >= _SINGLE_STOCK_FLAG,
        )
        for h in top
    ]

    # Herfindahl-Hirschman Index over individual holdings (0-10000).
    shares = [h.current_value / total * 100 for h in holdings]
    hhi = round(sum(s * s for s in shares), 1)
    if hhi < 1500:
        hhi_rating = "Well diversified"
    elif hhi < 2500:
        hhi_rating = "Moderately concentrated"
    else:
        hhi_rating = "Highly concentrated"

    # Diversification score: 100 at perfect equal-weight, decaying with HHI.
    n = max(len(holdings), 1)
    ideal_hhi = 10000 / n
    diversification = max(0.0, min(100.0, round(100 * ideal_hhi / hhi, 1))) if hhi else 100.0

    equity_pct = round(
        sum(h.current_value for h in holdings if h.asset_class.value in ("Equity", "ETF")) / total * 100, 2
    )

    est_vol = round(sum((h.current_value / total) * _VOL.get(h.asset_class.value, 15.0) for h in holdings), 1)
    top_holding_pct = top_items[0].pct if top_items else 0.0

    # Concentration flags (human-readable)
    flags: list[str] = []
    for item in top_items:
        if item.flag:
            flags.append(f"{item.label} is {item.pct:.0f}% of your portfolio (single-holding concentration)")
    for s in alloc_sector:
        if s.pct >= _SECTOR_FLAG:
            flags.append(f"{s.label} sector is {s.pct:.0f}% of your portfolio (sector concentration)")
    for a in alloc_asset:
        if a.pct >= _ASSET_CLASS_FLAG:
            flags.append(f"{a.pct:.0f}% is in {a.label} alone (low asset-class diversification)")

    risk = RiskMetrics(
        hhi=hhi,
        hhi_rating=hhi_rating,
        diversification_score=diversification,
        equity_pct=equity_pct,
        est_volatility=est_vol,
        top_holding_pct=top_holding_pct,
        concentration_flags=flags,
    )

    insights = _insights(alloc_asset, alloc_sector, risk, equity_pct)

    return Analytics(
        allocation_by_asset_class=alloc_asset,
        allocation_by_sector=alloc_sector,
        allocation_by_broker=alloc_broker,
        top_holdings=top_items,
        risk_metrics=risk,
        insights=insights,
    )


def _insights(alloc_asset, alloc_sector, risk: RiskMetrics, equity_pct: float) -> list[str]:
    out: list[str] = []
    if equity_pct >= 75:
        out.append(
            f"Your portfolio is {equity_pct:.0f}% equity — consider fixed income (bonds, SGBs) "
            "or REITs/InvITs to reduce volatility."
        )
    top_sector = alloc_sector[0] if alloc_sector else None
    if top_sector and top_sector.pct >= _SECTOR_FLAG:
        out.append(
            f"{top_sector.label} makes up {top_sector.pct:.0f}% of holdings — a downturn in this "
            "sector would hit your portfolio hard."
        )
    has_alt = any(a.label in ("REIT", "InvIT", "Bond") for a in alloc_asset)
    if not has_alt:
        out.append(
            "You hold no REITs, InvITs, or bonds. These can add regular income and diversification "
            "beyond equities — explore them in the Alt-Asset section."
        )
    if risk.diversification_score >= 70:
        out.append(f"Diversification score is healthy at {risk.diversification_score:.0f}/100.")
    elif risk.diversification_score < 45:
        out.append(
            f"Diversification score is low ({risk.diversification_score:.0f}/100) — your value is "
            "concentrated in a few holdings."
        )
    if not out:
        out.append("Your allocation looks balanced across asset classes and sectors.")
    return out
