# AgroHisob CFO — Testing & Quality Assurance Checklist

## 1. Testing Philosophy & Verification Standards

In AgriFinTech systems, computational errors directly impact bank credit decisions, solvency assessments, and farmer livelihood. AgroHisob CFO follows a strict financial QA framework:
* **Zero Discrepancy Tolerance**: Cash balances across any period must reconcile to the exact cent/tiyin.
* **Deterministic Double-Entry Integrity**: Closing balance of month $t$ must equal opening balance of month $t+1$.
* **Boundary & Error Resistance**: Invalid, negative, or incomplete inputs must fail gracefully with descriptive 404 or 422 HTTP responses.

---

## 2. Automated Test Results (14 / 14 Passed)

The automated test suite in `backend/tests/` can be executed using:
```bash
cd backend
python -m pytest -v
```

### Execution Log Summary:
```
============================= test session starts =============================
platform win32 -- Python 3.12.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\lenovo\Desktop\agroventures\backend
collected 14 items

tests/test_api.py::test_api_health PASSED                                [  7%]
tests/test_api.py::test_list_scenarios_api PASSED                        [ 14%]
tests/test_api.py::test_get_scenario_details_api PASSED                  [ 21%]
tests/test_api.py::test_get_nonexistent_scenario_404 PASSED              [ 28%]
tests/test_api.py::test_calculate_financials_api PASSED                  [ 35%]
tests/test_api.py::test_calculate_invalid_request_422 PASSED             [ 42%]
tests/test_api.py::test_stress_test_api PASSED                           [ 50%]
tests/test_api.py::test_credit_readiness_report_api PASSED               [ 57%]
tests/test_financial_engine.py::test_monthly_cash_flow_identity_rule PASSED [ 64%]
tests/test_financial_engine.py::test_dscr_calculation_and_benchmarks PASSED [ 71%]
tests/test_financial_engine.py::test_vmq613_valuation_formula PASSED     [ 78%]
tests/test_scenarios.py::test_three_synthetic_scenarios_exist_and_labeled PASSED [ 85%]
tests/test_scenarios.py::test_all_scenarios_internal_consistency PASSED  [ 92%]
tests/test_scenarios.py::test_small_farmer_seasonality_and_deficit_detection PASSED [100%]

======================== 14 passed, 1 warning in 1.27s ========================
```

---

## 3. Comprehensive Verification Matrix

| Category | Test Case Description | Verification Method | Status |
| :--- | :--- | :--- | :--- |
| **Financial Engine** | Monthly Closing Balance Identity: $Closing_t = Opening_t + Inflow_t - Outflow_t$ | `test_monthly_cash_flow_identity_rule` | **PASSED** |
| **Financial Engine** | Roll-forward consistency: $Opening_{t+1} == Closing_t$ across all 12 months | `test_monthly_cash_flow_identity_rule` | **PASSED** |
| **Financial Engine** | Overall 12-month reconciliation: $FinalClosing == InitialOpening + \sum Inflow - \sum Outflow$ | `test_monthly_cash_flow_identity_rule` | **PASSED** |
| **Financial Engine** | DSCR ratio computation & division-by-zero safeguarding | `test_dscr_calculation_and_benchmarks` | **PASSED** |
| **Financial Engine** | VMQ-613 DCF land leasehold formula validation with 65% LTV haircut | `test_vmq613_valuation_formula` | **PASSED** |
| **Synthetic Data** | 3 required scenarios exist: Small Farmer, Exporter, Cluster | `test_three_synthetic_scenarios_exist_and_labeled` | **PASSED** |
| **Synthetic Data** | Synthetic disclaimer flag explicitly `true` for all models | `test_three_synthetic_scenarios_exist_and_labeled` | **PASSED** |
| **Synthetic Data** | Internal consistency check for all 3 scenarios (zero discrepancy) | `test_all_scenarios_internal_consistency` | **PASSED** |
| **Synthetic Data** | Small farmer spring cash-flow deficit detection (April/May) | `test_small_farmer_seasonality_and_deficit_detection` | **PASSED** |
| **API Endpoints** | Health check `GET /api/health` returns 200 and healthy status | `test_api_health` | **PASSED** |
| **API Endpoints** | Scenario list `GET /api/scenarios` returns 3 scenario metadata objects | `test_list_scenarios_api` | **PASSED** |
| **API Endpoints** | Scenario details `GET /api/scenarios/{id}` returns complete data | `test_get_scenario_details_api` | **PASSED** |
| **API Endpoints** | Non-existent scenario lookup returns HTTP 404 with clear Uzbek message | `test_get_nonexistent_scenario_404` | **PASSED** |
| **API Endpoints** | Calculation endpoint `POST /api/financials/calculate` verifies reconciliation | `test_calculate_financials_api` | **PASSED** |
| **API Endpoints** | Invalid calculation payload (e.g. negative balance) returns HTTP 422 | `test_calculate_invalid_request_422` | **PASSED** |
| **API Endpoints** | Stress-test endpoint `POST /api/financials/stress-test` applies shocks | `test_stress_test_api` | **PASSED** |
| **API Endpoints** | Credit scorecard endpoint `GET /api/reports/credit-readiness/{id}` | `test_credit_readiness_report_api` | **PASSED** |
| **Frontend UI** | Next.js 14 production build (`pnpm build`) compiles 9 static routes | Next.js Build Worker | **PASSED** |
| **Frontend UI** | Client `useSearchParams` wrapped in `<Suspense>` boundaries | Next.js Prerender Engine | **PASSED** |
| **Frontend UI** | Recharts responsive cash-flow graph rendered on Dashboard | Component Render Test | **PASSED** |
| **Integration** | Frontend server (Port 3000) communicates with FastAPI backend (Port 8000) | Live HTTP Interop Test | **PASSED** |

---

## 4. Manual QA Smoke Test Procedure

1. **Start Backend**:
   ```bash
   python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
   ```
   *Verify*: Visit `http://127.0.0.1:8000/api/health` — should return `{"status": "healthy"}`.

2. **Start Frontend**:
   ```bash
   cd frontend
   pnpm start -p 3000
   # or for development: pnpm dev
   ```
   *Verify*: Visit `http://127.0.0.1:3000` — Landing page renders with macroeconomic statistics.

3. **Execute Vertical Slice**:
   - Navigate to `/demo` -> Select **"Andijon Baraka Fermer Xo'jaligi"**.
   - Click **"Moliya Panelida Tahlil Qilish"**.
   - Confirm Dashboard displays:
     - Boshlang'ich Kassa: **45 mln so'm**
     - Yillik Yalpi Tushum: **1.12 mlrd so'm**
     - Yillik Jami Xarajat: **978.5 mln so'm**
     - Qarz Qoplami (DSCR): **2.14x — A'lo**
     - Kassa Uzilishi: **Aprel va May oylarida defitsit** (Negative net cash flow correctly flagged).
     - Reconciliation Banner: **"Deterministik Moliya Balansi Reconciled: 100% Mos"**.
   - Navigate to `/scenario-analysis` -> Move Yield slider to `-20%` -> Observe updated DSCR and solvency alert.
   - Navigate to `/credit-report` -> Confirm borrower rating tier and VMQ-613 collateral calculation.
