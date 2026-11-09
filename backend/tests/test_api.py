import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "agrohisob-backend"
    assert "version" in data

    res_api = client.get("/api/health")
    assert res_api.status_code == 200

def test_api_readiness():
    res = client.get("/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"

def test_v1_demo_organizations():
    res = client.get("/api/v1/demo/organizations")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3
    ids = [org["id"] for org in data]
    assert "scenario-small-farmer" in ids
    assert "scenario-exporter" in ids
    assert "scenario-cluster" in ids
    for org in data:
        assert org["is_demo"] is True
        assert org["currency"] == "UZS"

def test_v1_demo_organization_details():
    res = client.get("/api/v1/demo/organizations/scenario-small-farmer")
    assert res.status_code == 200
    data = res.json()
    assert data["organization"]["name"] == "Andijon Baraka Fermer Xo'jaligi (Sintetik Demo)"
    assert data["currency"] == "UZS"
    assert data["is_demo"] is True

def test_v1_demo_organization_cashflow():
    res = client.get("/api/v1/demo/organizations/scenario-small-farmer/cashflow")
    assert res.status_code == 200
    data = res.json()
    assert data["organization_id"] == "scenario-small-farmer"
    assert data["currency"] == "UZS"
    assert data["reporting_period"] == "2024"
    assert data["is_mathematically_reconciled"] is True
    assert len(data["monthly_breakdown"]) == 12
    # Verify monthly roll-forward continuity
    for i in range(11):
        assert data["monthly_breakdown"][i+1]["opening_balance"] == data["monthly_breakdown"][i]["closing_balance"]

def test_list_scenarios_api():
    res = client.get("/api/scenarios")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3
    assert any(s["key"] == "small_farmer" for s in data)
    assert any(s["key"] == "exporter" for s in data)
    assert any(s["key"] == "cluster" for s in data)

def test_get_scenario_details_api():
    res = client.get("/api/scenarios/scenario-small-farmer")
    assert res.status_code == 200
    data = res.json()
    assert data["organization"]["name"] == "Andijon Baraka Fermer Xo'jaligi (Sintetik Demo)"

def test_get_nonexistent_scenario_404():
    res = client.get("/api/scenarios/non-existent-12345")
    assert res.status_code == 404
    assert "topilmadi" in res.json()["detail"].lower()

def test_calculate_financials_api():
    payload = {
        "scenario_id": "scenario-small-farmer",
        "initial_opening_balance": 45_000_000.0
    }
    res = client.post("/api/financials/calculate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_mathematically_reconciled"] is True
    assert len(data["monthly_data"]) == 12
    # Check that closing balance of December is mathematically reconciled
    assert data["final_closing_balance"] == data["monthly_data"][11]["closing_balance"]

def test_calculate_invalid_request_422():
    payload = {
        "initial_opening_balance": -500.0  # Invalid negative balance
    }
    res = client.post("/api/financials/calculate", json=payload)
    assert res.status_code == 422

def test_stress_test_api():
    payload = {
        "scenario_id": "scenario-exporter",
        "yield_shock_pct": -20.0,
        "price_shock_pct": -10.0,
        "cost_shock_pct": 10.0
    }
    res = client.post("/api/financials/stress-test", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["stressed_annual_inflow"] < data["baseline_annual_inflow"]
    assert data["stressed_dscr"] < data["baseline_dscr"]
    assert "solvency_status" in data

def test_credit_readiness_report_api():
    res = client.get("/api/reports/credit-readiness/scenario-cluster")
    assert res.status_code == 200
    data = res.json()
    assert data["credit_score"] >= 0
    assert data["vmq613_bankable_collateral_uzs"] > 0
    assert len(data["key_strengths"]) > 0
    assert "DIQQAT: Ushbu hisobot sintetik modellashtirish" in data["disclaimer"]
