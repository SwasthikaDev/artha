# UnifyInvest — SEBI GFF Hackathon Submission

**Problem Statement 3:** Super App for Unified Multi-Asset Investing and Awareness for Retail Investors

---

## Project Title *

**UnifyInvest — The Unified Multi-Asset Super App for India's Retail Investors**

---

## Team Members — Name & Organization (if any) *

*(Replace with your actual team details.)*

- Swasthika Devadiga — [Your college / organization] — Team Lead & Full-Stack Developer
- [Member 2 Name] — [Organization] — [Role]
- [Member 3 Name] — [Organization] — [Role]
- [Member 4 Name] — [Organization] — [Role]

---

## Brief Description of the Idea *

UnifyInvest is a secure, unified investment super app that solves the two compounding problems facing India's retail investors: **portfolio fragmentation** and **low awareness of alternate assets**.

Today an investor's holdings are scattered across multiple demat and trading accounts, depositories (NSDL/CDSL), and asset classes — with no single view of total holdings, exposure, or risk. At the same time, retail participation is dangerously skewed toward equities, with poor understanding of instruments like REITs, InvITs, and corporate bonds.

UnifyInvest brings both sides together in one intelligent dashboard. It **consolidates holdings across brokers, depositories, and asset classes** (modeled on the RBI Account Aggregator framework and the SEBI-NSDL-CDSL Unified Investor Platform), layers on **institutional-grade risk and exposure analytics**, and pairs this with **interactive product education, risk profiling, and a suitability engine** that helps investors safely discover and assess alternate assets. An **AI advisor**, grounded on the investor's own portfolio, answers plain-language questions like *"Am I over-concentrated in IT stocks?"* — delivering the kind of portfolio intelligence previously reserved for institutional and HNI investors, reimagined for every retail participant in India's securities markets.

---

## Proposed Solution — Business Model / Commercial Potential

**Product:** A cross-platform investor super app (web + mobile) with five integrated pillars: (1) unified portfolio aggregation, (2) risk & exposure analytics, (3) risk-profiling + product suitability engine, (4) alternate-asset education & discovery, and (5) an AI portfolio advisor.

**Business model (multi-layered, SEBI-aligned):**

- **Freemium (B2C):** Free core aggregation + analytics to drive mass adoption; premium tier (₹199–499/month) for advanced analytics, tax-loss harvesting, goal planning, and unlimited AI advisor queries.
- **B2B2C / white-label:** License the aggregation + analytics engine to brokers, wealth-management platforms, and banks that lack a unified multi-asset view.
- **Distribution revenue:** Regulated commissions / referral fees on alternate-asset transactions (REITs, InvITs, bonds) executed through partner RTAs / exchanges — expanding an under-served market rather than churning equities.
- **Data insights (aggregated & anonymized):** Privacy-compliant market-participation intelligence for issuers and market infrastructure institutions.

**Market & impact:** 15+ crore demat accounts in India and growing, with alternate-asset penetration in low single digits — a large, under-tapped TAM. The product directly furthers SEBI's investor-protection and financial-inclusion mandate, making it a natural fit for a regulatory sandbox and MII partnerships.

---

## Technology Stack Details

- **Frontend:** React 18 + TypeScript (Vite), Recharts / D3 for analytics visualizations, Tailwind CSS for a responsive, accessible dashboard (light/dark themes).
- **Backend:** Python + FastAPI (REST), Pydantic for typed schemas, modular services (aggregation, analytics, suitability, market-data, AI advisor).
- **Analytics engine:** pandas / NumPy for allocation, concentration (Herfindahl-Hirschman Index), sector & asset-class exposure, P&L, and risk metrics (volatility, drawdown, diversification score).
- **Market data:** AlphaVantage APIs for live quotes, fundamentals, technicals, and news sentiment, with a seeded fallback for offline demos.
- **AI advisor:** Claude (Anthropic) API — retrieval-grounded on the user's own portfolio and the alt-asset knowledge base, so answers are personalized and cite real holdings.
- **Data aggregation layer:** Modeled on the RBI **Account Aggregator** framework and the **SEBI-NSDL-CDSL Unified Investor Platform**, with consent-based data flows (simulated with realistic seed portfolios for the prototype).
- **Security:** Consent-driven data access, token-based auth, encryption in transit / at rest, read-only aggregation (no custody of assets).
- **Deployment:** Dockerized services; frontend on Vercel / Netlify, backend on a container host.

---

## Process Flow / Architecture

### High-level architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     REACT + TYPESCRIPT UI                      │
│  Unified Dashboard · Analytics · Risk Profiler · Alt-Asset     │
│  Explorer · AI Advisor Chat                                    │
└───────────────────────────────┬──────────────────────────────┘
                                 │  HTTPS / REST
┌───────────────────────────────▼──────────────────────────────┐
│                      FASTAPI  BACKEND                          │
│                                                                │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐  │
│  │  Aggregation  │  │  Analytics    │  │  Suitability &     │  │
│  │  Service      │  │  Engine       │  │  Risk-Profile      │  │
│  │ (AA / NSDL-   │  │ (allocation,  │  │  Engine            │  │
│  │  CDSL model)  │  │  HHI, risk)   │  │                    │  │
│  └───────┬───────┘  └───────┬───────┘  └─────────┬─────────┘  │
│          │                  │                    │            │
│  ┌───────▼───────┐  ┌───────▼───────┐  ┌─────────▼─────────┐  │
│  │  Market-Data  │  │  Alt-Asset    │  │  AI Advisor       │  │
│  │  Adapter      │  │  Catalog +    │  │  (Claude API,     │  │
│  │ (AlphaVantage)│  │  Screener     │  │  portfolio-       │  │
│  └───────────────┘  └───────────────┘  │  grounded)        │  │
│                                         └───────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### Process flow (end to end)

```
1. Investor grants consent (Account Aggregator-style) → read-only access.
2. Aggregation Service pulls holdings across brokers / depositories /
   asset classes and normalizes them into one canonical schema.
3. Market-Data Adapter enriches holdings with live prices, fundamentals,
   and news (seeded fallback if offline).
4. Analytics Engine computes allocation, concentration (HHI), exposure,
   P&L, and risk metrics.
5. Investor completes a risk questionnaire → risk score & category.
6. Suitability Engine tags each product as suitable / caution /
   unsuitable FOR THIS investor.
7. Alt-Asset Explorer lets the investor discover & learn about
   REITs / InvITs / bonds, filtered by suitability.
8. AI Advisor answers natural-language questions grounded on the
   investor's real portfolio + knowledge base.
9. Unified Dashboard renders holdings, analytics, suitability,
   discovery, and advisor as one intelligent view.
```

> Full detail — component responsibilities, consent/data-flow diagram, deployment view, security model, and PS3 requirement mapping — is documented in [`docs/ARCHITECTURE.md`](ARCHITECTURE.md).

---

## Upload Your Idea Deck

*To be attached — pitch deck (PDF).*
*(Status: idea deck to be generated / exported before submission.)*

---

## Demo Video Link (maximum 3 minutes)

*To be added — record a ≤3-minute walkthrough of the working prototype.*

`https://` *(paste link here)*

---

## GitHub Repository Link (if any)

**https://github.com/SwasthikaDev/artha**
