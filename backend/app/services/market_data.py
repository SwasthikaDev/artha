"""Market-Data Adapter — overlays live prices onto seed holdings.

Uses AlphaVantage when ALPHAVANTAGE_API_KEY is set; otherwise returns the seeded
price so the app demos fully offline. Results are cached in-process to respect the
free-tier rate limit.
"""
from __future__ import annotations

import os

import httpx

_CACHE: dict[str, float] = {}
_BASE = "https://www.alphavantage.co/query"


def _api_key() -> str | None:
    return os.getenv("ALPHAVANTAGE_API_KEY") or None


def get_live_price(symbol: str, fallback: float) -> float:
    """Return a live price for `symbol`, falling back to the seeded value.

    AlphaVantage uses `.BSE` suffixes for Indian equities; we best-effort try that
    and gracefully degrade to the fallback on any error or missing key.
    """
    key = _api_key()
    if not key:
        return fallback
    if symbol in _CACHE:
        return _CACHE[symbol]
    try:
        resp = httpx.get(
            _BASE,
            params={"function": "GLOBAL_QUOTE", "symbol": f"{symbol}.BSE", "apikey": key},
            timeout=6.0,
        )
        data = resp.json().get("Global Quote", {})
        price = float(data.get("05. price", 0) or 0)
        if price > 0:
            _CACHE[symbol] = price
            return price
    except Exception:
        pass
    return fallback


def is_live() -> bool:
    return _api_key() is not None
