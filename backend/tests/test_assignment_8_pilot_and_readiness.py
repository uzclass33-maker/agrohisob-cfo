import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.research.schemas import SourceClassification, CustomerSegment, InterviewStatus
from app.analytics.schemas import AnalyticsEventType

client = TestClient(app)

AUTH_HEADERS = {"Authorization": "Bearer test-token-researcher"}

def test_research_studies_api():
    response = client.get("/api/v1/research/studies", headers=AUTH_HEADERS)
    assert response.status_code == 200
    studies = response.json()
    assert isinstance(studies, list)
    assert len(studies) >= 1
    assert studies[0]["id"] == "study-agroventures-2026"

def test_research_interviews_api_source_classification():
    response = client.get("/api/v1/research/interviews", headers=AUTH_HEADERS)
    assert response.status_code == 200
    interviews = response.json()
    assert isinstance(interviews, list)
    assert len(interviews) >= 1
    
    # Check source classification separation: synthetic records are present but marked
    synthetic_records = [r for r in interviews if r["source_classification"] == SourceClassification.SYNTHETIC_DEMO.value]
    assert len(synthetic_records) >= 1

    # Verify no unconducted interview is marked as VERIFIED_INTERVIEW
    planned_records = [r for r in interviews if r["interview_status"] == InterviewStatus.PLANNED.value]
    for r in planned_records:
        assert r["source_classification"] != SourceClassification.VERIFIED_INTERVIEW.value

def test_add_interview_record():
    payload = {
        "study_id": "study-agroventures-2026",
        "code": "INT-SME-TEST-01",
        "customer_segment": "SME",
        "source_classification": "UNVERIFIED_NOTE",
        "interview_status": "PLANNED",
        "participant_role": "Moliya Menejeri",
        "region": "Buxoro",
        "consent_recorded": False,
        "validated_problems": [],
        "unverified_assumptions": ["Meva quritish sexi uchun 1C hisoboti yetarli emas"],
        "evidence_references": [],
        "notes": "Avtomatik test yozuvi"
    }
    response = client.post("/api/v1/research/interviews", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "INT-SME-TEST-01"
    assert data["id"].startswith("rec-")

def test_research_summary_api():
    response = client.get("/api/v1/research/summary")
    assert response.status_code == 200
    summary = response.json()
    assert "total_records" in summary
    assert "verified_interviews" in summary
    assert "synthetic_demo_records" in summary
    assert "segment_distribution" in summary
    # Initially verified_interviews must be 0 until real interviews are held
    assert summary["verified_interviews"] == 0

def test_analytics_event_tracking_and_privacy_scrubbing():
    payload = {
        "event_type": "import_started",
        "session_id": "sess-anon-12345",
        "organization_id": "org-test-cluster",
        "duration_ms": 120,
        "status": "SUCCESS",
        "metadata": {
            "file_ext": ".xlsx",
            "tax_id": "123456789",  # MUST BE SCRUBBED
            "inn": "987654321",      # MUST BE SCRUBBED
            "bank_account": "202080000000001", # MUST BE SCRUBBED
            "records_count": 45
        }
    }
    response = client.post("/api/v1/analytics/events", json=payload)
    assert response.status_code == 201
    evt = response.json()
    assert evt["id"].startswith("evt-")
    # Verify PII scrubbing
    assert evt["metadata"]["tax_id"] == "[REDACTED_PII]"
    assert evt["metadata"]["inn"] == "[REDACTED_PII]"
    assert evt["metadata"]["bank_account"] == "[REDACTED_PII]"
    assert evt["metadata"]["records_count"] == 45

def test_analytics_summary_api():
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    summary = response.json()
    assert "total_events" in summary
    assert "event_counts" in summary
    assert "avg_durations_ms" in summary

def test_pilot_dashboard_summary_api():
    response = client.get("/api/v1/pilot/dashboard")
    assert response.status_code == 200
    dash = response.json()
    
    # Must explicitly state 0 paying customers and 0 active real pilots
    assert dash["actual_paying_customers"] == 0
    assert dash["actual_active_pilots"] == 0
    assert dash["planned_pilot_targets"] == 5
    assert dash["synthetic_demo_profiles_count"] == 3
    assert len(dash["synthetic_demo_profiles"]) == 3
    assert len(dash["active_pilot_organizations"]) == 0
    assert len(dash["kpi_metrics"]) >= 4
    assert dash["data_security_status"] == "APP_RBAC_ACTIVE_DB_RLS_NOT_VERIFIED"
