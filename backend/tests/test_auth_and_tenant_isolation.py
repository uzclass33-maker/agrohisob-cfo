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
