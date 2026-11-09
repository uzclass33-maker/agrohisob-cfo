-- =====================================================================
-- AGROHISOB CFO: MIGRATION 002
-- ENABLE ROW LEVEL SECURITY (RLS) & DURABLE PERSISTENCE TABLES
-- =====================================================================
-- Target: Supabase / PostgreSQL 15+
-- Verification: Isolated Multi-Tenant Testing & Pre-Underwriting Data Safety
-- 
-- BACKUP PLAN BEFORE PRODUCTION EXECUTION:
--   pg_dump -U postgres -h <supabase_host> -d postgres -F c -b -v -f agrohisob_pre_rls_backup.dump
--
-- ROLLBACK SCRIPT (IF NEEDED):
--   ALTER TABLE transactions DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE financial_periods DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE imported_files DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE debt_schedules DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE financial_forecasts DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE generated_reports DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE report_file_records DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE analytics_events DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE research_interviews DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE organization_memberships DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE organizations DISABLE ROW LEVEL SECURITY;
--   DROP POLICY IF EXISTS rls_transactions_tenant ON transactions;
--   DROP POLICY IF EXISTS rls_financial_periods_tenant ON financial_periods;
--   DROP POLICY IF EXISTS rls_imported_files_tenant ON imported_files;
--   DROP POLICY IF EXISTS rls_debt_schedules_tenant ON debt_schedules;
--   DROP POLICY IF EXISTS rls_forecasts_tenant ON financial_forecasts;
--   DROP POLICY IF EXISTS rls_reports_tenant ON generated_reports;
--   DROP POLICY IF EXISTS rls_report_files_tenant ON report_file_records;
--   DROP POLICY IF EXISTS rls_analytics_tenant ON analytics_events;
--   DROP POLICY IF EXISTS rls_research_tenant ON research_interviews;
--   DROP POLICY IF EXISTS rls_memberships_tenant ON organization_memberships;
--   DROP POLICY IF EXISTS rls_orgs_tenant ON organizations;
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. DURABLE PERSISTENCE TABLES (REPLACING EPHEMERAL FILES)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS research_studies (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_count INT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS research_interviews (
    id VARCHAR(64) PRIMARY KEY,
    study_id VARCHAR(64) NOT NULL REFERENCES research_studies(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL,
    customer_segment VARCHAR(50) NOT NULL,
    source_classification VARCHAR(50) NOT NULL,
    interview_status VARCHAR(50) NOT NULL,
    participant_role VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    consent_recorded BOOLEAN DEFAULT FALSE,
    interview_date VARCHAR(50),
    validated_problems JSONB,
    unverified_assumptions JSONB,
    evidence_references JSONB,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_research_interviews_study ON research_interviews(study_id);
CREATE INDEX IF NOT EXISTS idx_research_interviews_status ON research_interviews(interview_status);

CREATE TABLE IF NOT EXISTS analytics_events (
    id VARCHAR(64) PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    user_id VARCHAR(100),
    organization_id VARCHAR(100),
    session_id VARCHAR(100) NOT NULL,
    path VARCHAR(255),
    metadata_json JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_org ON analytics_events(organization_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_time ON analytics_events(timestamp);

CREATE TABLE IF NOT EXISTS report_file_records (
    report_id VARCHAR(64) PRIMARY KEY,
    dossier_id VARCHAR(64),
    organization_id VARCHAR(64) NOT NULL,
    report_title VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'COMPLETED',
    pdf_path VARCHAR(500),
    xlsx_path VARCHAR(500),
    pdf_url VARCHAR(255),
    xlsx_url VARCHAR(255),
    file_hash VARCHAR(64),
    file_size_bytes_pdf INT DEFAULT 0,
    file_size_bytes_xlsx INT DEFAULT 0,
    calculation_version VARCHAR(20) DEFAULT '5.0.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_report_file_records_org ON report_file_records(organization_id);

-- ---------------------------------------------------------------------
-- 2. ENABLE ROW LEVEL SECURITY (RLS) ON ALL DATA TABLES
-- ---------------------------------------------------------------------

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_periods ENABLE ROW LEVEL SECURITY;
ALTER TABLE imported_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE debt_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_file_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_interviews ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------
-- 3. RLS POLICIES FOR AUTHENTICATED SUPABASE USERS (auth.uid())
-- ---------------------------------------------------------------------

-- Helper to check if current authenticated user has active membership in the organization
-- In Supabase: auth.uid() returns the current user's UUID from JWT 'sub' claim

-- 3.1 ORGANIZATIONS
DROP POLICY IF EXISTS rls_orgs_tenant ON organizations;
CREATE POLICY rls_orgs_tenant ON organizations
    FOR ALL
    TO authenticated
    USING (
        id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid() AND is_active = true
        )
        OR (auth.jwt() -> 'app_metadata' ->> 'is_super_admin')::boolean = true
    );

-- 3.2 ORGANIZATION MEMBERSHIPS
DROP POLICY IF EXISTS rls_memberships_tenant ON organization_memberships;
CREATE POLICY rls_memberships_tenant ON organization_memberships
    FOR ALL
    TO authenticated
    USING (
        user_id = auth.uid()
        OR (auth.jwt() -> 'app_metadata' ->> 'is_super_admin')::boolean = true
    );

-- 3.3 FINANCIAL PERIODS
DROP POLICY IF EXISTS rls_financial_periods_tenant ON financial_periods;
CREATE POLICY rls_financial_periods_tenant ON financial_periods
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid() AND is_active = true
        )
        OR (auth.jwt() -> 'app_metadata' ->> 'is_super_admin')::boolean = true
    );

-- 3.4 TRANSACTIONS (CRITICAL FINANCIAL INTEGRITY)
DROP POLICY IF EXISTS rls_transactions_tenant ON transactions;
CREATE POLICY rls_transactions_tenant ON transactions
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid() AND is_active = true
        )
        OR (auth.jwt() -> 'app_metadata' ->> 'is_super_admin')::boolean = true
    );

-- 3.5 IMPORTED FILES
DROP POLICY IF EXISTS rls_imported_files_tenant ON imported_files;
CREATE POLICY rls_imported_files_tenant ON imported_files
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid() AND is_active = true
        )
        OR (auth.jwt() -> 'app_metadata' ->> 'is_super_admin')::boolean = true
    );

-- 3.6 DEBT SCHEDULES
DROP POLICY IF EXISTS rls_debt_schedules_tenant ON debt_schedules;
CREATE POLICY rls_debt_schedules_tenant ON debt_schedules
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid() AND is_active = true
        )
        OR (auth.jwt() -> 'app_metadata' ->> 'is_super_admin')::boolean = true
    );

-- 3.7 FINANCIAL FORECASTS
DROP POLICY IF EXISTS rls_forecasts_tenant ON financial_forecasts;
CREATE POLICY rls_forecasts_tenant ON financial_forecasts
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid() AND is_active = true
        )
        OR (auth.jwt() -> 'app_metadata' ->> 'is_super_admin')::boolean = true
    );

-- 3.8 GENERATED REPORTS & REPORT FILE RECORDS
DROP POLICY IF EXISTS rls_reports_tenant ON generated_reports;
CREATE POLICY rls_reports_tenant ON generated_reports
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid() AND is_active = true
        )
        OR (auth.jwt() -> 'app_metadata' ->> 'is_super_admin')::boolean = true
    );

DROP POLICY IF EXISTS rls_report_files_tenant ON report_file_records;
CREATE POLICY rls_report_files_tenant ON report_file_records
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid() AND is_active = true
        )
        OR (auth.jwt() -> 'app_metadata' ->> 'is_super_admin')::boolean = true
    );

-- 3.9 ANALYTICS EVENTS (Insert by authenticated users; select restricted to SUPER_ADMIN)
DROP POLICY IF EXISTS rls_analytics_insert ON analytics_events;
CREATE POLICY rls_analytics_insert ON analytics_events
    FOR INSERT
    TO authenticated, anon
    WITH CHECK (true);

DROP POLICY IF EXISTS rls_analytics_select ON analytics_events;
CREATE POLICY rls_analytics_select ON analytics_events
    FOR SELECT
    TO authenticated
    USING (
        (auth.jwt() -> 'app_metadata' ->> 'is_super_admin')::boolean = true
    );

-- 3.10 RESEARCH INTERVIEWS (Restricted to SUPER_ADMIN or RESEARCHER)
DROP POLICY IF EXISTS rls_research_tenant ON research_interviews;
CREATE POLICY rls_research_tenant ON research_interviews
    FOR ALL
    TO authenticated
    USING (
        (auth.jwt() -> 'app_metadata' ->> 'is_super_admin')::boolean = true
        OR (auth.jwt() ->> 'role') = 'RESEARCHER'
    );
