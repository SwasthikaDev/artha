"""UnifyInvest API — FastAPI entrypoint.

Consolidates a retail investor's multi-asset portfolio and powers the five pillars:
aggregation, analytics, risk profiling + suitability, alt-asset discovery, and the AI advisor.
"""
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.routers import advisor, alt_assets, analytics, insights, portfolio, risk  # noqa: E402
from app.services import market_data  # noqa: E402

app = FastAPI(
    title="UnifyInvest API",
    description="Unified multi-asset super app for India's retail investors (SEBI GFF Hackathon — PS3).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio.router)
app.include_router(analytics.router)
app.include_router(risk.router)
app.include_router(alt_assets.router)
app.include_router(advisor.router)
app.include_router(insights.router)


@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok"}


@app.get("/api/status", tags=["system"])
def status():
    """Reports which integrations are live vs. running on seeded fallbacks."""
    return {
        "market_data": "live (AlphaVantage)" if market_data.is_live() else "seeded fallback",
        "ai_advisor": "live (Claude)" if os.getenv("ANTHROPIC_API_KEY") else "rule-based fallback",
    }
