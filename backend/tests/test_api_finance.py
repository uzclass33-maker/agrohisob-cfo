import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_finance_cashflow_analyze():
    payload = {
        "organization_id": "test-org-api",
        "reporting_period": "2024",
        "opening_balance": 10000000.0,
        "transactions": [
            {
                "transaction_date": "2024-01-15",
                "direction": "INFLOW",
                "amount": 20000000.0,
                "category": "CROP_SALES"
            },
            {
                "transaction_date": "2024-01-20",
                "direction": "OUTFLOW",
                "amount": 8000000.0,
                "category": "SEEDS"
            }
        ],
        "currency": "UZS"
    }
    res = client.post("/api/v1/finance/cashflow/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["organization_id"] == "test-org-api"
    assert data["net_cash_flow"] == "12000000.00" or float(data["net_cash_flow"]) == 12000000.0
    assert len(data["monthly_breakdown"]) == 12

def test_api_finance_loans_schedule():
    payload = {
        "principal": 50000000.0,
        "annual_interest_rate_pct": 14.0,
        "start_date": "2025-01-01",
        "term_months": 12,
        "repayment_type": "ANNUITY",
        "payment_frequency": "MONTHLY"
    }
    res = client.post("/api/v1/finance/loans/schedule", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["schedule"]) == 12
    # Last remaining principal must be 0.00
    assert float(data["schedule"][-1]["remaining_principal"]) == 0.0

def test_api_finance_dscr_calculate():
    payload = {
        "operating_cash_inflows": 30000000.0,
        "operating_cash_outflows": 10000000.0,
        "debt_service_principal": 8000000.0,
        "debt_service_interest": 2000000.0
    }
    res = client.post("/api/v1/finance/dscr/calculate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert float(data["dscr"]) == 2.0
    assert data["status_tier"] == "STRONG"

def test_api_finance_forecast():
    payload = {
        "organization_id": "test-forecast-api",
        "fiscal_year": 2026,
        "beginning_cash_balance": 25000000.0,
        "crop_assumptions": [
            {
                "crop_name": "Wheat",
                "area_ha": 15.0,
                "expected_yield_tons_per_ha": 4.0,
                "selling_price_per_ton_uzs": 2500000.0,
                "harvest_months": [6, 7],
                "collection_delay_months": 0
            }
        ],
        "cost_assumptions": {
            "fixed_monthly_opex_uzs": 5000000.0
        },
        "existing_monthly_debt_service": [2000000.0] * 12
    }
    res = client.post("/api/v1/finance/forecast", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["monthly_forecast"]) == 12
    assert "calculation_version" in data

def test_api_finance_scenarios_analyze():
    payload = {
        "base_forecast_request": {
            "organization_id": "test-scenario-api",
            "fiscal_year": 2026,
            "beginning_cash_balance": 50000000.0,
            "crop_assumptions": [
                {
                    "crop_name": "Cotton",
                    "area_ha": 20.0,
                    "expected_yield_tons_per_ha": 3.0,
                    "selling_price_per_ton_uzs": 8000000.0,
                    "harvest_months": [9, 10],
                    "collection_delay_months": 0
                }
            ],
            "cost_assumptions": {
                "fixed_monthly_opex_uzs": 10000000.0
            }
        },
        "scenario_type": "PESSIMISTIC"
    }
    res = client.post("/api/v1/finance/scenarios/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["scenario_type"] == "PESSIMISTIC"
    assert "stressed" in data
    assert "variance_closing_balance" in data
