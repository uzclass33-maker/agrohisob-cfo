import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard_overview_small_farmer():
    """Validates executive overview KPIs for small farmer benchmark."""
    response = client.get("/api/v1/dashboard/overview?organization_id=scenario-small-farmer")
    assert response.status_code == 200
    data = response.json()
    
    assert data["organization_id"] == "scenario-small-farmer"
    assert "Baraka Fermer" in data["organization_name"]
    assert data["base_currency"] == "UZS"
    assert data["data_source"] in ("SYNTHETIC_BENCHMARK", "BANK_STATEMENT_IMPORT")
    
    kpis = data["kpis"]
    inflows = Decimal(str(kpis["total_inflows"]))
    outflows = Decimal(str(kpis["total_outflows"]))
    net = Decimal(str(kpis["net_cash_flow"]))
    debt = Decimal(str(kpis["debt_service"]))

    assert inflows > 0
    assert outflows > 0
    assert net == inflows - outflows
    assert kpis["closing_balance"] is not None
    assert debt > 0
    assert kpis["dscr"] is not None
    assert kpis["projected_min_balance"] is not None
    assert kpis["min_balance_month"] in [
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
    ]

def test_dashboard_overview_all_scenarios_consistency():
    """Ensures overview succeeds for exporter and cluster scenarios."""
    for org_id in ["scenario-exporter", "scenario-cluster"]:
        resp = client.get(f"/api/v1/dashboard/overview?organization_id={org_id}")
        assert resp.status_code == 200
        d = resp.json()
        assert d["organization_id"] == org_id
        inf = Decimal(str(d["kpis"]["total_inflows"]))
        outf = Decimal(str(d["kpis"]["total_outflows"]))
        net = Decimal(str(d["kpis"]["net_cash_flow"]))
        assert inf > 0
        assert outf > 0
        assert net == inf - outf
