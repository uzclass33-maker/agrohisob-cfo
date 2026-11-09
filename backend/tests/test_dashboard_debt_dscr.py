import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard_debt_analytics():
    """Validates debt schedule extraction, interest breakdown, and DSCR risk tiers."""
    resp = client.get("/api/v1/dashboard/debt?organization_id=scenario-small-farmer")
    assert resp.status_code == 200
    data = resp.json()

    assert Decimal(str(data["total_principal"])) > 0
    assert Decimal(str(data["total_interest"])) > 0
    assert Decimal(str(data["total_debt_service"])) > 0
    assert len(data["loan_schedules"]) >= 1

    first_loan = data["loan_schedules"][0]
    assert "Agrobank" in first_loan["lender_name"]
    assert first_loan["annual_interest_rate"] == 14.0
    assert first_loan["monthly_payment"] > 0

    assert len(data["dscr_risk_tier"]) > 0
    assert len(data["dscr_interpretation_uz"]) > 0
    assert "DSCR" in data["dscr_interpretation_uz"]
