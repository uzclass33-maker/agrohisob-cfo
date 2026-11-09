import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard_forecast_12m_structure():
    """Validates 12-month agricultural forecast parameters and seasonality."""
    resp = client.get("/api/v1/dashboard/forecast?organization_id=scenario-small-farmer&fiscal_year=2026")
    assert resp.status_code == 200
    data = resp.json()

    assert data["organization_id"] == "scenario-small-farmer"
    assert data["fiscal_year"] == 2026
    assert data["forecast_months_count"] == 12
    assert len(data["monthly_forecast"]) == 12

    # Verify assumptions panel fields
    assumptions = data["assumptions"]
    assert "crop_type" in assumptions
    assert "land_hectares" in assumptions
    assert "collection_timing_days" in assumptions

    # Check deficit months and lowest cash point
    assert data["lowest_cash_point"] is not None
    assert data["lowest_cash_month"] in [
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
    ]
    assert data["months_in_deficit"] >= 0
