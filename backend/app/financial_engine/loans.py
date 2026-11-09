"""
Loan Amortization Engine for AgroHisob CFO.
Supports:
1. Annuity Repayment (Equal installments)
2. Equal Principal Repayment (Differential installments)
Grace period support, zero-interest handling, exact Decimal reconciliation.
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import List
from dateutil.relativedelta import relativedelta

from app.financial_engine.schemas import (
    LoanScheduleRequest, LoanScheduleResponse, RepaymentScheduleItem,
    RepaymentTypeEnum, PaymentFrequencyEnum
)
from app.financial_engine.exceptions import (
    InvalidLoanParametersError, NegativePrincipalError
)

TWO_PLACES = Decimal("0.01")
SIX_PLACES = Decimal("0.000001")

def round_money(val: Decimal) -> Decimal:
    return val.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def calculate_loan_schedule(req: LoanScheduleRequest) -> LoanScheduleResponse:
    """
    Computes deterministic loan amortization schedule.
    Guarantees that final remaining principal reconciles to exactly 0.00.
    """
    if req.principal <= Decimal("0.00"):
        raise NegativePrincipalError(f"Kredit asosiy qarzi musbat son bo'lishi shart. Berilgan qiymat: {req.principal}")
    
    if req.annual_interest_rate_pct < Decimal("0.00"):
        raise InvalidLoanParametersError(f"Yillik foiz stavkasi manfiy bo'lishi mumkin emas: {req.annual_interest_rate_pct}")

    if req.term_months <= 0:
        raise InvalidLoanParametersError(f"Kredit muddati kamida 1 oy bo'lishi shart: {req.term_months}")

    if req.grace_period_months >= req.term_months:
        raise InvalidLoanParametersError(
            f"Imtiyozli davr ({req.grace_period_months} oy) kreditning umumiy muddatidan ({req.term_months} oy) kam bo'lishi shart."
        )

    # Determine periods per year and number of periods
    if req.payment_frequency == PaymentFrequencyEnum.MONTHLY:
        periods_per_year = Decimal("12")
        total_periods = req.term_months
        grace_periods = req.grace_period_months
        step_delta = relativedelta(months=1)
    elif req.payment_frequency == PaymentFrequencyEnum.QUARTERLY:
        if req.term_months % 3 != 0:
            raise InvalidLoanParametersError(
                f"Choraklik to'lovda kredit muddati 3 ga karrali bo'lishi shart. Berilgan: {req.term_months}"
            )
        periods_per_year = Decimal("4")
        total_periods = req.term_months // 3
        grace_periods = req.grace_period_months // 3
        step_delta = relativedelta(months=3)
    else:
        periods_per_year = Decimal("12")
        total_periods = req.term_months
        grace_periods = req.grace_period_months
        step_delta = relativedelta(months=1)

    amortization_periods = total_periods - grace_periods
    if amortization_periods <= 0:
        raise InvalidLoanParametersError("Asosiy qarzni to'lash uchun kamida 1 davr qolishi lozim.")

    # Periodic interest rate r
    annual_rate_decimal = req.annual_interest_rate_pct / Decimal("100")
    periodic_rate = annual_rate_decimal / periods_per_year
    effective_periodic_pct = round_money(periodic_rate * Decimal("100"))

    # Annuity payment calculation after grace period
    p = req.principal
    r = periodic_rate
    n = amortization_periods

    if req.repayment_type == RepaymentTypeEnum.ANNUITY:
        if r == Decimal("0.00"):
            fixed_annuity_payment = round_money(p / Decimal(n))
        else:
            # Formula: P * [ r * (1 + r)^n ] / [ (1 + r)^n - 1 ]
            one_plus_r_n = (Decimal("1.0") + r) ** n
            numerator = p * r * one_plus_r_n
            denominator = one_plus_r_n - Decimal("1.0")
            fixed_annuity_payment = round_money(numerator / denominator)

    current_principal = round_money(p)
    schedule: List[RepaymentScheduleItem] = []
    total_interest_cost = Decimal("0.00")
    total_payment_sum = Decimal("0.00")

    current_date = req.start_date

    for period in range(1, total_periods + 1):
        payment_date = current_date + (step_delta * period)
        opening_principal = current_principal

        # Interest for current period
        interest_paid = round_money(opening_principal * r)

        if period <= grace_periods:
            # Grace period: only interest is paid, no principal repayment
            principal_paid = Decimal("0.00")
            total_payment = interest_paid
            remaining_principal = opening_principal
        else:
            # Amortization period
            periods_remaining = total_periods - period + 1

            if req.repayment_type == RepaymentTypeEnum.ANNUITY:
                if periods_remaining == 1:
                    # Final payment: clear remaining principal exactly
                    principal_paid = opening_principal
                    total_payment = principal_paid + interest_paid
                    remaining_principal = Decimal("0.00")
                else:
                    target_principal_paid = fixed_annuity_payment - interest_paid
                    if target_principal_paid > opening_principal:
                        target_principal_paid = opening_principal
                    principal_paid = round_money(target_principal_paid)
                    remaining_principal = round_money(opening_principal - principal_paid)
                    total_payment = round_money(principal_paid + interest_paid)
            else:
                # EQUAL_PRINCIPAL (Differential)
                if periods_remaining == 1:
                    principal_paid = opening_principal
                    remaining_principal = Decimal("0.00")
                else:
                    standard_principal_slice = round_money(p / Decimal(n))
                    principal_paid = min(standard_principal_slice, opening_principal)
                    remaining_principal = round_money(opening_principal - principal_paid)
                total_payment = round_money(principal_paid + interest_paid)

        # Prevent negative remaining principal caused by fractional roundoff
        if remaining_principal < Decimal("0.00"):
            principal_paid = opening_principal
            remaining_principal = Decimal("0.00")
            total_payment = round_money(principal_paid + interest_paid)

        schedule.append(
            RepaymentScheduleItem(
                period_number=period,
                payment_date=payment_date.strftime("%Y-%m-%d"),
                opening_principal=opening_principal,
                principal_paid=principal_paid,
                interest_paid=interest_paid,
                total_payment=total_payment,
                remaining_principal=remaining_principal
            )
        )

        total_interest_cost += interest_paid
        total_payment_sum += total_payment
        current_principal = remaining_principal

    return LoanScheduleResponse(
        principal=round_money(req.principal),
        annual_interest_rate_pct=req.annual_interest_rate_pct,
        term_months=req.term_months,
        repayment_type=req.repayment_type,
        payment_frequency=req.payment_frequency,
        grace_period_months=req.grace_period_months,
        total_interest_cost=round_money(total_interest_cost),
        total_payment_sum=round_money(total_payment_sum),
        effective_periodic_rate_pct=effective_periodic_pct,
        schedule=schedule,
        calculation_version="2.0.0"
    )
