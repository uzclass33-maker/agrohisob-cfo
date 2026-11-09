# AgroHisob CFO — Pre-Implementation Repository Audit

**Document Reference:** `docs/INITIAL_REPOSITORY_AUDIT.md`  
**Execution Date:** November 8, 2026 (Tashkent Time, UTC+5)  
**Auditor:** Principal Software Architect & QA Lead  
**Project:** AgroHisob CFO (AgriFinTech B2B SaaS)

---

## 1. Executive Summary

This audit assesses the state of the `agroventures` repository prior to the formal consolidation of **Assignment 1: Product Specification, System Architecture & Working Project Foundation**. The codebase was initialized as a dual-tier monorepo comprising a modern Next.js 14 frontend and a FastAPI (Python 3.12) backend. The system has been architected to address the systemic cash-flow forecasting and debt service analysis problems identified in the *AgroVentures 2026 Startup Selection Report*.

---

## 2. Current Repository Structure

The current workspace layout is clean, modular, and strictly separated:

```
agroventures/
├── .env.example                                      # Parameter configuration template
├── .gitignore                                        # Standard development ignores
├── ARCHITECTURE.md                                   # Root system architecture overview
├── DATABASE_SCHEMA.md                                # Root schema specification
├── DEVELOPMENT_ROADMAP.md                            # High-level product phases
├── README.md                                         # Project overview & running instructions
├── TESTING_CHECKLIST.md                              # QA test matrices
├── docker-compose.yml                                # Container orchestration (PostgreSQL 16)
│
├── backend/
│   ├── Dockerfile                                    # Python 3.12 runtime container
│   ├── requirements.txt                              # FastAPI, Pydantic, SQLAlchemy, NumPy, Pytest
│   ├── app/
│   │   ├── main.py                                   # FastAPI entrypoint & router registrations
│   │   ├── config.py                                 # Pydantic BaseSettings & regulatory rates
│   │   ├── api/                                      # API endpoint route modules
│   │   ├── db/                                       # Database engine & schema DDL
│   │   ├── models/                                   # SQLAlchemy ORM and Pydantic DTOs
│   │   └── services/                                 # Financial engine, scenario & synthetic data
│   └── tests/                                        # Pytest test suite (14 existing passing tests)
│
└── frontend/
    ├── Dockerfile                                    # Node 20 / Next.js production container
    ├── package.json                                  # Next 14.2.35, React 18, Tailwind, Recharts
    ├── tsconfig.json                                 # TypeScript compiler setup
    ├── next.config.js                                # Next.js rewrites & webpack aliases
    ├── tailwind.config.js                            # Agro-themed corporate design tokens
    ├── postcss.config.js                             # PostCSS build configuration
    └── src/
        ├── app/                                      # Next.js App Router pages (6 product views)
        ├── components/                               # Shared Navbar, Footer, CashFlowChart
        └── lib/                                      # Typed API client, formatters, domain types
```

---

## 3. Existing Technologies & Runtime Status

| Component | Technology | Version | Runtime Status | Health Verification |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend Runtime** | Node.js | v24.22.1 | Active | Responding on `http://localhost:3000` |
| **Frontend Framework** | Next.js (App Router) | 14.2.35 | Compiled | Prerendered static pages (`pnpm build`) |
| **Frontend Styling** | Tailwind CSS | 3.4.17 | Active | Responsive grid & corporate palette |
| **Frontend Charts** | Recharts | 3.10.1 | Active | Dynamic SVG monthly cash-flow chart |
| **Backend Runtime** | Python | 3.12.14 | Active | Responding on `http://127.0.0.1:8000` |
| **Backend Framework** | FastAPI | 0.162.2 | Active | OpenAPI Swagger at `/docs` |
| **Data Validation** | Pydantic v2 | 2.14.2 | Active | Strict typing & ConfigDict settings |
| **ORM Layer** | SQLAlchemy | 2.1.8 | Active | Relational mapping with SQLite fallback |
| **Database Engine** | PostgreSQL 16 / SQLite | 16-alpine / 3.x | Active | Auto-fallback to local `agrohisob_local.db` |
| **Package Managers** | PNPM & Pip | 11.25.0 & 26.2.2 | Verified | Zero dependency conflicts |

---

## 4. Reusable Components Identified

1. **Deterministic Financial Engine (`financial_engine.py`)**:
   - Monthly cash flow identity calculator: $\text{Closing Balance}_t = \text{Opening Balance}_t + \text{Inflows}_t - \text{Outflows}_t$.
   - Monthly roll-forward: $\text{Opening Balance}_{t+1} = \text{Closing Balance}_t$.
   - Debt Service Coverage Ratio (DSCR) calculations.
   - Liquidity deficit / cash gap identification.
   - VMQ-613 Discounted Cash Flow (DCF) agricultural land leasehold valuation model.

2. **Synthetic Agribusiness Data Portfolios (`synthetic_data.py`)**:
   - 3 verified scenarios (*Small Farmer*, *Horticulture Exporter*, *Agro-Cluster*) with 12 months of mathematically consistent inflows, outflows, and debt obligations.

3. **Frontend Application Shell**:
   - Top-level corporate navigation with Uzbekistan AgriFinTech branding.
   - Interactive composed chart component with custom tooltips (`CashFlowChart.tsx`).
   - Currency formatters (`formatUZS`, `formatCompactUZS`) handling large Uzbek Sum figures smoothly.
   - 6 fully rendered pages with error and loading boundaries.

---

## 5. Identified Gaps & Required Modifications for Full Assignment 1 Compliance

1. **Versioned REST API Endpoints**:
   - The specification calls for standardized versioned endpoints:
     - `GET /health`
     - `GET /ready`
     - `GET /api/v1/demo/organizations`
     - `GET /api/v1/demo/organizations/{id}`
     - `GET /api/v1/demo/organizations/{id}/cashflow`
   - *Action*: Expose these exact v1 endpoints alongside existing endpoints in `app/main.py`.

2. **Strict Python `Decimal` Currency Calculations**:
   - Financial applications require precision without IEEE 754 floating point imprecision.
   - *Action*: Add explicit `Decimal` calculation methods and dedicated precision tests (Test A through E).

3. **Multi-Tenancy Database Model Refinements**:
   - Addition of `organization_memberships` table and explicit fields (`organization_type`, `base_currency`, `is_demo`) in `core.py`.
   - Setup Alembic migration baseline.

4. **Centralized Localization (`locales/uz.ts`)**:
   - Centralize UI copy into a dedicated localization structure to support future multilingual expansion (Uzbek Cyrillic, Russian, English).

5. **Formal Documentation Suite**:
   - Create all 10 requested documents in `docs/` with complete architectural, testing, security, and PRD specifications.

---

## 6. Technical Risks & Mitigation Strategies

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **PostgreSQL Unavailable Locally** | High | Implemented resilient auto-fallback to SQLite for local developer velocity; PostgreSQL connection remains primary for Docker/production. |
| **Floating Point Inaccuracies** | High | Strict use of Python `Decimal` with quantized monetary precision for cash-flow accounting. |
| **SSR Hydration Mismatch** | Medium | Client-side mounting flags (`mounted`) implemented in Recharts wrapper; Next.js dynamic suspense boundaries in place. |
| **Premature External Integrations** | High | Clear boundaries: bank APIs (IABS), Soliq APIs, satellite imagery, and external LLMs are strictly deferred to subsequent phases. |

---

## 7. Architectural Decisions & Justification

1. **Modular Monolith over Microservices**: Given the Pre-Seed / MVP status of the venture, a modular monolith minimizes network overhead, deployment complexity, and synchronization errors while preserving clean domain boundaries.
2. **FastAPI for Computation**: FastAPI delivers high-performance asynchronous request handling paired with automatic OpenAPI documentation and strict Pydantic validation.
3. **Next.js 14 App Router**: Provides server-rendered performance, clean routing hierarchies, and instant mobile responsiveness.
