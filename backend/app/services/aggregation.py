"""Aggregation Service — the Account Aggregator / NSDL-CDSL model.

Pulls holdings for an investor (read-only), overlays live market prices, and
normalizes everything into the canonical Portfolio schema consumed downstream.
"""
from __future__ import annotations

from app.data import seed
from app.models.schemas import (
    AccountSummary,
    Holding,
    HoldingView,
    Portfolio,
    PortfolioSummary,
)
from app.services import market_data


def _to_view(h: Holding) -> HoldingView:
    return HoldingView(
        symbol=h.symbol,
        name=h.name,
        asset_class=h.asset_class,
        sector=h.sector,
        broker=h.broker,
        depository=h.depository,
        quantity=h.quantity,
        avg_cost=h.avg_cost,
        ltp=h.ltp,
        invested=round(h.invested, 2),
        current_value=round(h.current_value, 2),
        pnl=round(h.pnl, 2),
        pnl_pct=round(h.pnl_pct, 2),
    )


def get_raw_holdings(investor_id: str) -> list[Holding]:
    """Fetch normalized holdings with live prices overlaid."""
    holdings = seed.get_holdings(investor_id)
    for h in holdings:
        h.ltp = market_data.get_live_price(h.symbol, h.ltp)
    return holdings


def build_portfolio(investor_id: str) -> Portfolio:
    holdings = get_raw_holdings(investor_id)
    views = [_to_view(h) for h in holdings]

    total_invested = sum(v.invested for v in views)
    total_value = sum(v.current_value for v in views)
    total_pnl = total_value - total_invested

    # Simulated intraday move: a small deterministic fraction of unrealized P&L.
    day_change = round(total_pnl * 0.012, 2)

    # Per-account rollup (broker + depository).
    acc_map: dict[tuple[str, str], AccountSummary] = {}
    for v in views:
        k = (v.broker, v.depository.value)
        if k not in acc_map:
            acc_map[k] = AccountSummary(
                broker=v.broker, depository=v.depository, holdings_count=0, current_value=0.0
            )
        acc_map[k].holdings_count += 1
        acc_map[k].current_value = round(acc_map[k].current_value + v.current_value, 2)

    meta = seed.INVESTORS.get(investor_id, seed.INVESTORS[seed.DEFAULT_INVESTOR])

    summary = PortfolioSummary(
        investor_id=investor_id,
        investor_name=meta["name"],
        total_invested=round(total_invested, 2),
        total_current_value=round(total_value, 2),
        total_pnl=round(total_pnl, 2),
        total_pnl_pct=round((total_pnl / total_invested * 100) if total_invested else 0, 2),
        day_change=day_change,
        day_change_pct=round((day_change / total_value * 100) if total_value else 0, 2),
        holdings_count=len(views),
        accounts=sorted(acc_map.values(), key=lambda a: -a.current_value),
    )

    return Portfolio(
        investor_id=investor_id,
        investor_name=meta["name"],
        summary=summary,
        holdings=sorted(views, key=lambda v: -v.current_value),
    )


def list_investors() -> list[dict]:
    return [
        {"id": iid, "name": meta["name"], "tagline": meta["tagline"]}
        for iid, meta in seed.INVESTORS.items()
    ]
