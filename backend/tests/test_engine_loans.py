import pytest
from datetime import date
from decimal import Decimal
from app.financial_engine.schemas import (
    LoanScheduleRequest, RepaymentTypeEnum, PaymentFrequencyEnum
)
from app.financial_engine.loans import calculate_loan_schedule
from app.financial_engine.exceptions import (
    InvalidLoanParametersError, NegativePrincipalError
)

def test_annuity_loan_schedule_reconciliation():
    """
    Tests standard annuity loan:
    Principal: 100,000,000 UZS
    Annual rate: 14% (Agrobank preferential rate)
    Term: 12 months
    Monthly payment should be equal (except last period minor rounding adjustment).
    Remaining principal in period 12 MUST be exactly 0.00.
    """
    req = LoanScheduleRequest(
        principal=Decimal("100000000.00"),
        annual_interest_rate_pct=Decimal("14.00"),
        start_date=date(2025, 1, 1),
        term_months=12,
        repayment_type=RepaymentTypeEnum.ANNUITY,
        payment_frequency=PaymentFrequencyEnum.MONTHLY
    )
    res = calculate_loan_schedule(req)
    assert len(res.schedule) == 12
    # Verify final remaining principal is exactly 0.00
    assert res.schedule[-1].remaining_principal == Decimal("0.00")
    # Verify sum of principal paid equals initial principal
    total_principal_paid = sum(item.principal_paid for item in res.schedule)
    assert total_principal_paid == Decimal("100000000.00")
    # Total payment sum must equal principal + total interest cost
    assert res.total_payment_sum == res.principal + res.total_interest_cost
    assert res.total_interest_cost > Decimal("0.00")

def test_equal_principal_loan_schedule():
    """
    Tests equal principal loan (differential payment):
    Principal: 120,000,000 UZS
    Term: 12 months
    Principal paid each month = 10,000,000 UZS
    Interest decreases every month as principal amortizes.
    Remaining principal reaches exactly 0.00.
    """
    req = LoanScheduleRequest(
        principal=Decimal("120000000.00"),
        annual_interest_rate_pct=Decimal("23.50"), # Commercial rate
        start_date=date(2025, 1, 1),
        term_months=12,
        repayment_type=RepaymentTypeEnum.EQUAL_PRINCIPAL,
        payment_frequency=PaymentFrequencyEnum.MONTHLY
    )
    res = calculate_loan_schedule(req)
    assert len(res.schedule) == 12
    # Check that principal paid each month is 10,000,000
    for item in res.schedule:
        assert item.principal_paid == Decimal("10000000.00")
    # Check that interest paid in month 1 is higher than month 12
    assert res.schedule[0].interest_paid > res.schedule[-1].interest_paid
    assert res.schedule[-1].remaining_principal == Decimal("0.00")
    assert sum(item.principal_paid for item in res.schedule) == Decimal("120000000.00")

def test_loan_with_grace_period():
    """
    Tests loan with 3 months grace period:
    During months 1..3, principal paid must be 0.00 and remaining principal stays constant.
    During months 4..12, principal is amortized.
    """
    req = LoanScheduleRequest(
        principal=Decimal("60000000.00"),
        annual_interest_rate_pct=Decimal("14.00"),
        start_date=date(2025, 1, 1),
        term_months=12,
        grace_period_months=3,
        repayment_type=RepaymentTypeEnum.ANNUITY
    )
    res = calculate_loan_schedule(req)
    assert len(res.schedule) == 12
    for m in range(3):
        assert res.schedule[m].principal_paid == Decimal("0.00")
        assert res.schedule[m].opening_principal == Decimal("60000000.00")
        assert res.schedule[m].remaining_principal == Decimal("60000000.00")
    # Month 4 should begin principal repayment
    assert res.schedule[3].principal_paid > Decimal("0.00")
    assert res.schedule[-1].remaining_principal == Decimal("0.00")

def test_zero_interest_loan():
    """Tests interest-free subsidy or state loan (0% interest rate)."""
    req = LoanScheduleRequest(
        principal=Decimal("60000000.00"),
        annual_interest_rate_pct=Decimal("0.00"),
        start_date=date(2025, 1, 1),
        term_months=6,
        repayment_type=RepaymentTypeEnum.ANNUITY
    )
    res = calculate_loan_schedule(req)
    assert res.total_interest_cost == Decimal("0.00")
    assert res.total_payment_sum == Decimal("60000000.00")
    for item in res.schedule:
        assert item.interest_paid == Decimal("0.00")
        assert item.principal_paid == Decimal("10000000.00")
    assert res.schedule[-1].remaining_principal == Decimal("0.00")

def test_quarterly_payment_frequency():
    """Tests quarterly payment frequency (12 months = 4 periods)."""
    req = LoanScheduleRequest(
        principal=Decimal("40000000.00"),
        annual_interest_rate_pct=Decimal("16.00"),
        start_date=date(2025, 1, 1),
        term_months=12,
        payment_frequency=PaymentFrequencyEnum.QUARTERLY,
        repayment_type=RepaymentTypeEnum.EQUAL_PRINCIPAL
    )
    res = calculate_loan_schedule(req)
    assert len(res.schedule) == 4
    for item in res.schedule:
        assert item.principal_paid == Decimal("10000000.00")
    assert res.schedule[-1].remaining_principal == Decimal("0.00")

def test_invalid_loan_parameters_rejected():
    """Verifies that invalid principal or grace period triggers appropriate validation exceptions."""
    from pydantic import ValidationError

    # Negative principal rejected by Pydantic validation
    with pytest.raises(ValidationError):
        LoanScheduleRequest(
            principal=Decimal("-500.00"),
            annual_interest_rate_pct=Decimal("14.00"),
            start_date=date(2025, 1, 1),
            term_months=12
        )

    # Grace period >= term rejected by calculation engine
    with pytest.raises(InvalidLoanParametersError):
        calculate_loan_schedule(
            LoanScheduleRequest(
                principal=Decimal("10000000.00"),
                annual_interest_rate_pct=Decimal("14.00"),
                start_date=date(2025, 1, 1),
                term_months=6,
                grace_period_months=6
            )
        )
