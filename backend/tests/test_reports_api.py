"""
Tests for Credit Dossier & Bank Reporting REST API endpoints (Assignment 5).
"""

from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)


def test_credit_profile_validation_endpoint():
    """Test POST /api/v1/reports/credit/profile with valid and invalid data."""
    # Valid
    payload = {
        "organization_id": "scenario-small-farmer",
        "organization_name": "Andijon Baraka Fermer Xo'jaligi",
        "requested_loan_amount_uzs": 150000000.0,
        "loan_purpose": "WORKING_CAPITAL",
        "proposed_term_months": 24,
        "proposed_annual_interest_rate_pct": 14.0,
        "repayment_structure": "ANNUITY",
        "grace_period_months": 3,
        "expected_disbursement_date": "2026-03-01"
    }
    res = client.post("/api/v1/reports/credit/profile", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert len(data["errors"]) == 0

    # Invalid (excessive interest rate)
    payload_invalid = {**payload, "proposed_annual_interest_rate_pct": 55.0}
    res_err = client.post("/api/v1/reports/credit/profile", json=payload_invalid)
    assert res_err.status_code == 422  # Pydantic le=50 validator


def test_credit_validate_checklist_endpoint():
    """Test POST /api/v1/reports/credit/validate."""
    res = client.post(
        "/api/v1/reports/credit/validate",
        params={"organization_id": "scenario-small-farmer"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["total_items"] == 12
    assert data["completeness_percentage"] > 0


def test_credit_preview_endpoint():
    """Test POST /api/v1/reports/credit/preview returns full canonical CreditDossierData."""
    res = client.post(
        "/api/v1/reports/credit/preview",
        json={"organization_id": "scenario-small-farmer"}
    )
    assert res.status_code == 200
    dossier = res.json()
    assert dossier["dossier_id"].startswith("dos-")
    assert dossier["organization_id"] == "scenario-small-farmer"
    assert dossier["calculation_version"] == "5.0.0"
    assert "readiness_assessment" in dossier
    assert "historical_summary" in dossier
    assert "forecast_summary" in dossier
    assert "debt_dscr_summary" in dossier
    assert "risks_scenarios_summary" in dossier


def test_credit_generate_and_download_cycle():
    """Test full cycle: generate report, check metadata, download PDF, download XLSX."""
    # 1. Generate
    res_gen = client.post(
        "/api/v1/reports/credit/generate",
        json={"organization_id": "scenario-small-farmer"}
    )
    assert res_gen.status_code == 200
    record = res_gen.json()
    report_id = record["report_id"]
    assert record["status"] == "COMPLETED"
    assert record["file_size_bytes_pdf"] > 5000
    assert record["file_size_bytes_xlsx"] > 5000
    assert record["file_hash"] is not None

    # 2. Get Metadata
    res_meta = client.get(f"/api/v1/reports/{report_id}")
    assert res_meta.status_code == 200
    meta = res_meta.json()
    assert meta["report_id"] == report_id

    # 3. Download PDF
    res_pdf = client.get(f"/api/v1/reports/{report_id}/download/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert res_pdf.content.startswith(b"%PDF-")

    # 4. Download XLSX
    res_xlsx = client.get(f"/api/v1/reports/{report_id}/download/xlsx")
    assert res_xlsx.status_code == 200
    assert "spreadsheetml" in res_xlsx.headers["content-type"]
    assert len(res_xlsx.content) > 5000

    # 5. History list
    res_hist = client.get("/api/v1/reports/history?organization_id=scenario-small-farmer")
    assert res_hist.status_code == 200
    history = res_hist.json()
    assert any(r["report_id"] == report_id for r in history)
