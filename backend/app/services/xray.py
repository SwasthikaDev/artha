"""Portfolio X-Ray — look-through analysis.

Decomposes mutual funds / ETFs into their underlying holdings to reveal the investor's
TRUE concentration, which is hidden when funds are treated as opaque line-items. This is
the signature differentiator: direct equity + fund-embedded equity in the same name
compound into concentration the surface view never shows.
"""
from __future__ import annotations

from collections import defaultdict

from app.data import fund_composition as fc
from app.models.schemas import HoldingView, XRay, XRayExposure, XRaySectorExposure

_FLAG_TRUE_PCT = 15.0  # true single-name exposure worth flagging


def compute(holdings: list[HoldingView]) -> XRay:
    total = sum(h.current_value for h in holdings) or 1.0

    # apparent[symbol] = value held DIRECTLY as that symbol (funds counted as themselves)
    apparent: dict[str, float] = defaultdict(float)
    # true[symbol] = look-through value (funds decomposed into underlyings)
    true: dict[str, float] = defaultdict(float)
    meta: dict[str, tuple[str, str]] = {}   # symbol -> (name, sector)
    via: dict[str, set[str]] = defaultdict(set)

    for h in holdings:
        apparent[h.symbol] += h.current_value
        meta.setdefault(h.symbol, (h.name, h.sector))

        comp = fc.get_composition(h.symbol)
        if comp:
            # decompose the fund into its underlying names
            for u_sym, u_name, u_sector, weight in comp:
                val = h.current_value * weight / 100.0
                true[u_sym] += val
                meta.setdefault(u_sym, (u_name, u_sector))
                via[u_sym].add(h.name)
            # remainder ("Other / smaller holdings") stays inside the fund bucket
            covered = sum(w for _, _, _, w in comp)
            if covered < 100:
                rem_val = h.current_value * (100 - covered) / 100.0
                true[f"{h.symbol}_OTHER"] += rem_val
                meta.setdefault(f"{h.symbol}_OTHER", (f"{h.name} — other holdings", h.sector))
        else:
            true[h.symbol] += h.current_value

    # Build per-name exposures, merging apparent + true
    names = set(apparent) | set(true)
    exposures: list[XRayExposure] = []
    for sym in names:
        if sym.endswith("_OTHER"):
            continue
        name, sector = meta.get(sym, (sym, "Diversified"))
        a_val = apparent.get(sym, 0.0)
        t_val = true.get(sym, 0.0)
        # A pure fund line-item (held directly but also decomposed) shouldn't double count:
        # if it's a fund, its "apparent" as itself is not a real underlying-name exposure.
        if fc.is_fund(sym):
            continue
        hidden = max(t_val - a_val, 0.0)
        exposures.append(
            XRayExposure(
                symbol=sym,
                name=name,
                sector=sector,
                apparent_value=round(a_val, 2),
                apparent_pct=round(a_val / total * 100, 2),
                true_value=round(t_val, 2),
                true_pct=round(t_val / total * 100, 2),
                hidden_value=round(hidden, 2),
                via_funds=sorted(via.get(sym, set())),
                flag=(t_val / total * 100) >= _FLAG_TRUE_PCT,
            )
        )

    exposures.sort(key=lambda e: -e.true_value)

    # Sector-level apparent vs true
    sec_apparent: dict[str, float] = defaultdict(float)
    sec_true: dict[str, float] = defaultdict(float)
    for h in holdings:
        if not fc.is_fund(h.symbol):
            sec_apparent[h.sector] += h.current_value
    for sym, t_val in true.items():
        _, sector = meta.get(sym, (sym, "Diversified"))
        sec_true[sector] += t_val
    sectors = set(sec_apparent) | set(sec_true)
    sector_exposures = sorted(
        [
            XRaySectorExposure(
                sector=s,
                apparent_pct=round(sec_apparent.get(s, 0) / total * 100, 2),
                true_pct=round(sec_true.get(s, 0) / total * 100, 2),
                delta_pct=round((sec_true.get(s, 0) - sec_apparent.get(s, 0)) / total * 100, 2),
            )
            for s in sectors
        ],
        key=lambda x: -x.true_pct,
    )

    top_hidden = sorted(
        [e for e in exposures if e.hidden_value > 0], key=lambda e: -e.hidden_value
    )[:5]

    headline, insights = _narrate(exposures, top_hidden, sector_exposures)
    return XRay(
        exposures=exposures,
        sector_exposures=sector_exposures,
        top_hidden=top_hidden,
        headline=headline,
        insights=insights,
    )


def _narrate(exposures, top_hidden, sector_exposures) -> tuple[str, list[str]]:
    insights: list[str] = []
    headline = "Your look-through exposure closely matches your surface view."

    if top_hidden:
        t = top_hidden[0]
        headline = (
            f"You hold {t.true_pct:.0f}% in {t.name} on a look-through basis — "
            f"vs {t.apparent_pct:.0f}% visible on the surface."
        )
        for e in top_hidden[:3]:
            if e.hidden_value > 0:
                fund_list = ", ".join(e.via_funds) if e.via_funds else "your funds"
                insights.append(
                    f"{e.name}: {e.apparent_pct:.0f}% direct → {e.true_pct:.0f}% true "
                    f"(+{e.true_pct - e.apparent_pct:.0f}pp hidden inside {fund_list})."
                )

    flagged = [e for e in exposures if e.flag]
    for e in flagged:
        if e.apparent_pct < _FLAG_TRUE_PCT <= e.true_pct:
            insights.append(
                f"⚠ {e.name} crosses the 15% concentration line only once funds are "
                f"looked through — invisible on the surface."
            )

    worst_sector = max(sector_exposures, key=lambda s: s.delta_pct, default=None)
    if worst_sector and worst_sector.delta_pct >= 5:
        insights.append(
            f"{worst_sector.sector} exposure is actually {worst_sector.true_pct:.0f}% "
            f"(+{worst_sector.delta_pct:.0f}pp once funds are decomposed)."
        )

    if not insights:
        insights.append("No significant hidden concentration detected — your funds diversify well.")
    return headline, insights
