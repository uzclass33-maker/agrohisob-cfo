"""
Tests for Document Readiness Checklist and Deterministic Financial Readiness Assessment (Assignment 5).
"""

from decimal import Decimal
import pytest

from app.financial_engine import calculate_seasonal_forecast
from app.api.routes_dashboard import _build_forecast_request
from app.reporting.credit_profile import get_default_credit_profile
from app.reporting.readiness_assessment import (
    assess_financial_readiness,
    build_document_readiness_checklist,
)
from app.reporting.report_schemas import ChecklistItemStatus, ReadinessStatusEnum


def test_build_document_readiness_checklist():
    """Verify that the 5-domain checklist has items, categories, and completeness percentage."""
    checklist = build_document_readiness_checklist("scenario-small-farmer", is_imported=False)
    assert checklist.total_items == 12
    assert checklist.available_count >= 5
    assert checklist.completeness_percentage >= 50.0

    categories = {i.category for i in checklist.items}
    expected_categories = {
        "COMPANY_INFO", "FINANCIAL_INFO", "BUSINESS_INFO",
        "AGRICULTURAL_INFO", "FINANCING_INFO"
    }
    assert expected_categories.issubset(categories)


def test_checklist_marks_imported_bank_statement():
    """Verify that is_imported=True marks the bank statement as AVAILABLE."""
    chk_imported = build_document_readiness_checklist("scenario-small-farmer", is_imported=True)
    bank_doc = next(i for i in chk_imported.items if i.id == "chk-fin-bank-stmt")
    assert bank_doc.status == ChecklistItemStatus.AVAILABLE

    chk_not_imported = build_document_readiness_checklist("scenario-small-farmer", is_imported=False)
    bank_doc_raw = next(i for i in chk_not_imported.items if i.id == "chk-fin-bank-stmt")
    assert bank_doc_raw.status == ChecklistItemStatus.NEEDS_REVIEW


def test_assess_financial_readiness():
    """Verify deterministic scoring algorithm produces score 0-100 and explainability."""
    req = _build_forecast_request("scenario-small-farmer", 2026)
    forecast_res = calculate_seasonal_forecast(req)
    checklist = build_document_readiness_checklist("scenario-small-farmer", is_imported=True)
    profile = get_default_credit_profile("scenario-small-farmer")

    assessment = assess_financial_readiness(forecast_res, checklist, profile)
    assert 0 <= assessment.readiness_score <= 100
    assert assessment.overall_status in [
        ReadinessStatusEnum.READY_FOR_REVIEW,
        ReadinessStatusEnum.ADDITIONAL_INFO_REQUIRED,
        ReadinessStatusEnum.INSUFFICIENT_DATA
    ]
    assert len(assessment.key_strengths_uz) > 0
    assert len(assessment.identified_risks_uz) >= 0
    assert len(assessment.critical_limitations_uz) > 0
    assert "AgroHisob CFO" in assessment.audit_disclaimer_uz
