# AgroHisob CFO — Relational Database Architecture

**Document Reference:** `docs/DATABASE_SCHEMA.md`  
**Author:** PostgreSQL Database Architect & Security Engineer  
**Database Engine:** PostgreSQL 16 (with SQLite 3 local fallback)

---

## 1. Architectural Overview

The AgroHisob CFO database schema is designed for multi-tenant B2B financial software. It enforces strict relational integrity, organization-level isolation, and immutable auditability for financial transactions and pre-underwriting reports.

### Structural Tenets:
* **UUID Primary Keys**: Eliminates enumeration vulnerabilities and enables offline ID generation.
* **DECIMAL/NUMERIC for Monetary Types**: All financial values use `NUMERIC(18, 2)` to eliminate floating-point rounding errors.
* **Strict Check Constraints**: Core double-entry identity is verified at the database level:
  `CHECK (closing_balance = opening_balance + total_inflows - total_outflows)`.
* **Explicit Foreign Key Cascades**: Child entities cascade deletion safely, while uploaded files and audit reports use `SET NULL` on user deletion to preserve compliance history.

---

## 2. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ ORGANIZATION_MEMBERSHIPS : "has members"
    ORGANIZATIONS ||--o{ USERS : "associated with"
    ORGANIZATIONS ||--o{ FINANCIAL_PERIODS : "tracks"
    ORGANIZATIONS ||--o{ TRANSACTIONS : "incurs"
    ORGANIZATIONS ||--o{ DEBT_OBLIGATIONS : "services"
    ORGANIZATIONS ||--o{ IMPORT_RECORDS : "uploads"
    ORGANIZATIONS ||--o{ FINANCIAL_FORECASTS : "simulates"
    ORGANIZATIONS ||--o{ GENERATED_REPORTS : "generates"

    USERS ||--o{ ORGANIZATION_MEMBERSHIPS : "holds role in"
    USERS ||--o{ IMPORT_RECORDS : "uploads"
    USERS ||--o{ GENERATED_REPORTS : "creates"

    FINANCIAL_PERIODS ||--o{ TRANSACTIONS : "contains"
    IMPORT_RECORDS ||--o{ TRANSACTIONS : "originates"

    ORGANIZATIONS {
        uuid id PK
        string name
        string organization_type "farmer, exporter, cluster, sme"
        string inn UK "9-digit STIR"
        string region
        string district
        string base_currency "UZS"
        boolean is_demo
        decimal land_hectares
        string cadastre_number
        int soil_bonitet_score
        string main_crop_type
        boolean has_drip_irrigation
        boolean has_cold_storage
        timestamp created_at
        timestamp updated_at
    }

    USERS {
        uuid id PK
        string email UK
        string full_name
        string phone_number
        string hashed_password
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    ORGANIZATION_MEMBERSHIPS {
        uuid id PK
        uuid organization_id FK
        uuid user_id FK
        string role "owner, admin, accountant, finance_manager, viewer"
        timestamp created_at
    }

    FINANCIAL_PERIODS {
        uuid id PK
        uuid organization_id FK
        date period_start
        date period_end
        int fiscal_year
        int month_number "1..12"
        decimal opening_cash_balance
        decimal total_inflows
        decimal total_outflows
        decimal closing_balance
        string currency "UZS"
        string status "OPEN, CLOSED, RECONCILED"
        timestamp created_at
    }

    TRANSACTIONS {
        uuid id PK
        uuid organization_id FK
        uuid period_id FK
        uuid import_record_id FK
        date transaction_date
        string direction "INFLOW, OUTFLOW"
        decimal amount "CHECK > 0"
        string currency "UZS"
        string category "CROP_SALES, SEEDS, FUEL, etc."
        string description
        string source "SOLIQ_EFAKTURA, BANK_STATEMENT"
        string source_reference
        string counterparty_name
        string counterparty_inn
        string mxik_code "Soliq IKPU"
        timestamp created_at
    }

    DEBT_OBLIGATIONS {
        uuid id PK
        uuid organization_id FK
        string lender_name
        string contract_number
        decimal principal
        decimal outstanding_balance
        decimal interest_rate
        decimal monthly_payment
        date start_date
        date maturity_date
        string payment_frequency "MONTHLY, SEASONAL"
        string status "ACTIVE, PAID_OFF, RESTRUCTURED"
        timestamp created_at
    }

    IMPORT_RECORDS {
        uuid id PK
        uuid organization_id FK
        uuid uploaded_by FK
        string file_name
        string file_type "SOLIQ_XLSX, BANK_CSV, KADASTR_DATA"
        string file_hash "SHA-256"
        string import_status "PENDING, PARSED, REJECTED"
        int row_count
        timestamp created_at
    }

    FINANCIAL_FORECASTS {
        uuid id PK
        uuid organization_id FK
        string forecast_name
        string base_period
        int forecast_horizon "12 months"
        decimal yield_shock_pct
        decimal price_shock_pct
        decimal cost_shock_pct
        decimal projected_dscr
        int months_in_deficit
        jsonb assumptions_json
        string model_version "v1.0"
        timestamp created_at
    }

    GENERATED_REPORTS {
        uuid id PK
        uuid organization_id FK
        uuid created_by FK
        string report_type "CREDIT_DOSSIER, CASH_FLOW_AUDIT, VMQ613_VALUATION"
        string report_status "DRAFT, FINALIZED"
        int overall_credit_score
        string rating_tier "Tier 1, Tier 2, etc."
        decimal annual_dscr
        decimal vmq613_estimated_collateral_uzs
        jsonb report_payload_json
        string calculation_version "v1.0"
        timestamp created_at
    }
```

---

## 3. Data Dictionary

### 3.1 `organizations`
Core enterprise tenancy entity.
* `id` (`UUID`, PK): Platform-wide identifier.
* `name` (`VARCHAR(255)`, NOT NULL): Legal company name.
* `organization_type` (`VARCHAR(50)`, NOT NULL): `farmer`, `agricultural_sme`, `exporter`, `agricultural_cluster`.
* `inn` (`VARCHAR(9)`, UNIQUE, NOT NULL): 9-digit Uzbekistan Taxpayer Identification Number (*STIR*).
* `region` / `district` (`VARCHAR(100)`, NOT NULL): Administrative geography.
* `base_currency` (`VARCHAR(3)`, NOT NULL, DEFAULT `'UZS'`): Operating currency.
* `is_demo` (`BOOLEAN`, NOT NULL, DEFAULT `FALSE`): Distinguishes synthetic benchmark businesses from real client tenants.
* `land_hectares` (`NUMERIC(10, 2)`, NOT NULL): Cultivated land area.
* `soil_bonitet_score` (`INTEGER`, CHECK 1..100): Land fertility rating.

### 3.2 `organization_memberships`
Role-Based Access Control (RBAC) linking users to enterprise tenants.
* `id` (`UUID`, PK)
* `organization_id` (`UUID`, FK $\rightarrow$ `organizations.id` ON DELETE CASCADE)
* `user_id` (`UUID`, FK $\rightarrow$ `users.id` ON DELETE CASCADE)
* `role` (`VARCHAR(50)`, NOT NULL): `owner`, `admin`, `accountant`, `finance_manager`, `viewer`.

### 3.3 `transactions`
Granular cash movements.
* `id` (`UUID`, PK)
* `organization_id` (`UUID`, FK $\rightarrow$ `organizations.id` ON DELETE CASCADE)
* `period_id` (`UUID`, FK $\rightarrow$ `financial_periods.id` ON DELETE SET NULL)
* `transaction_date` (`DATE`, NOT NULL)
* `direction` (`VARCHAR(10)`, NOT NULL, CHECK in `('INFLOW', 'OUTFLOW')`)
* `amount` (`NUMERIC(18, 2)`, NOT NULL, CHECK `amount > 0`)
* `category` (`VARCHAR(50)`, NOT NULL): Agronomic category (`CROP_SALES`, `SEEDS_PLANTING`, `FERTILIZER_CHEMICALS`, `FUEL_LUBRICANTS`, `LABOR_SALARIES`, `DEBT_SERVICE`, etc.)
* `source` (`VARCHAR(50)`): `SOLIQ_EFAKTURA`, `BANK_STATEMENT`, `MANUAL_ADJUSTMENT`.
* `mxik_code` (`VARCHAR(20)`): Uzbekistan IKPU product code.

### 3.4 `financial_periods`
Monthly accounting partitions.
* `id` (`UUID`, PK)
* `organization_id` (`UUID`, FK)
* `period_start` / `period_end` (`DATE`, NOT NULL)
* `fiscal_year` (`INTEGER`, NOT NULL)
* `month_number` (`INTEGER`, CHECK 1..12)
* `opening_cash_balance` (`NUMERIC(18, 2)`, NOT NULL)
* `total_inflows` (`NUMERIC(18, 2)`, NOT NULL, DEFAULT 0.00)
* `total_outflows` (`NUMERIC(18, 2)`, NOT NULL, DEFAULT 0.00)
* `closing_balance` (`NUMERIC(18, 2)`, NOT NULL)
* `status` (`VARCHAR(20)`, NOT NULL, DEFAULT `'OPEN'`)
* **Constraint**: `CHECK (closing_balance = opening_cash_balance + total_inflows - total_outflows)`

---

## 4. Multi-Tenancy Security & Data Isolation

1. **Foreign Key Enclosure**: Every table holding financial transactions, debt records, or forecasts explicitly references `organization_id`.
2. **Demo Data Protection**: Demo records carry `is_demo = TRUE`. Public demonstration APIs strictly query datasets where `is_demo = TRUE`, ensuring private enterprise records are never exposed without authorization.
3. **Prepared for Row-Level Security (RLS)**: The PostgreSQL schema is structured for native RLS policies:
   ```sql
   CREATE POLICY tenant_isolation_policy ON transactions
   FOR ALL USING (organization_id = current_setting('app.current_organization_id')::uuid);
   ```
