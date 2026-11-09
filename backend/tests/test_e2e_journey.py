import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import app

BASE_BACKEND_URL = "http://127.0.0.1:8000"
BASE_FRONTEND_URL = "http://localhost:3000"

def _is_server_available(url: str) -> bool:
    try:
        r = httpx.get(url, timeout=0.5)
        return r.status_code == 200
    except Exception:
        return False

def get_client():
    headers = {"Authorization": "Bearer test-token-admin"}
    if _is_server_available(f"{BASE_BACKEND_URL}/health"):
        return httpx.Client(base_url=BASE_BACKEND_URL, headers=headers)
    return TestClient(app, headers=headers)

def test_e2e_backend_liveness_and_readiness():
    client = get_client()
    r_health = client.get("/health")
    assert r_health.status_code == 200
    health_data = r_health.json()
    assert health_data["status"] == "healthy"
    assert health_data["service"] == "agrohisob-backend"

    r_ready = client.get("/ready")
    assert r_ready.status_code == 200
    ready_data = r_ready.json()
    assert ready_data["status"] == "ready"
    assert ready_data["database"] == "connected"

def test_e2e_demo_organizations_discovery_and_selection():
    client = get_client()
    r_orgs = client.get("/api/v1/demo/organizations")
    assert r_orgs.status_code == 200
    orgs = r_orgs.json()
    assert len(orgs) == 3
    org_ids = [o["id"] for o in orgs]
    assert "scenario-small-farmer" in org_ids
    assert "scenario-exporter" in org_ids
    assert "scenario-cluster" in org_ids

def test_e2e_cashflow_calculation_and_invariants_across_all_scenarios():
    client = get_client()
    scenarios = ["scenario-small-farmer", "scenario-exporter", "scenario-cluster"]
    for s_id in scenarios:
        r_cf = client.get(f"/api/v1/demo/organizations/{s_id}/cashflow")
        assert r_cf.status_code == 200
        cf = r_cf.json()

        assert cf["organization_id"] == s_id
        assert cf["currency"] == "UZS"
        assert cf["is_mathematically_reconciled"] is True
        assert len(cf["monthly_breakdown"]) == 12

        # Roll-forward invariant check
        for m_idx in range(11):
            cur = cf["monthly_breakdown"][m_idx]
            nxt = cf["monthly_breakdown"][m_idx + 1]
            assert nxt["opening_balance"] == cur["closing_balance"]
            expected_cur_closing = round(cur["opening_balance"] + cur["total_inflows"] - cur["total_outflows"], 2)
            assert cur["closing_balance"] == expected_cur_closing

        # Year-end closing equality
        expected_final = round(cf["opening_balance"] + cf["total_inflows"] - cf["total_outflows"], 2)
        assert cf["closing_balance"] == expected_final

def test_e2e_stress_test_simulation():
    client = get_client()
    payload = {
        "scenario_id": "scenario-exporter",
        "yield_shock_pct": -20.0,
        "price_shock_pct": -10.0,
        "cost_shock_pct": 15.0
    }
    res = client.post("/api/financials/stress-test", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["stressed_annual_inflow"] < data["baseline_annual_inflow"]
    assert data["stressed_dscr"] < data["baseline_dscr"]
    assert any(keyword in data["solvency_status"] for keyword in ["RESILIENT", "VULNERABLE", "INSOLVENT"])

def test_e2e_credit_readiness_report():
    client = get_client()
    res = client.get("/api/reports/credit-readiness/scenario-cluster")
    assert res.status_code == 200
    data = res.json()
    assert 0 <= data["credit_score"] <= 100
    assert any(tier in data["rating_tier"] for tier in ["Tier 1", "Tier 2", "Tier 3", "Tier 4"])
    assert data["vmq613_bankable_collateral_uzs"] > 0
    assert "DIQQAT: Ushbu hisobot sintetik modellashtirish" in data["disclaimer"]

def test_e2e_frontend_all_routes_available():
    if not _is_server_available(BASE_FRONTEND_URL):
        pytest.skip("Next.js frontend server is offline (CI environment)")
    routes = ["/", "/demo", "/dashboard", "/data-import", "/scenario-analysis", "/credit-report"]
    with httpx.Client(base_url=BASE_FRONTEND_URL, timeout=5.0) as client:
        for route in routes:
            res = client.get(route)
            assert res.status_code == 200, f"Route {route} failed with status {res.status_code}"
