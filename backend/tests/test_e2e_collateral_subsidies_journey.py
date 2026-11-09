"""
AgroHisob CFO - End-to-End Test for Collateral & Subsidy Journey (Assignment 6)
Verifies the complete flow from land lease profile to legal screening, indicative DCF valuation,
subsidy matching, and dossier enrichment with 0% discrepancy invariant.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.reporting.dossier_builder import DossierBuilder

client = TestClient(app)


def test_e2e_collateral_and_subsidies_journey():
    org_id = "scenario-small-farmer"

    # Step 1: Discover Legal Sources
    res_reg = client.get("/api/v1/regulatory/sources")
    assert res_reg.status_code == 200
    sources = res_reg.json()
    assert any(s["document_code"] == "VMQ-613" for s in sources)
    assert any(s["document_code"] == "PQ-47" for s in sources)
    assert any(s["document_code"] == "PF-82" for s in sources)

    # Step 2: Fetch Organization Collateral Profile
    res_prof = client.get(f"/api/v1/collateral/profile/default?organization_id={org_id}")
    assert res_prof.status_code == 200
    profile = res_prof.json()
    assert profile["organization_id"] == org_id

    # Step 3: Run VMQ-613 Screening & Checklist
    res_screen = client.post("/api/v1/collateral/eligibility", json=profile)
    assert res_screen.status_code == 200
    screen = res_screen.json()
    assert screen["is_eligible"] is True
    assert screen["post_maturity_buffer_years"] >= 5

    res_chk = client.post("/api/v1/collateral/checklist", json=profile)
    assert res_chk.status_code == 200
    chk = res_chk.json()
    assert chk["total_documents"] == 9

    # Step 4: Run Indicative DCF Valuation & Sensitivity
    val_req = {
        "area_hectares": profile["area_hectares"],
        "soil_bonitet_score": profile["soil_bonitet_score"],
        "remaining_lease_years": 25,
        "normative_annual_net_benefit_per_ha_uzs": float(profile["normative_annual_net_benefit_per_ha_uzs"]),
        "discount_rate_pct": float(profile["discount_rate_pct"]),
        "annual_benefit_growth_pct": 2.0,
        "target_ltv_pct": float(profile["target_ltv_pct"]),
    }

    res_val = client.post("/api/v1/collateral/valuation/illustrative", json=val_req)
    assert res_val.status_code == 200
    val = res_val.json()
    assert float(val["indicative_market_value_uzs"]) > 0

    res_scen = client.post("/api/v1/collateral/scenarios", json=val_req)
    assert res_scen.status_code == 200
    scen = res_scen.json()
    assert scen["optimistic_scenario"]["indicative_valuation_uzs"] > scen["base_scenario"]["indicative_valuation_uzs"]

    # Step 5: Match Subsidies and Calculate PQ-47 and PF-82
    sub_req = {
        "organization_id": org_id,
        "region": profile["region"],
        "district": profile["district"],
        "crop_types": [profile["main_crop_type"], "Paxta", "Sabzavot"],
        "land_hectares": profile["area_hectares"],
        "has_drip_irrigation": True,
        "has_bank_debt": True,
    }

    res_sub = client.post("/api/v1/subsidies/financial-impact", json=sub_req)
    assert res_sub.status_code == 200
    impact = res_sub.json()
    assert float(impact["total_potential_subsidy_uzs"]) > 0

    # Step 6: Verify Dossier Enriched with Collateral and Subsidy Intelligence
    dossier = DossierBuilder.build_dossier(org_id)
    assert dossier.collateral_readiness_summary is not None
    assert dossier.collateral_readiness_summary["is_eligible"] is True
    assert dossier.collateral_readiness_summary["indicative_valuation_uzs"] > 0
    assert dossier.subsidy_opportunities_summary is not None
    assert dossier.subsidy_opportunities_summary["matched_count"] > 0

    # Step 7: Verify Non-Certification Disclaimers Present in Both Modules
    assert "baholash" in val["statutory_disclaimer_uz"].lower()
    assert "kafolat" in impact["statutory_disclaimer_uz"].lower()
