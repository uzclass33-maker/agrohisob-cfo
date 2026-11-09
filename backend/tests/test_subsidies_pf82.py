"""
AgroHisob CFO - Unit Tests for PF-82 Cotton & Wheat Financial Support (Assignment 6, Module B)
"""

from decimal import Decimal
from app.subsidies.calculators import calculate_pf82_compensation
from app.subsidies.schemas import PF82CalculationRequest


def test_pf82_cotton_compliant():
    req = PF82CalculationRequest(
        crop_type="Paxta",
        harvest_year=2026,
        loan_principal_uzs=Decimal("150000000.00"),
        contractual_interest_rate_pct=Decimal("14.00"),
        outstanding_balance_uzs=Decimal("100000000.00"),
        days_on_time_repaid=365,
        has_overdue_debt=False,
    )

    res = calculate_pf82_compensation(req)
    assert res.is_eligible is True
    assert res.compensation_pct_points == Decimal("10.00")
    # Farmer pays only 14% - 10% = 4%
    assert res.net_farmer_interest_rate_pct == Decimal("4.00")
    # Compensation for 365 days on 100M at 10% = 10,000,000 UZS
    assert res.indicative_interest_compensation_uzs == Decimal("10000000.00")


def test_pf82_overdue_debt_disqualification():
    # If overdue debt exists, must be disqualified
    req = PF82CalculationRequest(
        crop_type="Paxta",
        harvest_year=2026,
        loan_principal_uzs=Decimal("150000000.00"),
        contractual_interest_rate_pct=Decimal("14.00"),
        outstanding_balance_uzs=Decimal("100000000.00"),
        days_on_time_repaid=365,
        has_overdue_debt=True,  # Overdue debt exists
    )

    res = calculate_pf82_compensation(req)
    assert res.is_eligible is False
    assert res.indicative_interest_compensation_uzs == Decimal("0.00")
    assert "muddati o'tgan" in res.explanation_uz.lower()


def test_pf82_unsupported_crop_disqualification():
    # Only cotton and wheat eligible under PF-82
    req = PF82CalculationRequest(
        crop_type="Olma bog'i",  # Orchard
        harvest_year=2026,
        loan_principal_uzs=Decimal("150000000.00"),
        contractual_interest_rate_pct=Decimal("14.00"),
        outstanding_balance_uzs=Decimal("100000000.00"),
        days_on_time_repaid=365,
        has_overdue_debt=False,
    )

    res = calculate_pf82_compensation(req)
    assert res.is_eligible is False
    assert res.indicative_interest_compensation_uzs == Decimal("0.00")
    assert "paxta va g'alla" in res.explanation_uz.lower()
