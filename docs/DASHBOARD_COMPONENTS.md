# AgroHisob CFO — Dashboard Komponentlari Texnik Hujjati

## 1. Komponentlar Ierarxiyasi

```
DashboardPage (frontend/src/app/dashboard/page.tsx)
 ├── Suspense Wrapper
 └── DashboardContent
      ├── Top Control Bar (Org Selector, Data Source Badge, Refresh)
      ├── 7-Module Navigation Tabs (overview, cashflow, forecast, debt, risks, scenarios, ai_cfo)
      ├── Module 1: Executive Overview
      │    ├── KPI Cards Grid (Total Inflows, Outflows, Net, Closing, DSCR)
      │    ├── Secondary Metrics (Lowest Cash Point, Deficit Months, Engine Version)
      │    └── CashFlowChart (ComposedChart Inflows, Outflows, Closing)
      ├── Module 2: Cash-Flow Intelligence
      │    ├── Inflow Categories Breakdown
      │    ├── Outflow Categories Breakdown
      │    └── Monthly Roll-Forward Reconciliation Table
      ├── Module 3: Seasonal Forecast Dashboard
      │    ├── Agrar Assumptions Panel (Crop, Area, Yield, Inflation, Timing)
      │    ├── Seasonality KPI Summary
      │    └── Monthly Forecast Grid (CFADS, DSCR, Buffer Breach Alerts)
      ├── Module 4: Debt & DSCR Analytics
      │    ├── Debt Overview Cards (Principal, Interest, Annual Debt Service)
      │    ├── DSCR Formula & Benchmark Bands Box
      │    └── Active Loan Amortization Schedule Table
      ├── Module 5: Financial Risk Monitor
      │    ├── Severity Summary Cards (Critical, High, Medium, Total)
      │    └── Deep-Dive Explainable Risk Cards with Trigger Rules & Responses
      ├── Module 6: Interactive Scenario Simulation
      │    ├── Scenario Presets (Base, Optimistic, Pessimistic, Custom)
      │    ├── Real-Time Sliders (Revenue Change, Cost Change, Collection Delay, Interest Delta)
      │    ├── Authoritative Backend Recalculation Trigger
      │    ├── Variance Metrics Cards (Delta Net Cash, Delta Closing, Delta DSCR)
      │    └── Stressed Scenario CashFlowChart
      └── Module 7: AI-CFO Insights Engine
           ├── Financial Health Executive Summary
           ├── Key Strategic Findings Grid
           ├── LLM Privacy-Preserving Toggle
           └── Verified Insight Cards (Evidence Bullets, Recommendations, Supporting Metrics)
```

## 2. Reaktiv Holat Boshqaruvi (State Management)

- `selectedOrgId`: Joriy tanlangan korxona IDsi (`scenario-small-farmer`, `scenario-exporter`, `scenario-cluster`).
- `activeTab`: Aktiv ochilgan modul tegi (`overview`, `cashflow`, `forecast`, `debt`, `risks`, `scenarios`, `ai_cfo`).
- `simulationResult`: Backend `/api/v1/dashboard/scenarios` orqali olingan `ScenarioComparisonResponse`.
- `llmRequested`: Maxfiy neyrotarmoq kengaytmasi so'ralganligi bayrog'i.
- `loading` va `simulating`: API so'rovlari vaqtida animatsiyalarni boshqaruvchi indikatorlar.
