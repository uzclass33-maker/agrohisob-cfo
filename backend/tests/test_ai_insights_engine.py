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
        # Verify UI-rich fields
        assert "headline_uz" in insight
        assert "core_message_uz" in insight
        assert "evidence_bullets_uz" in insight
        assert isinstance(insight["evidence_bullets_uz"], list)
        assert "recommended_action_uz" in insight
        assert isinstance(insight["supporting_metrics"], dict)

def test_insights_deepseek_integration_mocked(monkeypatch):
    """Validates that request_llm=true invokes DeepSeek and returns enriched response."""
    import httpx

    fake_deepseek_resp = {
        "choices": [
            {
                "message": {
                    "content": '{"financial_health_summary_uz": "Fermer xo\'jaligida bahorgi kassa uzilishi xatari mavjud.", "key_findings_uz": ["Aprel oyida defitsit"], "insights": [{"headline_uz": "Bahorgi likvidlik tanqisligi", "core_message_uz": "Aprelda urug\'lik va o\'g\'it xarajatlari tufayli kassa manfiy.", "evidence_bullets_uz": ["-60,000,000 so\'m defitsit"], "recommended_action_uz": "Aylanma mablag\' uchun revolver kredit jalb etish", "severity": "HIGH", "insight_type": "LIQUIDITY_DEFICIT"}]}'
                }
            }
        ]
    }

    class MockResponse:
        status_code = 200
        def json(self):
            return fake_deepseek_resp

    def mock_post(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(httpx.Client, "post", mock_post)

    resp = client.get("/api/v1/insights?organization_id=scenario-small-farmer&request_llm=true")
    assert resp.status_code == 200
    data = resp.json()
    assert data["generation_method"] == "DEEPSEEK_V3_FINANCIAL_INTELLIGENCE"
    assert data["is_llm_used"] is True
    assert "bahorgi" in data["financial_health_summary_uz"].lower()
    assert len(data["insights"]) == 1
    assert data["insights"][0]["headline_uz"] == "Bahorgi likvidlik tanqisligi"


def test_insights_numerical_claim_validation():
    """Validates that unverified claims or prohibited regulatory statements are rejected."""
    allowed_facts = [Decimal("100.0"), Decimal("200.0"), Decimal("1.25")]
    
    # Claim without forbidden promises
    claim_valid = "Yillik DSCR 1.25x va kassa oqimi ijobiy darajada."
    assert InsightsEngine.validate_llm_claims(claim_valid, allowed_facts) is True

    # Claim with forbidden regulatory promise
    claim_invalid = "Kredit bank tomonidan ma'qullandi va davlat kafolati berildi."
    assert InsightsEngine.validate_llm_claims(claim_invalid, allowed_facts) is False
