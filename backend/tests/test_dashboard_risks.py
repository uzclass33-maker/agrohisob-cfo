import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard_risks_detection():
    """Validates deterministic detection of financial risks, severity tiers, and actions."""
    resp = client.get("/api/v1/dashboard/risks?organization_id=scenario-small-farmer")
    assert resp.status_code == 200
    data = resp.json()

    assert data["risks_count"] > 0
    assert len(data["risks"]) == data["risks_count"]

    severities = {r["severity"] for r in data["risks"]}
    assert any(s in ("CRITICAL", "HIGH", "MEDIUM") for s in severities)

    for risk in data["risks"]:
        assert len(risk["title"]) > 0
        assert len(risk["affected_period"]) > 0
        assert len(risk["trigger_rule"]) > 0
        assert len(risk["explanation_uz"]) > 0
        assert len(risk["business_response_uz"]) > 0
