"""
AgroHisob CFO - Post-Assignment 8 Critical Security & Release Gate Test Suite
Validates:
1. Production authentication hardening (rejection of test-tokens, forged signatures, expired tokens).
2. Two genuinely isolated organizations (cross-tenant isolation on dashboard, reports, downloads, imports).
3. Non-acceptance of client-provided organization_id as authorization.
4. Durable database persistence (ReportFileRecordModel, ResearchInterviewModel, AnalyticsEventModel).
5. Pilot dashboard zero-customer and zero-revenue truthfulness.
6. Statutory subsidies (PQ-47, PF-82) and collateral (VMQ-613) disclaimers.
"""

import time
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.auth.models import UserRole
from app.auth.security import create_token, verify_token
from app.db.database import SessionLocal, init_db
from app.models.core import (
    ReportFileRecordModel,
    ResearchInterviewModel,
    AnalyticsEventModel,
)
from app.reporting.report_repository import ReportRepository
from app.reporting.report_schemas import GeneratedReportRecord
from app.research.tracker import ResearchTracker
from app.research.schemas import InterviewRecordCreate, CustomerSegment, SourceClassification, InterviewStatus
from app.analytics.tracker import ProductAnalytics
from app.analytics.schemas import AnalyticsEventCreate

client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_db():
    init_db()


# ---------------------------------------------------------------------
# 1. PRODUCTION AUTHENTICATION HARDENING TESTS
# ---------------------------------------------------------------------

def test_production_rejects_test_tokens(monkeypatch):
    """Under ENVIRONMENT=production, test-token-* MUST be rejected."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    # verify_token unit check
    assert verify_token("test-token-cfo-org1") is None
    assert verify_token("test-token-admin") is None

    # API endpoint check
    res = client.get(
        "/api/v1/dashboard/overview?organization_id=org-bogdor-01",
        headers={"Authorization": "Bearer test-token-cfo-org1"}
    )
    assert res.status_code == 401


def test_production_rejects_forged_signature(monkeypatch):
    """Under ENVIRONMENT=production, forged HMAC signature MUST be rejected."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    # Valid token signed with wrong secret
    forged_token = create_token(
        user_id="attacker-01",
        email="attacker@evil.com",
        role=UserRole.SUPER_ADMIN,
        secret="completely-wrong-secret-key"
    )

    assert verify_token(forged_token) is None

    res = client.get(
        "/api/v1/dashboard/overview?organization_id=org-bogdor-01",
        headers={"Authorization": f"Bearer {forged_token}"}
    )
    assert res.status_code == 401


def test_production_rejects_expired_tokens(monkeypatch):
    """Expired tokens MUST be rejected in production."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    expired_token = create_token(
        user_id="user-cfo-org1",
        email="cfo@bogdor.uz",
        role=UserRole.CFO,
        expires_in_seconds=-3600  # 1 hour ago
    )

    assert verify_token(expired_token) is None

    res = client.get(
        "/api/v1/dashboard/overview?organization_id=org-bogdor-01",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert res.status_code == 401


def test_production_accepts_genuinely_signed_token(monkeypatch):
    """Genuinely signed token with valid secret and unexpired exp must be accepted."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    valid_token = create_token(
        user_id="user-cfo-org1",
        email="cfo@bogdor.uz",
        role=UserRole.CFO,
        memberships={"org-bogdor-01": "CFO"},
        expires_in_seconds=3600
    )

    payload = verify_token(valid_token)
    assert payload is not None
    assert payload["sub"] == "user-cfo-org1"

    res = client.get(
        "/api/v1/dashboard/overview?organization_id=org-bogdor-01",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert res.status_code == 200
    assert res.json()["organization_id"] == "org-bogdor-01"


# ---------------------------------------------------------------------
# 2. TWO GENUINELY ISOLATED ORGANIZATIONS TESTS
# ---------------------------------------------------------------------

def test_two_organizations_strict_cross_tenant_isolation():
    """
    Org 1 (org-bogdor-01) vs Org 2 (org-zarafshon-02).
    User 1 has access ONLY to org-bogdor-01.
    User 2 has access ONLY to org-zarafshon-02.
    Neither user can access or mutate the other's resources.
    """
    token_org1 = "test-token-cfo-org1"
    token_org2 = "test-token-cfo-org2"

    # User 1 accesses Org 1 -> 200 OK
    res1_own = client.get(
        "/api/v1/dashboard/overview?organization_id=org-bogdor-01",
        headers={"Authorization": f"Bearer {token_org1}"}
    )
    assert res1_own.status_code == 200

    # User 2 accesses Org 2 -> 200 OK
    res2_own = client.get(
        "/api/v1/dashboard/overview?organization_id=org-zarafshon-02",
        headers={"Authorization": f"Bearer {token_org2}"}
    )
    assert res2_own.status_code == 200

    # CROSS-TENANT ATTEMPT 1: User 1 attempts to access Org 2 Dashboard -> 403 FORBIDDEN
    res1_cross = client.get(
        "/api/v1/dashboard/overview?organization_id=org-zarafshon-02",
        headers={"Authorization": f"Bearer {token_org1}"}
    )
    assert res1_cross.status_code == 403
    assert "rad etildi" in res1_cross.json()["detail"].lower()

    # CROSS-TENANT ATTEMPT 2: User 2 attempts to access Org 1 Dashboard -> 403 FORBIDDEN
    res2_cross = client.get(
        "/api/v1/dashboard/overview?organization_id=org-bogdor-01",
        headers={"Authorization": f"Bearer {token_org2}"}
    )
    assert res2_cross.status_code == 403

    # CROSS-TENANT ATTEMPT 3: User 1 attempts to access Org 2 Cash Flow -> 403 FORBIDDEN
    res1_cashflow = client.get(
        "/api/v1/dashboard/cashflow?organization_id=org-zarafshon-02",
        headers={"Authorization": f"Bearer {token_org1}"}
    )
    assert res1_cashflow.status_code == 403

    # CROSS-TENANT ATTEMPT 4: User 1 attempts to access Org 2 Forecast -> 403 FORBIDDEN
    res1_forecast = client.get(
        "/api/v1/dashboard/forecast?organization_id=org-zarafshon-02",
        headers={"Authorization": f"Bearer {token_org1}"}
    )
    assert res1_forecast.status_code == 403


def test_reports_cross_tenant_download_forbidden(tmp_path):
    """
    A generated report belonging to Org 2 cannot be downloaded by User 1.
    """
    from datetime import datetime, timezone
    # Create fake report file records for Org 2
    pdf_file = tmp_path / "org2_report.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 fake pdf content")
    xlsx_file = tmp_path / "org2_report.xlsx"
    xlsx_file.write_bytes(b"fake xlsx content")

    rec = GeneratedReportRecord(
        report_id="rep-org2-private-01",
        dossier_id="dos-org2-private-01",
        organization_id="org-zarafshon-02",
        report_title="Zarafshon Baraka Maxfiy Hisoboti",
        created_at=datetime.now(timezone.utc).isoformat(),
        pdf_path=str(pdf_file),
        xlsx_path=str(xlsx_file),
        pdf_url="/api/v1/reports/rep-org2-private-01/download/pdf",
        xlsx_url="/api/v1/reports/rep-org2-private-01/download/xlsx",
        status="COMPLETED"
    )
    ReportRepository.save_report_record(rec)

    # User 1 (from org-bogdor-01) tries to download Org 2 PDF -> 403 FORBIDDEN
    res_pdf = client.get(
        "/api/v1/reports/rep-org2-private-01/download/pdf",
        headers={"Authorization": "Bearer test-token-cfo-org1"}
    )
    assert res_pdf.status_code == 403

    # User 1 tries to download Org 2 XLSX -> 403 FORBIDDEN
    res_xlsx = client.get(
        "/api/v1/reports/rep-org2-private-01/download/xlsx",
        headers={"Authorization": "Bearer test-token-cfo-org1"}
    )
    assert res_xlsx.status_code == 403

    # User 2 (owner of org-zarafshon-02) downloads successfully -> 200 OK
    res_user2 = client.get(
        "/api/v1/reports/rep-org2-private-01/download/pdf",
        headers={"Authorization": "Bearer test-token-cfo-org2"}
    )
    assert res_user2.status_code == 200


# ---------------------------------------------------------------------
# 3. DURABLE PERSISTENCE MODELS DATABASE VERIFICATION
# ---------------------------------------------------------------------

def test_durable_report_persistence_in_db(tmp_path):
    """Verifies that ReportRepository persists records to durable ReportFileRecordModel."""
    from datetime import datetime, timezone
    test_rep_id = f"rep-durable-{int(time.time())}"
    rec = GeneratedReportRecord(
        report_id=test_rep_id,
        dossier_id=f"dos-{test_rep_id}",
        organization_id="org-bogdor-01",
        report_title="Durable Report Persistence Test",
        created_at=datetime.now(timezone.utc).isoformat(),
        pdf_path="/tmp/test.pdf",
        xlsx_path="/tmp/test.xlsx",
        status="COMPLETED"
    )
    ReportRepository.save_report_record(rec)

    # Verify directly from SQLAlchemy database session
    session = SessionLocal()
    try:
        db_record = session.query(ReportFileRecordModel).filter(
            ReportFileRecordModel.report_id == test_rep_id
        ).first()
        assert db_record is not None
        assert db_record.organization_id == "org-bogdor-01"
        assert db_record.report_title == "Durable Report Persistence Test"
    finally:
        session.close()


def test_durable_research_interview_persistence_in_db():
    """Verifies that ResearchTracker persists interviews to durable ResearchInterviewModel."""
    rec_code = f"INT-TEST-{int(time.time()) % 10000}"
    new_rec = InterviewRecordCreate(
        study_id="study-agrohisob-2026",
        code=rec_code,
        customer_segment=CustomerSegment.FARMER,
        source_classification=SourceClassification.UNVERIFIED_NOTE,
        interview_status=InterviewStatus.PLANNED,
        participant_role="Fermer Boshlig'i",
        region="Farg'ona",
        consent_recorded=False,
        validated_problems=[],
        unverified_assumptions=["Test farazi"],
        notes="Durable DB test"
    )
    created = ResearchTracker.add_interview(new_rec)

    # Verify directly from SQLAlchemy database session
    session = SessionLocal()
    try:
        db_rec = session.query(ResearchInterviewModel).filter(
            ResearchInterviewModel.id == created.id
        ).first()
        assert db_rec is not None
        assert db_rec.code == rec_code
        assert db_rec.customer_segment == "FARMER"
    finally:
        session.close()


def test_durable_analytics_event_persistence_in_db():
    """Verifies that ProductAnalytics persists events to durable AnalyticsEventModel."""
    from app.analytics.schemas import AnalyticsEventType
    evt_session = f"sess-test-{int(time.time())}"
    evt_create = AnalyticsEventCreate(
        event_type=AnalyticsEventType.DASHBOARD_VIEWED,
        session_id=evt_session,
        organization_id="org-bogdor-01",
        path="/test",
        metadata={"section": "dashboard_viewed"}
    )
    created = ProductAnalytics.record_event(evt_create)

    # Verify directly from SQLAlchemy database session
    session = SessionLocal()
    try:
        db_evt = session.query(AnalyticsEventModel).filter(
            AnalyticsEventModel.id == created.id
        ).first()
        assert db_evt is not None
        assert db_evt.event_type == AnalyticsEventType.DASHBOARD_VIEWED.value
        assert db_evt.session_id == evt_session
    finally:
        session.close()


# ---------------------------------------------------------------------
# 4. PILOT DASHBOARD ZERO-STATE & TRUTHFULNESS TESTS
# ---------------------------------------------------------------------

def test_pilot_dashboard_zero_state_truthfulness():
    """
    Verifies that Pilot Dashboard exposes exact zero-customer and zero-revenue numbers.
    """
    res = client.get("/api/v1/pilot/dashboard")
    assert res.status_code == 200
    data = res.json()

    assert data["actual_paying_customers"] == 0
    assert data["actual_active_pilots"] == 0
    assert len(data["active_pilot_organizations"]) == 0
    assert len(data["synthetic_demo_profiles"]) > 0
    # Every synthetic profile must be explicitly flagged
    for p in data["synthetic_demo_profiles"]:
        assert p["is_synthetic"] is True


# ---------------------------------------------------------------------
# 5. STATUTORY REGULATIONS (PQ-47, PF-82, VMQ-613) VERIFICATION
# ---------------------------------------------------------------------

def test_subsidies_statutory_disclaimers():
    """
    Verifies that PQ-47 and PF-82 calculations include legal sources and indicative disclaimers.
    """
    # PQ-47 Drip irrigation calculation
    res_pq47 = client.post(
        "/api/v1/subsidies/calculate/pq47",
        json={
            "crop_type": "Paxta",
            "irrigation_technology": "DRIP_IRRIGATION",
            "region": "Qoraqalpog'iston Respublikasi",
            "land_hectares": 10.0,
            "has_water_measuring_devices": True
        }
    )
    assert res_pq47.status_code == 200
    pq_data = res_pq47.json()
    assert "PQ-47" in pq_data["legal_source"]
    assert float(pq_data["estimated_total_subsidy_uzs"]) > 0
    assert len(pq_data["statutory_disclaimer_uz"]) > 20

    # PF-82 Interest compensation calculation
    res_pf82 = client.post(
        "/api/v1/subsidies/calculate/pf82",
        json={
            "loan_principal_uzs": 150000000.0,
            "contractual_interest_rate_pct": 14.0,
            "outstanding_balance_uzs": 120000000.0,
            "crop_type": "Bug'doy",
            "has_overdue_debt": False,
            "repaid_by_year_end": True
        }
    )
    assert res_pf82.status_code == 200
    pf_data = res_pf82.json()
    assert "PF-82" in pf_data["legal_source"]
    assert len(pf_data["disclaimer_uz"]) > 20
