"""
Tests for Credit Profile configuration, defaults, and validation (Assignment 5).
"""

from decimal import Decimal
import pytest

from app.reporting.credit_profile import (
    get_default_credit_profile,
    validate_credit_profile,
)
from app.reporting.report_schemas import CreditProfile, LoanPurposeEnum


def test_default_profiles_load_correctly():
    """Verify default profiles for small farmer, exporter, and cluster."""
    farmer = get_default_credit_profile("scenario-small-farmer")
    assert farmer.organization_name == "Andijon Baraka Fermer Xo'jaligi"
    assert farmer.requested_loan_amount_uzs == Decimal("150000000.00")
    assert farmer.loan_purpose == LoanPurposeEnum.AGRICULTURAL_INPUTS

    exporter = get_default_credit_profile("scenario-exporter")
    assert "Eksport" in exporter.organization_name
    assert exporter.requested_loan_amount_uzs == Decimal("800000000.00")
    assert exporter.loan_purpose == LoanPurposeEnum.WORKING_CAPITAL

    cluster = get_default_credit_profile("scenario-cluster")
    assert "Klaster" in cluster.organization_name
    assert cluster.requested_loan_amount_uzs == Decimal("4000000000.00")
    assert cluster.loan_purpose == LoanPurposeEnum.MACHINERY_EQUIPMENT


def test_validate_valid_profile():
    """Verify that a standard valid profile passes validation."""
    profile = get_default_credit_profile("scenario-small-farmer")
    is_valid, errors = validate_credit_profile(profile)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_invalid_loan_amount():
    """Verify validation detects non-positive loan amount."""
    profile = get_default_credit_profile("scenario-small-farmer")
    profile.requested_loan_amount_uzs = Decimal("-50000.00")
    is_valid, errors = validate_credit_profile(profile)
    assert is_valid is False
    assert any("0 dan katta" in err for err in errors)


def test_validate_invalid_interest_rate():
    """Verify validation detects negative or excessive interest rates."""
    profile = get_default_credit_profile("scenario-small-farmer")
    profile.proposed_annual_interest_rate_pct = Decimal("65.0")
    is_valid, errors = validate_credit_profile(profile)
    assert is_valid is False
    assert any("50%" in err for err in errors)


def test_validate_grace_period_exceeds_term():
    """Verify validation catches grace period exceeding loan term."""
    profile = get_default_credit_profile("scenario-small-farmer")
    profile.proposed_term_months = 12
    profile.grace_period_months = 15
    is_valid, errors = validate_credit_profile(profile)
    assert is_valid is False
    assert any("Imtiyozli davr" in err for err in errors)
