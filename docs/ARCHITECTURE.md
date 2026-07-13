# Artha — Process Flow & Architecture

**Project:** Artha — The Unified Multi-Asset Super App for India's Retail Investors
**Problem Statement:** SEBI GFF Hackathon — PS3: Super App for Unified Multi-Asset Investing and Awareness for Retail Investors
**Document:** System Architecture & Process Flow Specification
**Version:** 1.0

---

## 1. Overview

Artha is a secure, consent-driven super app that consolidates a retail investor's holdings across depositories, brokers, and asset classes into a single intelligent dashboard, while simultaneously expanding awareness of and access to alternate instruments (REITs, InvITs, corporate bonds, and emerging products).

The system is organized as a **React single-page frontend** talking over HTTPS/REST to a **FastAPI backend** composed of six cooperating services. The design cleanly separates the *aggregation* concern (getting data in, read-only, with consent) from the *intelligence* concern (analytics, suitability, and AI advice).

### Design principles

| Principle | How it is honored |
|---|---|
| **Consent-first** | All personal-holdings access follows the RBI Account Aggregator consent model. The app is read-only and never takes custody of assets. |
| **Investor protection by design** | Every alternate-asset recommendation passes through a suitability engine tied to the investor's risk profile. |
| **Grounded intelligence** | The AI advisor answers only against the investor's real portfolio and a curated knowledge base — no ungrounded speculation. |
| **Graceful degradation** | Live market data has a seeded fallback so the product demos fully offline. |
| **Modular services** | Each backend concern is an independent, independently testable service. |

---

## 2. High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                        REACT + TYPESCRIPT UI (Vite)                     │
│                                                                         │
│   Unified      Risk &        Risk         Alt-Asset       AI            │
│   Dashboard    Exposure      Profiler +   Education &     Advisor       │
│   (holdings)   Analytics     Suitability  Discovery       Chat          │
│                                                                         │
│   Recharts / D3 visualizations · Tailwind CSS · Light & Dark themes     │
└─────────────────────────────────┬─────────────────────────────────────┘
                                   │  HTTPS / REST (JSON)
                                   │  Token-based auth
┌─────────────────────────────────▼─────────────────────────────────────┐
│                            FASTAPI  BACKEND                              │
│                        (Python · Pydantic schemas)                      │
│                                                                         │
│  ┌────────────────┐   ┌────────────────┐   ┌─────────────────────────┐  │
│  │  Aggregation   │   │  Analytics     │   │  Risk-Profile &         │  │
│  │  Service       │   │  Engine        │   │  Suitability Engine     │  │
│  │                │   │                │   │                         │  │
│  │ AA / NSDL-CDSL │   │ allocation,    │   │ questionnaire → score,  │  │
│  │ consent model, │   │ HHI concentr., │   │ per-product suitable /  │  │
│  │ read-only pull │   │ exposure, P&L, │   │ caution / unsuitable    │  │
│  │ of holdings    │   │ risk metrics   │   │ tagging                 │  │
│  └───────┬────────┘   └───────┬────────┘   └───────────┬─────────────┘  │
│          │                    │                        │                │
│  ┌───────▼────────┐   ┌───────▼────────┐   ┌───────────▼─────────────┐  │
│  │  Market-Data   │   │  Alt-Asset     │   │  AI Advisor Service     │  │
│  │  Adapter       │   │  Catalog +     │   │                         │  │
│  │                │   │  Screener      │   │ Claude API, retrieval-  │  │
│  │ AlphaVantage   │   │                │   │ grounded on portfolio + │  │
│  │ + seeded       │   │ REITs, InvITs, │   │ knowledge base          │  │
│  │ fallback       │   │ bonds catalog  │   │                         │  │
│  └────────────────┘   └────────────────┘   └─────────────────────────┘  │
│                                                                         │
└─────────────────────────────────┬─────────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
┌───────▼────────┐        ┌────────▼─────────┐       ┌────────▼─────────┐
│ Account Aggreg. │        │  AlphaVantage    │       │  Claude          │
│ / NSDL-CDSL     │        │  Market Data     │       │  (Anthropic) API │
│ (simulated with │        │  APIs            │       │                  │
│  seed data)     │        │                  │       │                  │
└─────────────────┘        └──────────────────┘       └──────────────────┘
       EXTERNAL / SIMULATED DATA SOURCES & MODEL PROVIDERS
```

---

## 3. Component Responsibilities

### 3.1 Frontend (React + TypeScript, Vite)

| Module | Responsibility |
|---|---|
| **Unified Dashboard** | Consolidated net worth, holdings table across brokers/depositories/asset classes, asset-allocation donut, top movers. |
| **Analytics View** | Concentration heatmaps, sector & asset-class exposure, realized/unrealized P&L, diversification and risk scores. |
| **Risk Profiler** | Guided questionnaire that produces a risk score and investor category (Conservative → Aggressive). |
| **Alt-Asset Explorer** | Discover, learn about, and screen REITs, InvITs, and corporate bonds — filtered by suitability. |
| **AI Advisor Chat** | Natural-language chat grounded on the investor's portfolio. |

Cross-cutting: Recharts/D3 for visualization, Tailwind CSS for responsive and theme-aware styling, a typed API client mirroring the backend Pydantic schemas.

### 3.2 Backend services (FastAPI)

**1. Aggregation Service**
- Models the RBI Account Aggregator + SEBI-NSDL-CDSL Unified Investor Platform flow.
- Consent-based, read-only pull of holdings across multiple demat/trading accounts.
- Normalizes heterogeneous broker/depository formats into one canonical holdings schema.
- *Prototype:* backed by realistic seed portfolios; production swaps in live AA/depository connectors behind the same interface.

**2. Analytics Engine**
- pandas/NumPy computations over normalized holdings enriched with live prices.
- Metrics: asset-class & sector allocation, concentration via **Herfindahl-Hirschman Index (HHI)**, single-name/issuer exposure, realized & unrealized P&L, volatility, max drawdown, and a composite diversification score.

**3. Risk-Profile & Suitability Engine**
- Scores the investor from questionnaire responses (horizon, capacity, tolerance, experience, liquidity needs).
- Tags each product/instrument as **Suitable / Caution / Unsuitable** for *this specific investor* — the investor-protection core.

**4. Market-Data Adapter**
- Fetches live quotes, fundamentals, technicals, and news sentiment from AlphaVantage.
- Seeded fallback cache guarantees a full offline demo and resilience to rate limits.

**5. Alt-Asset Catalog + Screener**
- Curated catalog of REITs, InvITs, and corporate bonds with education content and key attributes (yield, rating, maturity, liquidity).
- Screener filters by attribute and by suitability tag.

**6. AI Advisor Service**
- Claude (Anthropic) API, retrieval-grounded on the investor's real holdings and the alt-asset knowledge base.
- Answers plain-language questions ("Am I over-concentrated in IT?") citing actual positions; never gives ungrounded advice.

---

## 4. Primary Process Flow — End to End

```
 ┌─────────┐
 │ Investor│
 └────┬────┘
      │ 1. Grants consent (AA-style)
      ▼
┌──────────────────┐    2. Read-only pull of holdings across
│ Aggregation Svc  │───────brokers / depositories / asset classes
└────────┬─────────┘
         │ normalized canonical holdings
         ▼
┌──────────────────┐    3. Enrich holdings with live prices,
│ Market-Data      │───────fundamentals, news
│ Adapter          │
└────────┬─────────┘
         │ enriched holdings
         ▼
┌──────────────────┐    4. Compute allocation, concentration (HHI),
│ Analytics Engine │───────exposure, P&L, risk metrics
└────────┬─────────┘
         │ analytics payload
         ▼
┌──────────────────┐    5. Investor completes risk questionnaire →
│ Risk-Profile &   │───────risk score & category
│ Suitability Eng. │    6. Each product tagged suitable / caution /
└────────┬─────────┘       unsuitable FOR THIS investor
         │ profile + suitability tags
         ▼
┌──────────────────┐    7. Investor explores & learns about
│ Alt-Asset        │───────REITs / InvITs / bonds, filtered by
│ Catalog + Screener│      suitability
└────────┬─────────┘
         │
         ▼
┌──────────────────┐    8. Investor asks natural-language questions;
│ AI Advisor Svc   │───────answered grounded on real portfolio +
│ (Claude API)     │       knowledge base
└────────┬─────────┘
         │
         ▼
┌──────────────────┐    9. Unified Dashboard renders holdings,
│ React Dashboard  │───────analytics, suitability, discovery, and
│                  │       advisor — one intelligent view
└──────────────────┘
```

### Step-by-step narrative

1. **Consent** — The investor grants consent through an Account Aggregator-style flow. Access is read-only; the app never holds custody.
2. **Aggregation** — The Aggregation Service pulls holdings from every linked demat/trading account and normalizes them into one canonical schema.
3. **Enrichment** — The Market-Data Adapter attaches live prices, fundamentals, and news sentiment (seeded fallback if offline).
4. **Analytics** — The Analytics Engine computes allocation, concentration (HHI), exposure, P&L, and risk metrics.
5. **Risk profiling** — The investor completes a questionnaire; the engine derives a risk score and category.
6. **Suitability** — Every instrument is tagged Suitable / Caution / Unsuitable for that investor.
7. **Discovery & education** — The Alt-Asset Explorer surfaces REITs, InvITs, and bonds, filtered by suitability, with interactive learning.
8. **AI advice** — The AI Advisor answers plain-language questions, grounded on the investor's real portfolio.
9. **Presentation** — The React dashboard renders all of the above as one cohesive, institutional-grade experience.

---

## 5. Consent & Data-Flow (Account Aggregator model)

```
Investor ──consent request──▶ Artha
   ▲                              │
   │                              │ consent artifact
   │                              ▼
   │                     Account Aggregator (AA)
   │                              │
   │        ┌─────────────────────┼─────────────────────┐
   │        ▼                     ▼                     ▼
   │   Broker A FIP          Broker B FIP        NSDL/CDSL FIP
   │   (holdings)            (holdings)          (demat holdings)
   │        │                     │                     │
   │        └─────────────────────┼─────────────────────┘
   │                              │ encrypted, consented data
   └──────────────────────────────┘
            read-only, purpose-limited, time-bound

FIP = Financial Information Provider   ·   Artha acts as FIU (Financial Information User)
```

- **Purpose-limited & time-bound:** consent specifies scope and expiry.
- **Read-only:** Artha is a Financial Information User (FIU); it never initiates transactions on custody.
- **Revocable:** the investor can withdraw consent at any time.
- **Prototype note:** in the hackathon build this flow is simulated with realistic seed portfolios; the interface is designed so a live AA connector drops in without changing downstream services.

---

## 6. Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18 + TypeScript (Vite), Recharts/D3, Tailwind CSS (light/dark, responsive) |
| **Backend** | Python + FastAPI (REST), Pydantic typed schemas |
| **Analytics** | pandas, NumPy (allocation, HHI concentration, exposure, risk metrics) |
| **Market data** | AlphaVantage APIs (quotes, fundamentals, technicals, news sentiment) + seeded fallback |
| **AI advisor** | Claude (Anthropic) API, retrieval-grounded on portfolio + knowledge base |
| **Aggregation model** | RBI Account Aggregator + SEBI-NSDL-CDSL Unified Investor Platform (simulated in prototype) |
| **Security** | Consent-driven access, token-based auth, encryption in transit/at rest, read-only aggregation |
| **Deployment** | Dockerized services; frontend on Vercel/Netlify, backend on a container host |

---

## 7. Deployment View

```
┌────────────────────┐        ┌─────────────────────┐
│  Frontend (static) │        │  Backend (container)│
│  Vercel / Netlify  │◀──────▶│  FastAPI + Uvicorn  │
│  React build       │  REST  │  Dockerized         │
└────────────────────┘        └──────────┬──────────┘
                                          │
                          ┌───────────────┼───────────────┐
                          ▼               ▼               ▼
                   AlphaVantage      Claude API      AA / Depository
                   (market data)    (AI advisor)     connectors
                                                     (prod) / seed (proto)
```

---

## 8. Security & Privacy

- **Consent-driven, read-only** access to holdings; no custody, no trade initiation on prototype scope.
- **Token-based authentication** between frontend and backend.
- **Encryption** in transit (TLS) and at rest.
- **Purpose limitation & minimization** — only data required for aggregation and analytics is requested.
- **Aggregated insights are anonymized** — any market-intelligence product uses only privacy-compliant, aggregated data.

---

## 9. Mapping to PS3 Requirements

| PS3 desired outcome | Artha component |
|---|---|
| Consolidate holdings across depositories, brokers, asset classes | Aggregation Service + Unified Dashboard |
| Risk & exposure analytics, transaction intelligence | Analytics Engine + Analytics View |
| Expand awareness of alternate instruments (REITs, InvITs, bonds) | Alt-Asset Catalog + Explorer |
| Interactive product education | Alt-Asset Explorer education content |
| Risk profiling & suitability assessment | Risk-Profile & Suitability Engine |
| Seamless multi-asset access | Screener + suitability-filtered discovery (transaction-ready design) |
| Institutional-grade experience for every retail investor | AI Advisor + the integrated whole |

---

## 10. Real vs. Simulated (prototype honesty)

| Capability | Status in prototype |
|---|---|
| Analytics engine (allocation, HHI, exposure, risk, P&L) | **Real** |
| Suitability logic | **Real** |
| Market quotes / fundamentals / news | **Real** (AlphaVantage) with seeded fallback |
| AI advisor | **Real** (Claude API) |
| Personal-holdings feed (Account Aggregator / NSDL-CDSL) | **Simulated** with realistic seed portfolios behind a production-ready interface |
