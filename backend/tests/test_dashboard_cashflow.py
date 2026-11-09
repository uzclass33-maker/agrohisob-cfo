import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard_cashflow_roll_forward():
    """Validates 12-month roll-forward identity and category totals."""
    resp = client.get("/api/v1/dashboard/cashflow?organization_id=scenario-small-farmer")
    assert resp.status_code == 200
    data = resp.json()

    assert data["currency"] == "UZS"
    assert data["reconciled_with_engine"] is True
    assert len(data["monthly_data"]) == 12

    # Check roll forward: opening(t+1) == closing(t)
    monthly = data["monthly_data"]
    for idx in range(11):
        assert Decimal(str(monthly[idx]["closing_balance"])) == Decimal(str(monthly[idx + 1]["opening_balance"]))

    # Verify net cash flow for each month: closing == opening + net
    for m in monthly:
        c = Decimal(str(m["closing_balance"]))
        o = Decimal(str(m["opening_balance"]))
        net = Decimal(str(m["net_cash_flow"]))
        inf = Decimal(str(m["total_inflows"]))
        outf = Decimal(str(m["total_outflows"]))

        assert c == o + net
        assert net == inf - outf

    # Check category distribution dictionaries
    assert len(data["inflow_by_category"]) > 0
    assert len(data["outflow_by_category"]) > 0
    total_in = sum(Decimal(str(v)) for v in data["inflow_by_category"].values())
    total_out = sum(Decimal(str(v)) for v in data["outflow_by_category"].values())
    assert total_in == Decimal(str(data["total_inflows"]))
    assert total_out == Decimal(str(data["total_outflows"]))
