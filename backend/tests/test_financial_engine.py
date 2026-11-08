import pytest
from app.services.financial_engine import FinancialEngine

def test_monthly_cash_flow_identity_rule():
    """
    Core FinTech invariant:
    For every month t:
    Closing Balance(t) == Opening Balance(t) + Inflows(t) - Outflows(t)
    Opening Balance(t+1) == Closing Balance(t)
    """
    initial_opening = 100_000_000.0
    monthly_inflows = [
        {"CROP_SALES": 50_000_000.0},
        {"CROP_SALES": 20_000_000.0},
        {"CROP_SALES": 0.0},
        {"CROP_SALES": 10_000_000.0},
        {"CROP_SALES": 0.0},
        {"CROP_SALES": 80_000_000.0},
        {"CROP_SALES": 120_000_000.0},
        {"CROP_SALES": 90_000_000.0},
        {"CROP_SALES": 140_000_000.0},
        {"CROP_SALES": 200_000_000.0},
        {"CROP_SALES": 60_000_000.0},
        {"CROP_SALES": 30_000_000.0}
    ]
    monthly_outflows = [
        {"LABOR_SALARIES": 15_000_000.0, "FUEL": 5_000_000.0},
        {"LABOR_SALARIES": 15_000_000.0, "SEEDS": 20_000_000.0},
        {"FERTILIZER": 40_000_000.0, "FUEL": 10_000_000.0},
        {"FERTILIZER": 30_000_000.0, "LABOR": 20_000_000.0},
        {"LABOR_SALARIES": 20_000_000.0},
        {"LABOR_SALARIES": 25_000_000.0},
        {"LABOR_SALARIES": 35_000_000.0},
        {"LABOR_SALARIES": 30_000_000.0},
        {"LABOR_SALARIES": 45_000_000.0},
        {"LABOR_SALARIES": 50_000_000.0},
        {"LABOR_SALARIES": 25_000_000.0},
        {"MISC": 15_000_000.0}
    ]
    monthly_debt = [10_000_000.0] * 12

    result = FinancialEngine.calculate_12m_cash_flow(
        initial_opening_balance=initial_opening,
        monthly_inflows_raw=monthly_inflows,
        monthly_outflows_raw=monthly_outflows,
        monthly_debt_service=monthly_debt
    )

    # 1. Verify every month individually
    for i, month in enumerate(result.monthly_data):
        expected_closing = round(month.opening_balance + month.total_inflows - month.total_outflows, 2)
        assert month.closing_balance == expected_closing, (
            f"Month {month.month_name} violation: closing={month.closing_balance} != expected={expected_closing}"
        )
        if i > 0:
            prev_month = result.monthly_data[i - 1]
            assert month.opening_balance == prev_month.closing_balance, (
                f"Month {month.month_name} roll-forward violation: opening={month.opening_balance} != prev_closing={prev_month.closing_balance}"
            )

    # 2. Overall reconciliation check
    expected_final = initial_opening + result.total_annual_inflows - result.total_annual_outflows
    assert round(result.final_closing_balance, 2) == round(expected_final, 2)
    assert result.is_mathematically_reconciled is True

def test_dscr_calculation_and_benchmarks():
    """Verifies DSCR calculation accuracy."""
    initial_opening = 50_000_000.0
    monthly_inflows = [{"CROP_SALES": 100_000_000.0}] * 12
    monthly_outflows = [{"LABOR_SALARIES": 40_000_000.0}] * 12
    monthly_debt = [20_000_000.0] * 12

    # Annual Operating Inflows = 1,200,000,000
    # Annual Non-debt Outflows = 480,000,000
    # Net Operating Cash Flow = 720,000,000
    # Annual Debt Service = 240,000,000
    # Expected DSCR = 720M / 240M = 3.0

    result = FinancialEngine.calculate_12m_cash_flow(
        initial_opening_balance=initial_opening,
        monthly_inflows_raw=monthly_inflows,
        monthly_outflows_raw=monthly_outflows,
        monthly_debt_service=monthly_debt
    )

    assert result.annual_dscr == 3.0
    assert result.dscr_rating == "EXCELLENT"

def test_vmq613_valuation_formula():
    """Verifies VMQ-613 leasehold collateral calculation."""
    dcf_val, haircut, bankable = FinancialEngine.estimate_vmq613_collateral_value(
        land_hectares=100.0,
        soil_bonitet_score=65,
        remaining_lease_years=25,
        discount_rate=0.16
    )

    assert dcf_val > 0.0
    assert haircut == 0.65
    assert bankable == round(dcf_val * 0.65, 2)
