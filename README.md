# UnifyInvest

**The Unified Multi-Asset Super App for India's Retail Investors**

> SEBI GFF Hackathon — Problem Statement 3: Super App for Unified Multi-Asset Investing and Awareness for Retail Investors

UnifyInvest consolidates a retail investor's holdings across depositories, brokers, and asset
classes into a single intelligent dashboard, and expands awareness of and access to alternate
instruments (REITs, InvITs, corporate bonds) — the portfolio intelligence previously reserved
for institutional and HNI investors, reimagined for every retail participant.

## Five pillars

1. **Unified Dashboard** — consolidated holdings across brokers / depositories / asset classes
2. **Live Analytics** — allocation, concentration (HHI), exposure, P&L, risk metrics
3. **Risk Profiler + Suitability Engine** — questionnaire → risk score → per-product suitability
4. **Alt-Asset Education & Discovery** — learn about and screen REITs, InvITs, corporate bonds
5. **AI Advisor** — natural-language Q&A grounded on the investor's own portfolio

## Tech stack

- **Frontend:** React 18 + TypeScript (Vite), Recharts, Tailwind CSS
- **Backend:** Python + FastAPI, Pydantic, pandas / NumPy
- **Market data:** AlphaVantage (seeded fallback for offline demos)
- **AI advisor:** Claude (Anthropic) API, grounded on the user's portfolio

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full architecture and
[`docs/SUBMISSION.md`](docs/SUBMISSION.md) for the hackathon submission write-up.

## Getting started

### Backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs (Swagger UI): http://localhost:8000/docs

Optional environment variables (create `backend/.env`, see `.env.example`):

- `ALPHAVANTAGE_API_KEY` — live market data (falls back to seeded data if unset)
- `ANTHROPIC_API_KEY` — AI advisor (falls back to a rule-based advisor if unset)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

## Project layout

```
backend/
  app/
    main.py            FastAPI app + CORS
    routers/           API endpoints (portfolio, analytics, risk, alt-assets, advisor, market)
    services/          business logic (aggregation, analytics, suitability, market, advisor)
    models/            Pydantic schemas
    data/              seed portfolios + alt-asset catalog
  requirements.txt
frontend/
  src/
    pages/             the 5 pillars
    components/        shared UI + charts
    api/               typed API client
docs/                  architecture + submission
```

## Prototype honesty

The personal-holdings feed is **simulated** with realistic seed portfolios behind a
production-ready interface (a live Account Aggregator / NSDL-CDSL connector drops in
without changing downstream services). Analytics, suitability, market data, and the AI
advisor are **real**.
