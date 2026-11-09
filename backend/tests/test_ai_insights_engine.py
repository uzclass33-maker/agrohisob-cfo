import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.financial_engine.insights import InsightsEngine

client = TestClient(app)

def test_insights_deterministic_generation():
    """Validates Layer A deterministic insight generation."""
    resp = client.get("/api/v1/insights?organization_id=scenario-small-farmer&request_llm=false")
    assert resp.status_code == 200
    data = resp.json()

    assert data["generation_method"] == "DETERMINISTIC_RULE_ENGINE"
    assert data["is_llm_used"] is False
    assert len(data["financial_health_summary_uz"]) > 0
    assert len(data["key_findings_uz"]) > 0
    assert len(data["insights"]) > 0

    for insight in data["insights"]:
        assert insight["generation_method"] == "DETERMINISTIC_RULE_ENGINE"
        assert len(insight["explanation_uz"]) > 0
        assert len(insight["suggested_action_uz"]) > 0
        assert isinstance(insight["supporting_values"], dict)

def test_insights_numerical_claim_validation():
    """Validates that unverified claims or prohibited regulatory statements are rejected."""
    allowed_facts = [Decimal("100.0"), Decimal("200.0"), Decimal("1.25")]
    
    # Claim without forbidden promises
    claim_valid = "Yillik DSCR 1.25x va kassa oqimi ijobiy darajada."
    assert InsightsEngine.validate_llm_claims(claim_valid, allowed_facts) is True

    # Claim with forbidden regulatory promise
    claim_invalid = "Kredit bank tomonidan ma'qullandi va davlat kafolati berildi."
    assert InsightsEngine.validate_llm_claims(claim_invalid, allowed_facts) is False
