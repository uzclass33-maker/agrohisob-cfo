"""
AgroHisob CFO - Security, Authentication & Tenant Isolation Test Suite
Verifies server-side Bearer token validation, tenant isolation, role-based authorization,
deep PII regex scrubbing, and isolated test storage.
"""

import os
import shutil
import tempfile
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth.security import create_token
from app.auth.models import UserRole
from app.analytics.tracker import ProductAnalytics, set_analytics_storage_dir
from app.analytics.schemas import AnalyticsEventCreate, AnalyticsEventType
from app.research.tracker import ResearchTracker, set_research_storage_dir


# Clean client without any default auth headers
client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. Server-Side Authentication Enforcement (401 Unauthorized)
# -----------------------------------------------------------------------------

def test_unauthenticated_requests_return_401():
    """Verifies that private tenant endpoints strictly reject unauthenticated requests."""
    endpoints = [
        ("GET", "/api/v1/imports/history/list"),
        ("GET", "/api/v1/dashboard/overview?organization_id=org-zarafshon-02"),
        ("GET", "/api/v1/dashboard/cashflow?organization_id=org-zarafshon-02"),
        ("GET", "/api/v1/dashboard/forecast?organization_id=org-zarafshon-02"),
        ("GET", "/api/v1/dashboard/debt?organization_id=org-zarafshon-02"),
        ("GET", "/api/v1/dashboard/risks?organization_id=org-zarafshon-02"),
        ("POST", "/api/v1/dashboard/scenarios", {"organization_id": "org-zarafshon-02"}),
        ("GET", "/api/v1/reports/history?organization_id=org-zarafshon-02"),
        ("GET", "/api/v1/research/studies"),
        ("GET", "/api/v1/research/interviews"),
        ("GET", "/api/v1/analytics/events"),
    ]

    for item in endpoints:
        method = item[0]
        url = item[1]
        payload = item[2] if len(item) > 2 else None

        if method == "GET":
            res = client.get(url, headers={})
        else:
            res = client.post(url, json=payload, headers={})

        assert res.status_code == 401, f"{method} {url} must return 401, got {res.status_code}"
        assert "Autentifikatsiya talab etiladi" in res.json().get("detail", "") or "token" in res.json().get("detail", "").lower()


def test_synthetic_demo_scenarios_allow_anonymous_read_access():
    """Verifies that approved synthetic demo benchmark companies allow anonymous read-only access."""
    demo_scenarios = [
        "scenario-small-farmer",
        "scenario-exporter",
        "scenario-cluster"
    ]
    for s_id in demo_scenarios:
        res = client.get(f"/api/v1/dashboard/overview?organization_id={s_id}")
        assert res.status_code == 200, f"Anonymous access to demo scenario {s_id} must return 200, got {res.status_code}"
        assert res.json()["is_synthetic"] is True
        assert res.json()["organization_id"] == s_id

        # Cashflow endpoint
        cf_res = client.get(f"/api/v1/dashboard/cashflow?organization_id={s_id}")
        assert cf_res.status_code == 200

        # Forecast endpoint
        fc_res = client.get(f"/api/v1/dashboard/forecast?organization_id={s_id}")
        assert fc_res.status_code == 200


def test_invalid_or_tampered_token_returns_401():
    """Verifies that malformed or improperly signed JWTs are rejected."""
    bad_headers = [
        {"Authorization": "Bearer not-a-valid-token"},
        {"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.invalidpayload.invalidsig"},
        {"Authorization": "Basic dXNlcjpwYXNz"},
        {"Authorization": "InvalidFormatToken"},
    ]

    for h in bad_headers:
        res = client.get("/api/v1/dashboard/overview?organization_id=org-zarafshon-02", headers=h)
        assert res.status_code == 401


# -----------------------------------------------------------------------------
# 2. Cross-Tenant Authorization & Isolation (403 Forbidden)
# -----------------------------------------------------------------------------

def test_cross_tenant_access_is_strictly_forbidden():
    """
    Verifies that User A from Org 1 cannot access or modify Org 2's financial data.
    The client-supplied organization_id is never trusted blindly.
    """
    # User 1 (CFO of org-bogdor-01)
    token_user1 = "test-token-cfo-org1"
    headers_user1 = {"Authorization": f"Bearer {token_user1}"}

    # User 1 accessing own organization -> 200 OK
    res_own = client.get("/api/v1/dashboard/overview?organization_id=org-bogdor-01", headers=headers_user1)
    assert res_own.status_code == 200

    # User 1 attempting to access Org 2 (org-zarafshon-02) -> 403 Forbidden
    res_forbidden = client.get("/api/v1/dashboard/overview?organization_id=org-zarafshon-02", headers=headers_user1)
    assert res_forbidden.status_code == 403
    assert "Tashkilotlararo ruxsat rad etildi" in res_forbidden.json().get("detail", "")

    # User 1 attempting to access Org 2 cashflow -> 403 Forbidden
    res_cf_forbidden = client.get("/api/v1/dashboard/cashflow?organization_id=org-zarafshon-02", headers=headers_user1)
    assert res_cf_forbidden.status_code == 403

    # User 1 attempting to run scenario simulation on Org 2 -> 403 Forbidden
    res_scen_forbidden = client.post(
        "/api/v1/dashboard/scenarios",
        json={"organization_id": "org-zarafshon-02"},
        headers=headers_user1
    )
    assert res_scen_forbidden.status_code == 403

    # User 2 (CFO of org-zarafshon-02) attempting to access org-bogdor-01 -> 403 Forbidden
    token_user2 = "test-token-cfo-org2"
    headers_user2 = {"Authorization": f"Bearer {token_user2}"}
    res_user2_forbidden = client.get("/api/v1/dashboard/overview?organization_id=org-bogdor-01", headers=headers_user2)
    assert res_user2_forbidden.status_code == 403


def test_super_admin_has_multi_tenant_oversight():
    """Verifies that authenticated Super Admin has oversight access across tenants."""
    admin_headers = {"Authorization": "Bearer test-token-admin"}

    res1 = client.get("/api/v1/dashboard/overview?organization_id=scenario-small-farmer", headers=admin_headers)
    assert res1.status_code == 200

    res2 = client.get("/api/v1/dashboard/overview?organization_id=scenario-exporter", headers=admin_headers)
    assert res2.status_code == 200


# -----------------------------------------------------------------------------
# 3. Role-Based Access Control (RBAC)
# -----------------------------------------------------------------------------

def test_raw_analytics_restricted_to_admin():
    """Verifies that GET /api/v1/analytics/events is restricted to SUPER_ADMIN."""
    # CFO cannot view raw telemetry events
    cfo_headers = {"Authorization": "Bearer test-token-cfo-org1"}
    res_cfo = client.get("/api/v1/analytics/events", headers=cfo_headers)
    assert res_cfo.status_code == 403

    # Admin can view raw telemetry events
    admin_headers = {"Authorization": "Bearer test-token-admin"}
    res_admin = client.get("/api/v1/analytics/events", headers=admin_headers)
    assert res_admin.status_code == 200


def test_raw_research_restricted_to_admin_or_researcher():
    """Verifies that raw research studies/interviews are restricted to Admin / Researcher."""
    # CFO cannot view raw discovery records
    cfo_headers = {"Authorization": "Bearer test-token-cfo-org1"}
    res_cfo = client.get("/api/v1/research/studies", headers=cfo_headers)
    assert res_cfo.status_code == 403

    # Researcher can view raw studies
    res_headers = {"Authorization": "Bearer test-token-researcher"}
    res_researcher = client.get("/api/v1/research/studies", headers=res_headers)
    assert res_researcher.status_code == 200

    # Public summary endpoint is accessible to all users
    res_summary = client.get("/api/v1/research/summary")
    assert res_summary.status_code == 200


# -----------------------------------------------------------------------------
# 4. Deep Regex PII & Content Scrubbing in Analytics
# -----------------------------------------------------------------------------

def test_deep_regex_and_allowlist_pii_scrubbing():
    """
    Verifies that embedded PII in free-text and dictionary payloads
    (STIR, PINFL, Bank Account, Card, Phone, Email) are scrubbed.
    """
    payload = {
        "event_type": "import_started",
        "session_id": "sess-test-security-999",
        "organization_id": "demo-org-agro-01",
        "duration_ms": 150,
        "status": "SUCCESS",
        "metadata": {
            "section": "import_page",
            "file_ext": ".xlsx",
            "tax_id": "123456789",  # Forbidden key -> [REDACTED_PII]
            "inn": "987654321",      # Forbidden key -> [REDACTED_PII]
            "free_text_note": (
                "Fermer STIR: 301234567, JSHSHIR: 31201901234567, "
                "Bank hisobi: 20208000900123456789, Karta: 8600 1234 5678 9012, "
                "Telefon: +998901234567, Email: farm_lead@agrohisob.uz"
            )
        }
    }

    res = client.post("/api/v1/analytics/events", json=payload)
    assert res.status_code == 201
    evt = res.json()
    meta = evt["metadata"]

    assert meta["tax_id"] == "[REDACTED_PII]"
    assert meta["inn"] == "[REDACTED_PII]"

    # Verify deep string scrubbing
    scrubbed = meta["free_text_note"]
    assert "301234567" not in scrubbed
    assert "[REDACTED_STIR]" in scrubbed
    assert "31201901234567" not in scrubbed
    assert "[REDACTED_PINFL]" in scrubbed
    assert "20208000900123456789" not in scrubbed
    assert "[REDACTED_BANK_ACC]" in scrubbed
    assert "8600 1234 5678 9012" not in scrubbed
    assert "[REDACTED_CARD]" in scrubbed
    assert "+998901234567" not in scrubbed
    assert "[REDACTED_PHONE]" in scrubbed
    assert "farm_lead@agrohisob.uz" not in scrubbed
    assert "[REDACTED_EMAIL]" in scrubbed


# -----------------------------------------------------------------------------
# 5. Storage Isolation During Testing
# -----------------------------------------------------------------------------

def test_storage_directory_isolation():
    """Verifies that custom storage directories completely isolate test data from production."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        analytics_tmp = os.path.join(tmp_dir, "analytics")
        research_tmp = os.path.join(tmp_dir, "research")

        set_analytics_storage_dir(analytics_tmp)
        set_research_storage_dir(research_tmp)

        # Ingest event into isolated directory
        evt = ProductAnalytics.record_event(
            AnalyticsEventCreate(
                event_type=AnalyticsEventType.DEMO_STARTED,
                session_id="test-isolated-sess",
                metadata={"section": "isolated_test"}
            )
        )
        assert os.path.exists(os.path.join(analytics_tmp, "events.json"))

        # Verify summary reflects only isolated events
        summary = ProductAnalytics.get_summary()
        assert summary.total_events == 1

        # Reset storage back to default after test
        default_analytics = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "analytics")
        default_research = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "research")
        set_analytics_storage_dir(default_analytics)
        set_research_storage_dir(default_research)


# -----------------------------------------------------------------------------
# 6. Session Reliability & Expired/Stale Token Handling
# -----------------------------------------------------------------------------

def test_expired_token_is_strictly_rejected_on_private_endpoints():
    """Verifies that expired JWTs are rejected with HTTP 401 on private customer endpoints."""
    expired_token = create_token(
        user_id="user-cfo-org2",
        email="cfo@zarafshon.uz",
        role=UserRole.CFO,
        memberships={"org-zarafshon-02": "CFO"},
        expires_in_seconds=-3600  # Expired 1 hour ago
    )
    headers = {"Authorization": f"Bearer {expired_token}"}

    res_overview = client.get("/api/v1/dashboard/overview?organization_id=org-zarafshon-02", headers=headers)
    assert res_overview.status_code == 401
    assert "Autentifikatsiya talab etiladi" in res_overview.json().get("detail", "") or "token" in res_overview.json().get("detail", "").lower()

    res_history = client.get("/api/v1/reports/history?organization_id=org-zarafshon-02", headers=headers)
    assert res_history.status_code == 401

    res_imports = client.get("/api/v1/imports/history/list", headers=headers)
    assert res_imports.status_code == 401


def test_expired_or_stale_token_does_not_break_synthetic_demo_reads():
    """
    Verifies that a visitor who has an expired or stale token in their browser
    can still cleanly view the three approved synthetic demo scenarios without errors.
    """
    expired_token = create_token(
        user_id="user-old",
        email="old@agrohisob.uz",
        expires_in_seconds=-86400  # Expired 1 day ago
    )
    stale_headers = {"Authorization": f"Bearer {expired_token}"}

    demo_scenarios = ["scenario-small-farmer", "scenario-exporter", "scenario-cluster"]
    for s_id in demo_scenarios:
        # Overview
        res_ov = client.get(f"/api/v1/dashboard/overview?organization_id={s_id}", headers=stale_headers)
        assert res_ov.status_code == 200, f"Overview for {s_id} with expired token must return 200, got {res_ov.status_code}"
        assert res_ov.json()["is_synthetic"] is True

        # Cashflow
        res_cf = client.get(f"/api/v1/dashboard/cashflow?organization_id={s_id}", headers=stale_headers)
        assert res_cf.status_code == 200

        # Forecast
        res_fc = client.get(f"/api/v1/dashboard/forecast?organization_id={s_id}", headers=stale_headers)
        assert res_fc.status_code == 200

        # Report history
        res_hist = client.get(f"/api/v1/reports/history?organization_id={s_id}", headers=stale_headers)
        assert res_hist.status_code == 200


def test_anonymous_access_to_non_demo_org_is_strictly_rejected():
    """Verifies that non-allowlisted organization IDs cannot be accessed anonymously."""
    non_demo_orgs = [
        "org-unknown-customer",
        "org-bogdor-01",
        "org-zarafshon-02",
        "secret-corp-99"
    ]
    for org_id in non_demo_orgs:
        res = client.get(f"/api/v1/dashboard/overview?organization_id={org_id}", headers={})
        assert res.status_code == 401, f"Anonymous access to {org_id} must return 401, got {res.status_code}"


def test_file_imports_strictly_require_valid_authenticated_accountant_or_cfo():
    """Verifies that file imports cannot be accessed anonymously or with invalid/expired tokens."""
    import io
    csv_bytes = b"Sana;Debet;Kredit;Kontragent;INN;Hujjat raqami;To'lov maqsadi\n2026-03-12;1000000;;Test;200115542;101;Test purpose"
    files = {"file": ("statement.csv", io.BytesIO(csv_bytes), "text/csv")}
    data = {"document_type": "BANK_STATEMENT", "organization_id": "demo-org-fruit"}

    # 1. Anonymous upload -> 401
    res_anon = client.post("/api/v1/imports/upload", files=files, data=data, headers={})
    assert res_anon.status_code == 401

    # 2. Expired token upload -> 401
    expired_token = create_token("u1", "cfo@bogdor.uz", role=UserRole.CFO, expires_in_seconds=-60)
    files_exp = {"file": ("statement.csv", io.BytesIO(csv_bytes), "text/csv")}
    res_exp = client.post("/api/v1/imports/upload", files=files_exp, data=data, headers={"Authorization": f"Bearer {expired_token}"})
    assert res_exp.status_code == 401

    # 3. Cross-tenant upload (user from org2 trying to upload to org-bogdor-01) -> 403
    files_cross = {"file": ("statement.csv", io.BytesIO(csv_bytes), "text/csv")}
    cross_data = {"document_type": "BANK_STATEMENT", "organization_id": "org-bogdor-01"}
    res_cross = client.post("/api/v1/imports/upload", files=files_cross, data=cross_data, headers={"Authorization": "Bearer test-token-cfo-org2"})
    assert res_cross.status_code == 403


def test_valid_custom_signed_jwt_respects_tenant_isolation():
    """Verifies that a validly signed JWT is authorized only for its granted organizations."""
    valid_token = create_token(
        user_id="user-custom-cfo",
        email="custom@agro.uz",
        role=UserRole.CFO,
        memberships={"org-custom-agro": "CFO"}
    )
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Access authorized org -> 200 OK
    res_auth = client.get("/api/v1/dashboard/overview?organization_id=org-custom-agro", headers=headers)
    assert res_auth.status_code == 200

    # Access unauthorized other private tenant -> 403 Forbidden
    res_unauth = client.get("/api/v1/dashboard/overview?organization_id=org-zarafshon-02", headers=headers)
    assert res_unauth.status_code == 403
