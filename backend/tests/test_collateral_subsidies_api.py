"""
AgroHisob CFO - Unit Tests for Collateral and Subsidy REST APIs (Assignment 6)
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_collateral_profile_default_api():
    res = client.get("/api/v1/collateral/profile/default?organization_id=scenario-small-farmer")
    assert res.status_code == 200
    data = res.json()
    assert data["organization_id"] == "scenario-small-farmer"
    assert data["area_hectares"] == 65.0
    assert data["is_registered_in_cadastre"] is True


def test_collateral_eligibility_api():
    # 1. Fetch default profile
    prof_res = client.get("/api/v1/collateral/profile/default?organization_id=scenario-small-farmer")
    profile = prof_res.json()

    # 2. Post to eligibility endpoint
    res = client.post("/api/v1/collateral/eligibility", json=profile)
    assert res.status_code == 200
    data = res.json()
    assert "is_eligible" in data
    assert data["is_eligible"] is True
    assert len(data["rule_checks"]) >= 5


def test_collateral_valuation_and_scenarios_api():
    val_req = {
        "area_hectares": 65.0,
        "soil_bonitet_score": 68,
        "remaining_lease_years": 25,
        "normative_annual_net_benefit_per_ha_uzs": 8500000.0,
        "discount_rate_pct": 16.0,
        "annual_benefit_growth_pct": 2.0,
        "target_ltv_pct": 65.0,
    }

    # Illustrative valuation
    res_val = client.post("/api/v1/collateral/valuation/illustrative", json=val_req)
    assert res_val.status_code == 200
    val_data = res_val.json()
    assert float(val_data["indicative_market_value_uzs"]) > 0
    assert float(val_data["max_pledge_value_uzs"]) > 0

    # Sensitivity scenarios
    res_scen = client.post("/api/v1/collateral/scenarios", json=val_req)
    assert res_scen.status_code == 200
    scen_data = res_scen.json()
    assert "base_scenario" in scen_data
    assert "optimistic_scenario" in scen_data
    assert "pessimistic_scenario" in scen_data


def test_collateral_checklist_and_summary_api():
    prof_res = client.get("/api/v1/collateral/profile/default?organization_id=scenario-small-farmer")
    profile = prof_res.json()

    # Checklist
    res_chk = client.post("/api/v1/collateral/checklist", json=profile)
    assert res_chk.status_code == 200
    chk_data = res_chk.json()
    assert chk_data["total_documents"] == 9
    assert chk_data["readiness_percentage"] > 0

    # Summary
    res_sum = client.post("/api/v1/collateral/summary", json=profile)
    assert res_sum.status_code == 200
    sum_data = res_sum.json()
    assert "screening" in sum_data
    assert "valuation" in sum_data
    assert "sensitivity" in sum_data
    assert "checklist" in sum_data
    assert "regulatory_disclaimer_uz" in sum_data


def test_subsidies_programs_and_match_api():
    # Programs list
    res_prog = client.get("/api/v1/subsidies/programs")
    assert res_prog.status_code == 200
    progs = res_prog.json()
    assert len(progs) >= 5

    # Match API
    match_req = {
        "organization_id": "scenario-small-farmer",
        "region": "Andijon viloyati",
        "district": "Asaka tumani",
        "crop_types": ["Paxta", "Sabzavot"],
        "land_hectares": 65.0,
        "has_drip_irrigation": True,
        "has_bank_debt": True,
    }

    res_match = client.post("/api/v1/subsidies/match", json=match_req)
    assert res_match.status_code == 200
    matches = res_match.json()
    assert len(matches) >= 5

    # Financial impact
    res_impact = client.post("/api/v1/subsidies/financial-impact", json=match_req)
    assert res_impact.status_code == 200
    impact = res_impact.json()
    assert float(impact["total_potential_subsidy_uzs"]) > 0
    assert float(impact["immediate_cash_inflow_potential_uzs"]) > 0
    assert float(impact["conditional_future_inflow_uzs"]) > 0


def test_subsidies_pq47_and_pf82_calculators_api():
    # PQ-47 calculator
    pq_req = {
        "crop_type": "Paxta",
        "area_hectares": 25.0,
        "technology_type": "DRIP_IRRIGATION",
        "region": "Andijon viloyati",
        "district": "Asaka tumani",
        "installation_cost_uzs": 250000000.0,
        "financed_via_bank_loan": True,
        "loan_principal_uzs": 200000000.0,
    }
    res_pq = client.post("/api/v1/subsidies/calculate/pq47", json=pq_req)
    assert res_pq.status_code == 200
    assert float(res_pq.json()["estimated_total_subsidy_uzs"]) == 200000000.0

    # PF-82 calculator
    pf_req = {
        "crop_type": "Paxta",
        "harvest_year": 2026,
        "loan_principal_uzs": 150000000.0,
        "contractual_interest_rate_pct": 14.0,
        "outstanding_balance_uzs": 120000000.0,
        "days_on_time_repaid": 365,
        "has_overdue_debt": False,
    }
    res_pf = client.post("/api/v1/subsidies/calculate/pf82", json=pf_req)
    assert res_pf.status_code == 200
    assert res_pf.json()["is_eligible"] is True
    assert float(res_pf.json()["compensation_pct_points"]) == 10.0
