import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_cfo_complete_dashboard_journey():
    """
    Simulates complete CFO analysis journey across all 7 modules:
    1. Check Executive Overview for Small Farmer.
    2. Switch to Exporter and verify updated KPIs.
    3. Inspect Monthly Cash-flow and category distribution.
    4. Review 12-Month seasonal forecast and lowest cash point.
    5. Examine Debt amortizations and DSCR risk rating.
    6. Review detected risks and mitigations.
    7. Simulate Custom stressed scenario and check backend variance.
    8. Retrieve explainable AI-CFO strategic insights.
    """
    # 1. Overview
    res_ov = client.get("/api/v1/dashboard/overview?organization_id=scenario-small-farmer")
    assert res_ov.status_code == 200
    ov_data = res_ov.json()
    assert ov_data["kpis"]["net_cash_flow"] is not None

    # 2. Switch Org
    res_exp = client.get("/api/v1/dashboard/overview?organization_id=scenario-exporter")
    assert res_exp.status_code == 200
    assert "Eksport" in res_exp.json()["organization_name"]

    # 3. Cash Flow
    res_cf = client.get("/api/v1/dashboard/cashflow?organization_id=scenario-small-farmer")
    assert res_cf.status_code == 200
    assert len(res_cf.json()["monthly_data"]) == 12

    # 4. Forecast
    res_fc = client.get("/api/v1/dashboard/forecast?organization_id=scenario-small-farmer")
    assert res_fc.status_code == 200
    assert res_fc.json()["lowest_cash_point"] is not None

    # 5. Debt
    res_db = client.get("/api/v1/dashboard/debt?organization_id=scenario-small-farmer")
    assert res_db.status_code == 200
    assert Decimal(str(res_db.json()["total_debt_service"])) > 0

    # 6. Risks
    res_rk = client.get("/api/v1/dashboard/risks?organization_id=scenario-small-farmer")
    assert res_rk.status_code == 200
    assert res_rk.json()["risks_count"] > 0

    # 7. Scenario Simulation
    res_sim = client.post("/api/v1/dashboard/scenarios", json={
        "organization_id": "scenario-small-farmer",
        "scenario_type": "CUSTOM",
        "revenue_change_pct": -15.0,
        "cost_change_pct": 10.0,
        "collection_delay_months": 1,
        "interest_rate_delta_pct": 1.5
    })
    assert res_sim.status_code == 200
    sim_data = res_sim.json()
    assert Decimal(str(sim_data["variance_net_cash_flow"])) < 0

    # 8. AI Insights
    res_ai = client.get("/api/v1/insights?organization_id=scenario-small-farmer")
    assert res_ai.status_code == 200
    assert len(res_ai.json()["insights"]) > 0
