# AgroHisob CFO — User Flows & Operational Journeys

**Document Reference:** `docs/USER_FLOWS.md`  
**Author:** UI/UX Product Designer & Systems QA Specialist  
**Language:** English (Technical Documentation)

---

## 1. Primary User Journey (Unauthenticated Demo Flow)

The primary goal of Assignment 1 is to allow any agricultural founder, bank loan officer, or prospective client to explore AgroHisob CFO immediately without friction.

```mermaid
sequenceDiagram
    autonumber
    actor User as Agribusiness User / Banker
    participant UI as Next.js 14 Frontend
    participant API as FastAPI Backend Gateway
    participant Engine as Financial Engine (Decimal)
    participant Store as Scenario Data Store

    User->>UI: Visits Landing Page (/)
    User->>UI: Clicks "Demoni sinab ko‘rish"
    UI->>API: GET /api/v1/demo/organizations
    API->>Store: Retrieve 3 synthetic profiles
    Store-->>API: Profiles list (Small Farmer, Exporter, Cluster)
    API-->>UI: 200 OK [JSON metadata]
    UI-->>User: Renders Demo Selector (/demo)

    User->>UI: Selects "Andijon Baraka Fermer Xo'jaligi"
    UI->>UI: Navigates to /dashboard?scenario=scenario-small-farmer
    UI->>API: GET /api/v1/demo/organizations/{id}/cashflow
    API->>Store: Load 12-month synthetic transactions & opening cash
    Store-->>API: Raw monthly datasets & debt schedule
    API->>Engine: execute calculate_12m_cash_flow(...)
    Note over Engine: Closing = Opening + Inflows - Outflows<br/>Roll-forward: Opening(t+1) = Closing(t)<br/>Calculate DSCR & deficit months
    Engine-->>API: Reconciled Financial Summary
    API-->>UI: 200 OK [Calculated Results JSON]
    UI-->>User: Displays KPI Cards, Recharts Cash-Flow Graph & Ledger Table

    opt Exploration of Advanced Capabilities
        User->>UI: Clicks "Stress-Test"
        UI-->>User: Renders /scenario-analysis with interactive sliders
        User->>UI: Clicks "Kredit Dosyesi"
        UI-->>User: Renders /credit-report with DSCR & VMQ-613 evaluation
    end
```

---

## 2. Future Authenticated Enterprise User Journey

In subsequent phases (Assignments 2–3), enterprise users will authenticate, create organization tenancies, upload live Soliq E-faktura files, and manage team access.

```mermaid
flowchart TD
    A["User Registration / Login (OneID or Phone + SMS OTP)"] --> B["Select or Create Organization Tenancy"]
    B --> C["Assign RBAC Roles (Owner, Accountant, CFO, Auditor)"]
    C --> D["Upload Soliq E-Faktura (XLSX/XML) & Bank CSV"]
    D --> E["Smart Parser (MXIK/IKPU Agronomic Classification)"]
    E --> F["Review & Verify Categorized Transactions"]
    F --> G["Deterministic 12M Cash Flow & DSCR Engine"]
    G --> H["Monte-Carlo Sensitivity Simulation (±20% Shocks)"]
    H --> I["VMQ-613 Leasehold Land Collateral DCF Model"]
    I --> J["Generate Bank-Ready Credit Dossier (PDF & XLSX)"]
    J --> K["Submit via Pre-Underwriting Bridge to Partner Banks"]
```

---

## 3. Financial Data Processing Pipeline

```mermaid
flowchart LR
    subgraph Inputs ["Input Ledger Data"]
        In1["Opening Cash Balance (UZS)"]
        In2["Monthly Cash Receipts (Inflows)"]
        In3["Monthly Operating Expenses (Outflows)"]
        In4["Contractual Debt Amortization"]
    end

    subgraph Computation ["Pure Python Decimal Engine"]
        Step1["Compute Inflows Sum per Month"]
        Step2["Compute Operating Outflows per Month"]
        Step3["Net Cash Flow = Inflows - Outflows"]
        Step4["Closing Cash = Opening + Net Cash Flow"]
        Step5["Roll Forward: Opening(t+1) = Closing(t)"]
        Step6["Operating Cash Flow = Inflows - NonDebtOutflows"]
        Step7["Annual DSCR = Operating Cash / Debt Service"]
        Step8["Flag Deficit if Closing < 0"]
    end

    subgraph Verification ["Reconciliation & Invariant Check"]
        Check1{"Closing == Opening + In - Out?"}
        Check2{"Annual Final == Initial + TotalIn - TotalOut?"}
    end

    subgraph Output ["Structured Output Payload"]
        Out1["Reconciliation Status: Reconciled (100% Match)"]
        Out2["12 Monthly Breakdown Objects"]
        Out3["Annual Aggregations & DSCR Rating"]
    end

    In1 & In2 & In3 & In4 --> Step1 & Step2
    Step1 & Step2 --> Step3 --> Step4 --> Step5 --> Step6 --> Step7 --> Step8
    Step4 & Step5 --> Check1
    Step8 --> Check2
    Check1 -- Yes --> Out1
    Check2 -- Yes --> Out2 & Out3
```

---

## 4. Error Scenarios & Defensive Fallback Matrix

AgroHisob CFO enforces a strict rule: **Never silently substitute fake successful data when a backend request fails.**

```mermaid
flowchart TD
    Request["Frontend API Request"] --> Gateway{"Backend Gateway Reachable?"}
    Gateway -- No (Network / 502 / 504) --> Err1["Display Error Alert in Uzbek:<br/>'Backend bilan aloqa yo'q. Server ishga tushirilganligini tekshiring.'<br/>Provide retry button."]
    Gateway -- Yes --> Endpoint{"Requested Scenario Found?"}
    Endpoint -- No (404) --> Err2["Display 404 Alert:<br/>'Ssenariy topilmadi.'<br/>Offer fallback to Small Farmer demo."]
    Endpoint -- Yes --> Validate{"Payload Structurally Valid?"}
    Validate -- No (422) --> Err3["Display 422 Validation Error:<br/>Specific parameter error message."]
    Validate -- Yes --> Calc{"Calculation Succeeded?"}
    Calc -- Discrepancy Detected --> Err4["Flag Discrepancy:<br/>'Reconciliation discrepancy detected.'<br/>Display audit warning."]
    Calc -- Success --> Render["Render Reconciled Financial Dashboard"]
```

### Detailed Failure Handling Table:

| Error Case | Trigger Condition | Backend HTTP Status | Frontend User Experience |
| :--- | :--- | :--- | :--- |
| **Backend Offline** | FastAPI server stopped or network cut off | Network Error (Failed to fetch) | Displays clear red alert: *"Backend bilan aloqa o'rnatilmadi. Iltimos FastAPI serveri ishlayotganligini tekshiring."* |
| **Invalid Scenario ID** | User enters `/dashboard?scenario=unknown-id` | `404 Not Found` | Renders clear error message with available scenario links. |
| **Malformed Parameter** | Negative initial balance or shock $>50\%$ | `422 Unprocessable Entity` | Form highlights the specific field with boundary constraints. |
| **Reconciliation Discrepancy** | Inflows/outflows don't equal closing balance | `200 OK` (flagged in payload) | Prominently displays *"Reconciliation discrepancy detected"* banner in red. |
| **Zero Debt Organization** | Farm has zero loans | `200 OK` | DSCR shows *"Qarzsiz (99.99x)"* without dividing by zero. |
| **Loading Latency** | Network delay during heavy calculations | Pending Promise | Shows animated spinner with text *"FastAPI Moliyaviy Yadrosida 12 Oylik Balans Hisoblanmoqda..."* |
