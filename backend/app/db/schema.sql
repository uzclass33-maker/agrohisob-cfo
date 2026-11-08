-- =====================================================================
-- AGROHISOB CFO: ENTERPRISE POSTGRESQL SCHEMA SPECIFICATION
-- Database Architecture for Uzbekistan AgriFinTech B2B SaaS
-- Designed for AgroVentures 2026 Accelerator / Agrobank Pre-Underwriting
-- =====================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------------------------------------------------------------------
-- 1. ENUMS FOR STRICT FINANCIAL VALIDATION
-- ---------------------------------------------------------------------
CREATE TYPE user_role_enum AS ENUM ('SUPER_ADMIN', 'CFO', 'CHIEF_ACCOUNTANT', 'FINANCIAL_ANALYST', 'BANK_AUDITOR');
CREATE TYPE legal_structure_enum AS ENUM ('FERMER_XOJALIGI', 'MCHJ', 'AGRO_KLASTER', 'DEHQON_XOJALIGI', 'XK');
CREATE TYPE transaction_direction_enum AS ENUM ('INFLOW', 'OUTFLOW');
CREATE TYPE transaction_category_enum AS ENUM (
    'CROP_SALES',
    'EXPORT_PROCEEDS',
    'STATE_SUBSIDY',
    'SEEDS_PLANTING',
    'FERTILIZER_CHEMICALS',
    'FUEL_LUBRICANTS',
    'LABOR_SALARIES',
    'MACHINERY_LEASING',
    'UTILITIES_WATER_TAX',
    'DEBT_SERVICE_PRINCIPAL',
    'DEBT_SERVICE_INTEREST',
    'COLD_STORAGE_OPEX',
    'TAXES_OTHER',
    'MISC_EXPENSES'
);
CREATE TYPE file_source_type_enum AS ENUM ('SOLIQ_EFAKTURA_EXCEL', 'SOLIQ_EFAKTURA_XML', 'BANK_STATEMENT_CSV', 'BANK_STATEMENT_PDF', 'KADASTR_EXTRACT');
CREATE TYPE file_parse_status_enum AS ENUM ('PENDING', 'PROCESSING', 'PARSED', 'VALIDATION_FAILED', 'REJECTED');
CREATE TYPE loan_category_enum AS ENUM ('PREFERENTIAL_STATE_AGRO', 'COMMERCIAL_WORKING_CAPITAL', 'EQUIPMENT_LEASING', 'COLD_STORAGE_CAPEX');
CREATE TYPE report_type_enum AS ENUM ('CREDIT_DOSSIER_SUMMARY', 'CASH_FLOW_12M_AUDIT', 'VMQ613_LEASEHOLD_VALUATION', 'STRESS_TEST_REPORT');

-- ---------------------------------------------------------------------
-- 2. ORGANIZATIONS (AGRIBUSINESS PROFILES)
-- ---------------------------------------------------------------------
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    inn VARCHAR(9) UNIQUE NOT NULL, -- STIR (9 digits in Uzbekistan)
    legal_type legal_structure_enum NOT NULL,
    region VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    land_hectares NUMERIC(10, 2) NOT NULL CHECK (land_hectares > 0),
    cadastre_number VARCHAR(50),
    soil_bonitet_score INT CHECK (soil_bonitet_score BETWEEN 1 AND 100),
    main_crop_type VARCHAR(100) NOT NULL,
    has_drip_irrigation BOOLEAN DEFAULT FALSE,
    has_cold_storage BOOLEAN DEFAULT FALSE,
    cold_storage_capacity_tons NUMERIC(10, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_organizations_inn ON organizations(inn);
CREATE INDEX idx_organizations_region ON organizations(region);

-- ---------------------------------------------------------------------
-- 3. USERS (AUTHENTICATION & RBAC)
-- ---------------------------------------------------------------------
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    role user_role_enum NOT NULL DEFAULT 'CHIEF_ACCOUNTANT',
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_organization ON users(organization_id);

-- ---------------------------------------------------------------------
-- 4. FINANCIAL PERIODS (12-MONTH FISCAL TRACKING)
-- ---------------------------------------------------------------------
CREATE TABLE financial_periods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    fiscal_year INT NOT NULL CHECK (fiscal_year >= 2020),
    month_number INT NOT NULL CHECK (month_number BETWEEN 1 AND 12),
    opening_balance NUMERIC(18, 2) NOT NULL,
    total_inflows NUMERIC(18, 2) NOT NULL DEFAULT 0.00,
    total_outflows NUMERIC(18, 2) NOT NULL DEFAULT 0.00,
    closing_balance NUMERIC(18, 2) NOT NULL,
    is_closed BOOLEAN DEFAULT FALSE,
    is_reconciled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Financial Integrity Constraint: Closing Balance = Opening + Inflows - Outflows
    CONSTRAINT chk_closing_balance_identity CHECK (closing_balance = (opening_balance + total_inflows - total_outflows)),
    CONSTRAINT uq_org_year_month UNIQUE(organization_id, fiscal_year, month_number)
);

CREATE INDEX idx_financial_periods_org ON financial_periods(organization_id, fiscal_year);

-- ---------------------------------------------------------------------
-- 5. IMPORTED FILES (AUDIT TRAIL FOR SOLIQ E-FAKTURA & BANK EXPORTS)
-- ---------------------------------------------------------------------
CREATE TABLE imported_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    original_file_name VARCHAR(255) NOT NULL,
    stored_file_path VARCHAR(500) NOT NULL,
    file_type file_source_type_enum NOT NULL,
    file_hash_sha256 VARCHAR(64) NOT NULL,
    row_count INT NOT NULL DEFAULT 0,
    parse_status file_parse_status_enum NOT NULL DEFAULT 'PENDING',
    validation_errors_json JSONB,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_imported_files_org ON imported_files(organization_id);

-- ---------------------------------------------------------------------
-- 6. TRANSACTIONS (DISAGGREGATED AT PRIMARY DOCUMENT LEVEL)
-- ---------------------------------------------------------------------
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    period_id UUID REFERENCES financial_periods(id) ON DELETE SET NULL,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    imported_file_id UUID REFERENCES imported_files(id) ON DELETE SET NULL,
    transaction_date DATE NOT NULL,
    direction transaction_direction_enum NOT NULL,
    amount NUMERIC(18, 2) NOT NULL CHECK (amount > 0),
    category transaction_category_enum NOT NULL,
    counterparty_name VARCHAR(255) NOT NULL,
    counterparty_inn VARCHAR(9),
    mxik_code VARCHAR(20), -- Soliq IKPU (Mahsulot va xizmatlar identifikatsiya kodi)
    document_number VARCHAR(100),
    description TEXT,
    is_verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_org_date ON transactions(organization_id, transaction_date);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_direction ON transactions(direction);

-- ---------------------------------------------------------------------
-- 7. DEBT SCHEDULES (BANK LOANS & LEASING OBLIGATIONS)
-- ---------------------------------------------------------------------
CREATE TABLE debt_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    lender_name VARCHAR(150) NOT NULL, -- e.g. ATB 'Agrobank'
    loan_type loan_category_enum NOT NULL,
    contract_number VARCHAR(100) NOT NULL,
    principal_amount NUMERIC(18, 2) NOT NULL CHECK (principal_amount > 0),
    outstanding_balance NUMERIC(18, 2) NOT NULL CHECK (outstanding_balance >= 0),
    annual_interest_rate NUMERIC(5, 2) NOT NULL CHECK (annual_interest_rate >= 0),
    monthly_payment_total NUMERIC(18, 2) NOT NULL CHECK (monthly_payment_total >= 0),
    monthly_principal NUMERIC(18, 2) NOT NULL CHECK (monthly_principal >= 0),
    monthly_interest NUMERIC(18, 2) NOT NULL CHECK (monthly_interest >= 0),
    start_date DATE NOT NULL,
    maturity_date DATE NOT NULL,
    collateral_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_debt_schedules_org ON debt_schedules(organization_id);

-- ---------------------------------------------------------------------
-- 8. FINANCIAL FORECASTS & SENSITIVITY SCENARIOS
-- ---------------------------------------------------------------------
CREATE TABLE financial_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    scenario_name VARCHAR(150) NOT NULL,
    forecast_year INT NOT NULL,
    yield_shock_pct NUMERIC(5, 2) DEFAULT 0.00, -- e.g. -20% or +10%
    price_shock_pct NUMERIC(5, 2) DEFAULT 0.00,
    cost_shock_pct NUMERIC(5, 2) DEFAULT 0.00,
    projected_annual_inflow NUMERIC(18, 2) NOT NULL,
    projected_annual_outflow NUMERIC(18, 2) NOT NULL,
    net_operating_cash_flow NUMERIC(18, 2) NOT NULL,
    projected_dscr NUMERIC(6, 3) NOT NULL,
    months_in_deficit INT NOT NULL DEFAULT 0,
    lowest_cash_balance NUMERIC(18, 2) NOT NULL,
    monthly_breakdown_json JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_forecasts_org ON financial_forecasts(organization_id);

-- ---------------------------------------------------------------------
-- 9. GENERATED CREDIT DOSSIER REPORTS
-- ---------------------------------------------------------------------
CREATE TABLE generated_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    report_type report_type_enum NOT NULL,
    report_title VARCHAR(255) NOT NULL,
    overall_credit_score INT CHECK (overall_credit_score BETWEEN 0 AND 100),
    credit_rating_tier VARCHAR(10) NOT NULL, -- 'A', 'B', 'C', 'D'
    annual_dscr NUMERIC(6, 3) NOT NULL,
    vmq613_estimated_collateral_uzs NUMERIC(18, 2),
    report_payload_json JSONB NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_generated_reports_org ON generated_reports(organization_id);
