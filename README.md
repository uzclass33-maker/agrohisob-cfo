# AgroHisob CFO — AgriFinTech B2B SaaS for Uzbekistan

> **AgroVentures 2026 Corporate Accelerator Selection**: #1 Winning Startup Idea (91.5 / 100 Weighted Score)  
> Designed for Agro-Clusters, Horticulture Exporters, Commercial Farmers, and ATB «Agrobank» Pre-Underwriting.

---

## 1. Executive Summary

In Uzbekistan's $24.3B agricultural economy, over **91,775 commercial farmers**, **633 agro-industrial clusters**, and **34,283 agro-SMEs** face acute working capital bottlenecks:
* Traditional accounting software (1C, Soliq.uz) operates retrospectively for tax compliance, failing to forecast seasonal liquidity gaps (*kassa uzilishi*). Between 2022 and 2025, 19 cotton/textile clusters collapsed into insolvency due to unmanaged cash-flow mismatches.
* Despite **Cabinet of Ministers Resolution No. 613 (VMQ-613, Sept 30, 2025)** authorizing the pledge of agricultural land lease rights for bank loans, 57% of Agrobank loan collateral remains tied up in urban real estate due to the lack of an automated discounted cash flow (DCF) valuation tool.
* Preparing bank credit dossiers currently takes businesses 3–6 weeks and costs $500–$3,000 in consulting fees.

**AgroHisob CFO** solves this by providing a unified financial intelligence layer: it ingests electronic invoices (Soliq E-faktura) and bank statements, calculates a deterministic 12-month seasonal cash flow, tracks Debt Service Coverage Ratios (DSCR), calculates VMQ-613 land lease collateral values, and compiles an audit-ready **Bank Credit Dossier in under 3 minutes**.

---

## 2. Core Features (Assignment 1 Scope)

1. **Deterministic 12-Month Cash-Flow Engine**:
   - Enforces the fundamental cash flow identity across all periods:
     $$\text{Closing Balance}_t = \text{Opening Balance}_t + \text{Inflows}_t - \text{Outflows}_t$$
   - Automatic roll-forward continuity ($\text{Opening}_{t+1} = \text{Closing}_t$).
   - Real-time liquidity deficit / cash-flow gap detection.
2. **Dynamic Debt Service Coverage Ratio (DSCR)**:
   - Evaluates whether operating cash flow safely covers bank debt obligations.
   - Categorized by commercial bank underwriting tiers (*A'lo*, *Barqaror*, *Kuzatuvda*, *Kritik*).
3. **VMQ-613 Leasehold Collateral Valuation**:
   - Calculates present value (DCF) of land lease rights using soil bonitet scores, regional normative productivity, and regulatory 65% LTV haircuts.
4. **Interactive Sensitivity & Stress-Testing**:
   - Dynamic simulation of biological yield shocks (±30%), commodity market price drops (±30%), input cost inflation (0–50%), and interest rate adjustments (10% state preferential to 23.5% commercial rate).
5. **Smart Data Import Preview**:
   - Ingestion interface for Soliq E-faktura (Excel/XML) and Bank CSV exports.
   - Automated mapping to official Uzbekistan MXIK (IKPU) product categories (seeds, fertilizers, diesel fuel, wages, water tax).
   - **Zero-Retention Mode** ensuring compliance with Law O‘RQ-547 ("On Personal Data").
6. **3 Synthetic Agribusiness Benchmark Portfolios**:
   - Small Family Farmer (*Andijon Baraka Fermer Xo'jaligi* — 65 ha cotton & vegetables).
   - Horticulture Exporter (*«Samarqand Agro Eksport» MChJ* — 120 ha table grapes/cherries + 1,000t cold storage).
   - Vertically Integrated Cluster (*«Qashqadaryo Paxta-G'alla Klasteri»* — 2,500 ha cotton/wheat cluster).

---

## 3. Technology Stack & Architecture

* **Frontend**: Next.js 14 (App Router, TypeScript, React 18), Tailwind CSS, Recharts (responsive financial charts), Lucide React.
* **Backend**: Python 3.12, FastAPI, Pydantic v2 (Settings & DTOs), SQLAlchemy 2.0, NumPy, Pandas.
* **Database**: PostgreSQL 16 (Enterprise DDL with ENUMs and mathematical check constraints) + seamless local SQLite fallback for developer autonomy.
* **DevOps / Orchestration**: Docker, Docker Compose, Uvicorn, PNPM.

---

## 4. Repository Structure

```
agroventures/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI entrypoint, CORS, router mounts
│   │   ├── config.py                  # Pydantic BaseSettings, regulatory constants
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── core.py                # 9 SQLAlchemy ORM entities
│   │   │   └── schemas.py             # Pydantic request/response validation schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── financial_engine.py    # 12M cash flow & VMQ-613 DCF valuation engine
│   │   │   ├── scenario_engine.py     # Sensitivity & stress-test simulation engine
│   │   │   └── synthetic_data.py      # 3 consistent synthetic agribusiness datasets
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes_scenarios.py    # GET /api/scenarios endpoints
│   │   │   ├── routes_financials.py   # POST /api/financials/calculate & stress-test
│   │   │   └── routes_reports.py      # GET /api/reports/credit-readiness/:id
│   │   └── db/
│   │       ├── __init__.py
│   │       ├── database.py            # PostgreSQL engine with auto SQLite fallback
│   │       └── schema.sql             # Full PostgreSQL DDL specification
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_financial_engine.py   # Cash flow identities, DSCR, VMQ-613 tests
│   │   ├── test_scenarios.py          # Synthetic dataset integrity & deficit tests
│   │   └── test_api.py                # Live FastAPI endpoint & error handling tests
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx             # Root layout with responsive Navbar & Footer
│   │   │   ├── page.tsx               # Landing page with market statistics
│   │   │   ├── demo/page.tsx          # Scenario selector with 3 synthetic cases
│   │   │   ├── dashboard/page.tsx     # Financial dashboard & 12M cash flow table
│   │   │   ├── data-import/page.tsx   # Soliq E-faktura & bank ingestion UI
│   │   │   ├── scenario-analysis/     # Stress-test simulation with interactive sliders
│   │   │   └── credit-report/         # Bank pre-underwriting credit scorecard
│   │   ├── components/
│   │   │   ├── Navbar.tsx             # Main navigation header
│   │   │   ├── Footer.tsx             # Footer with regulatory references
│   │   │   └── CashFlowChart.tsx      # Recharts monthly cash-flow visualization
│   │   └── lib/
│   │       ├── api.ts                 # Typed fetch client
│   │       ├── formatters.ts          # UZS currency and percentage formatters
│   │       └── types.ts               # Shared TypeScript domain interfaces
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── next.config.js
│   └── Dockerfile
│
├── README.md                          # Main project guide
├── ARCHITECTURE.md                    # Technical & FinTech architecture blueprint
├── DATABASE_SCHEMA.md                 # Relational ERD & data dictionary
├── DEVELOPMENT_ROADMAP.md             # Development roadmap (Assignments 1 & 2, Pilot)
├── TESTING_CHECKLIST.md               # QA verification matrix & test results
├── .env.example                       # Environment configuration template
└── docker-compose.yml                 # Multi-container orchestration (PostgreSQL + App)
```

---

## 5. Quickstart & How to Run

### Prerequisites
* Python 3.11+
* Node.js 18+ (Node 20+ recommended) and `pnpm` (or `npm`)

### 1. Environment Setup
Create a `.env` file from the example:
```bash
cp .env.example .env
```

### 2. Backend Setup & Startup
Install Python dependencies and run the FastAPI server:
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
* Interactive API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`
* Health Check Endpoint: `http://127.0.0.1:8000/api/health`

### 3. Frontend Setup & Startup
In a separate terminal, install packages and start the Next.js server:
```bash
cd frontend
pnpm install
pnpm build
pnpm start -p 3000
# Or for live hot-reload development:
# pnpm dev
```
Open your browser and visit: `http://localhost:3000`

### 4. Running via Docker Compose
To spin up the entire stack including PostgreSQL 16:
```bash
docker-compose up --build
```

---

## 6. Running Automated Tests

AgroHisob CFO includes an automated test suite verifying mathematical consistency, debt service coverage, and endpoint error handling:
```bash
cd backend
python -m pytest -v
```

All 14 tests pass with zero discrepancies:
* `test_monthly_cash_flow_identity_rule`: Verifies $Closing_t = Opening_t + Inflow_t - Outflow_t$ for all months.
* `test_dscr_calculation_and_benchmarks`: Verifies DSCR formula and coverage ratings.
* `test_vmq613_valuation_formula`: Verifies leasehold DCF and 65% LTV bankable haircut.
* `test_three_synthetic_scenarios_exist_and_labeled`: Verifies presence and explicit synthetic labeling.
* `test_all_scenarios_internal_consistency`: Verifies zero reconciliation discrepancy across all synthetic scenarios.
* `test_small_farmer_seasonality_and_deficit_detection`: Verifies spring cash-flow deficit identification.
* `test_api_*`: Verifies all REST endpoints and invalid payload rejections (404, 422).

---

## 7. Product Pages Guide

1. **Landing Page (`/`)**: Overview of the platform, Uzbekistan agricultural market realities (91.7k farmers, 56.2 trln UZS Agrobank credit plan, 19 bankrupt clusters), and direct call-to-actions.
2. **Demo Ssenariylar (`/demo`)**: Interactive selector between the 3 synthetic business types with key indicators and quick navigation links.
3. **Moliya Paneli (`/dashboard`)**: The primary vertical slice view showing active business switching, 6 KPI cards, the dynamic Recharts cash-flow chart, and the 12-month reconciled financial ledger.
4. **Faktura & Data Yuklash (`/data-import`)**: Upload interface for Soliq E-faktura and bank statements with simulated smart MXIK (IKPU) categorization and Zero-Retention security toggle.
5. **Ssenariy & Stress-Test (`/scenario-analysis`)**: Interactive sensitivity testing allowing users to simulate yield (-30% to +30%), price, and cost shocks in real time.
6. **Kreditga Tayyorgarlik (`/credit-report`)**: Formal bank pre-underwriting dossier with credit scorecard, DSCR evaluation, additional debt capacity, and VMQ-613 leasehold collateral calculation.

---

## 8. Compliance & Constraints Notice

* **No Direct Bank/Soliq APIs Yet**: In strict accordance with Assignment 1 scope, bank core banking (IABS) and direct Soliq API integrations are omitted; document ingestion is performed via synthetic/file structures.
* **No External LLM Privacy Risk**: No sensitive customer financial data is transmitted to external artificial intelligence APIs.
* **Explicit Synthetic Status**: All demo figures are explicitly identified as hypothetical benchmarks for demonstration and evaluation purposes.
