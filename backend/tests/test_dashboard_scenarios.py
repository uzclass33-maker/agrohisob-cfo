import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard_scenarios_optimistic_recalculation():
    """Validates that optimistic scenario genuinely increases cash flow in backend."""
    payload = {
        "organization_id": "scenario-small-farmer",
        "scenario_type": "OPTIMISTIC",
        "revenue_change_pct": 20.0,
        "cost_change_pct": -10.0,
        "collection_delay_months": 0,
        "interest_rate_delta_pct": 0.0
    }
    resp = client.post("/api/v1/dashboard/scenarios", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["scenario_type"] == "OPTIMISTIC"
    stressed_inf = Decimal(str(data["stressed"]["total_annual_inflows"]))
    base_inf = Decimal(str(data["baseline"]["total_annual_inflows"]))
    variance_net = Decimal(str(data["variance_net_cash_flow"]))
    variance_close = Decimal(str(data["variance_closing_balance"]))

    assert stressed_inf > base_inf
    assert variance_net > 0
    assert variance_close > 0

def test_dashboard_scenarios_pessimistic_recalculation():
    """Validates that pessimistic scenario suppresses cash flow and detects solvency impact."""
    payload = {
        "organization_id": "scenario-small-farmer",
        "scenario_type": "PESSIMISTIC",
        "revenue_change_pct": -20.0,
        "cost_change_pct": 15.0,
        "collection_delay_months": 1,
        "interest_rate_delta_pct": 2.0
    }
    resp = client.post("/api/v1/dashboard/scenarios", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["scenario_type"] == "PESSIMISTIC"
    stressed_inf = Decimal(str(data["stressed"]["total_annual_inflows"]))
    base_inf = Decimal(str(data["baseline"]["total_annual_inflows"]))
    variance_net = Decimal(str(data["variance_net_cash_flow"]))
    variance_close = Decimal(str(data["variance_closing_balance"]))

    assert stressed_inf < base_inf
    assert variance_net < 0
    assert variance_close < 0
    assert len(data["solvency_impact"]) > 0
