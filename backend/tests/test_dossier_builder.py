"""
Tests for canonical DossierBuilder service (Assignment 5).
Ensures 100% financial consistency across UI preview, PDF, and Excel representations.
"""

from decimal import Decimal
import pytest

from app.reporting.credit_profile import get_default_credit_profile
from app.reporting.dossier_builder import DossierBuilder
from app.reporting.report_schemas import CreditDossierData


def test_build_dossier_small_farmer():
    """Verify dossier creation for small farmer."""
    dossier = DossierBuilder.build_dossier("scenario-small-farmer")
    assert isinstance(dossier, CreditDossierData)
    assert dossier.organization_id == "scenario-small-farmer"
    assert dossier.calculation_version == "5.0.0"
    
    # Check historical figures
    hist = dossier.historical_summary
    assert hist["total_inflows"] > 0
    assert hist["total_outflows"] > 0
    assert len(hist["monthly_data"]) == 12

    # Check forecast figures
    fc = dossier.forecast_summary
    assert fc["total_annual_inflows"] > 0
    assert fc["total_annual_outflows"] > 0
    assert len(fc["monthly_forecast"]) == 12

    # Check debt & DSCR summary
    debt = dossier.debt_dscr_summary
    assert debt["requested_principal"] == 150000000.0
    assert debt["combined_annual_debt_service"] >= debt["first_year_new_loan_service"]
    assert len(debt["amortization_schedule"]) <= 12

    # Check scenarios
    scenarios = dossier.risks_scenarios_summary
    assert "base" in scenarios
    assert "optimistic" in scenarios
    assert "pessimistic" in scenarios
    assert scenarios["optimistic"]["inflows"] >= scenarios["base"]["inflows"]
    assert scenarios["pessimistic"]["inflows"] <= scenarios["base"]["inflows"]


def test_build_dossier_with_custom_profile():
    """Verify dossier respects customized financing request parameters."""
    custom_profile = get_default_credit_profile("scenario-small-farmer")
    custom_profile.requested_loan_amount_uzs = Decimal("300000000.00")
    custom_profile.proposed_term_months = 36

    dossier = DossierBuilder.build_dossier(
        "scenario-small-farmer",
        custom_profile=custom_profile
    )
    assert dossier.credit_profile.requested_loan_amount_uzs == Decimal("300000000.00")
    assert dossier.debt_dscr_summary["requested_principal"] == 300000000.0
    assert dossier.debt_dscr_summary["requested_term_months"] == 36
