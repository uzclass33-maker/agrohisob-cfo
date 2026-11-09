import pytest
from decimal import Decimal
from app.services.financial_engine import FinancialEngine

def test_financial_calculation_test_a_positive_cash_flow():
    """
    TEST A — POSITIVE CASH FLOW:
    Opening Balance: 10,000,000 UZS
    Inflows: 8,000,000 UZS
    Outflows: 5,000,000 UZS
    Expected Net Cash Flow: +3,000,000 UZS
    Expected Closing Balance: 13,000,000 UZS
    Closing Balance Identity: Closing = Opening + Inflows - Outflows
    """
    initial_opening = 10_000_000.0
    inflows_month = {"CROP_SALES": 8_000_000.0}
    outflows_month = {"FUEL_LUBRICANTS": 5_000_000.0}
    
    # 12-month array where month 1 has the test figures and other months have zero
    inflows_raw = [inflows_month] + [{"CROP_SALES": 0.0}] * 11
    outflows_raw = [outflows_month] + [{"FUEL_LUBRICANTS": 0.0}] * 11
    debt_service = [0.0] * 12

    summary = FinancialEngine.calculate_12m_cash_flow(
        initial_opening_balance=initial_opening,
        monthly_inflows_raw=inflows_raw,
        monthly_outflows_raw=outflows_raw,
        monthly_debt_service=debt_service
    )

    m1 = summary.monthly_data[0]
    assert m1.opening_balance == 10_000_000.0
    assert m1.total_inflows == 8_000_000.0
    assert m1.total_outflows == 5_000_000.0
    assert m1.net_cash_flow == 3_000_000.0
    assert m1.closing_balance == 13_000_000.0
    assert m1.closing_balance == m1.opening_balance + m1.total_inflows - m1.total_outflows
    assert summary.is_mathematically_reconciled is True


def test_financial_calculation_test_b_negative_cash_flow():
    """
    TEST B — NEGATIVE CASH FLOW:
    Opening Balance: 10,000,000 UZS
    Inflows: 2,000,000 UZS
    Outflows: 7,000,000 UZS
    Expected Net Cash Flow: -5,000,000 UZS
    Expected Closing Balance: 5,000,000 UZS
    Closing Balance Identity: Closing = Opening + Inflows - Outflows
    """
    initial_opening = 10_000_000.0
    inflows_month = {"CROP_SALES": 2_000_000.0}
    outflows_month = {"SEEDS_PLANTING": 7_000_000.0}

    inflows_raw = [inflows_month] + [{"CROP_SALES": 0.0}] * 11
    outflows_raw = [outflows_month] + [{"SEEDS_PLANTING": 0.0}] * 11
    debt_service = [0.0] * 12

    summary = FinancialEngine.calculate_12m_cash_flow(
        initial_opening_balance=initial_opening,
        monthly_inflows_raw=inflows_raw,
        monthly_outflows_raw=outflows_raw,
        monthly_debt_service=debt_service
    )

    m1 = summary.monthly_data[0]
    assert m1.opening_balance == 10_000_000.0
    assert m1.total_inflows == 2_000_000.0
    assert m1.total_outflows == 7_000_000.0
    assert m1.net_cash_flow == -5_000_000.0
    assert m1.closing_balance == 5_000_000.0
    assert m1.closing_balance == m1.opening_balance + m1.total_inflows - m1.total_outflows
    assert summary.is_mathematically_reconciled is True


def test_financial_calculation_test_c_zero_activity():
    """
    TEST C — ZERO ACTIVITY:
    Opening Balance: 10,000,000 UZS
    Inflows: 0 UZS
    Outflows: 0 UZS
    Expected Net Cash Flow: 0 UZS
    Expected Closing Balance: 10,000,000 UZS
    Closing Balance Identity: Closing = Opening + 0 - 0 = Opening
    """
    initial_opening = 10_000_000.0
    inflows_raw = [{"CROP_SALES": 0.0}] * 12
    outflows_raw = [{"MISC_EXPENSES": 0.0}] * 12
    debt_service = [0.0] * 12

    summary = FinancialEngine.calculate_12m_cash_flow(
        initial_opening_balance=initial_opening,
        monthly_inflows_raw=inflows_raw,
        monthly_outflows_raw=outflows_raw,
        monthly_debt_service=debt_service
    )

    for m in summary.monthly_data:
        assert m.opening_balance == 10_000_000.0
        assert m.total_inflows == 0.0
        assert m.total_outflows == 0.0
        assert m.net_cash_flow == 0.0
        assert m.closing_balance == 10_000_000.0

    assert summary.final_closing_balance == 10_000_000.0
    assert summary.net_annual_cash_flow == 0.0
    assert summary.is_mathematically_reconciled is True


def test_financial_calculation_test_d_decimal_precision():
    """
    TEST D — DECIMAL PRECISION:
    Tests fractional sums without IEEE 754 floating-point error accumulation.
    For example: 0.1 + 0.2 != 0.3 in raw binary float, but with Decimal arithmetic
    or exact two-decimal rounding, 1,000,000.15 + 2,000,000.25 - 500,000.40 == 2,500,000.00 exactly.
    """
    initial_opening = 100_000_000.45
    # Precise fractional inflows and outflows
    inflows_month = {"ITEM_1": 12_345_678.12, "ITEM_2": 98_765_432.88} # Sum: 111,111,111.00
    outflows_month = {"COST_1": 55_555_555.55, "COST_2": 44_444_444.45} # Sum: 100,000,000.00
    
    inflows_raw = [inflows_month] + [{"ITEM_1": 0.0}] * 11
    outflows_raw = [outflows_month] + [{"COST_1": 0.0}] * 11
    debt_service = [0.0] * 12

    summary = FinancialEngine.calculate_12m_cash_flow(
        initial_opening_balance=initial_opening,
        monthly_inflows_raw=inflows_raw,
        monthly_outflows_raw=outflows_raw,
        monthly_debt_service=debt_service
    )

    m1 = summary.monthly_data[0]
    # Expected net: 111,111,111.00 - 100,000,000.00 = 11,111,111.00
    assert m1.total_inflows == 111_111_111.00
    assert m1.total_outflows == 100_000_000.00
    assert m1.net_cash_flow == 11_111_111.00
    # Expected closing: 100,000,000.45 + 11,111,111.00 = 111,111,111.45
    assert m1.closing_balance == 111_111_111.45
    assert summary.is_mathematically_reconciled is True


def test_financial_calculation_test_e_monthly_continuity():
    """
    TEST E — MONTHLY CONTINUITY (12-MONTH ROLL-FORWARD INVARIANT):
    For every month N from 1 to 11:
    Opening Balance(Month N + 1) == Closing Balance(Month N)
    Closing Balance(Month N) == Opening Balance(Month N) + Inflows(Month N) - Outflows(Month N)
    Final Year Closing == Initial Opening + Total Annual Inflows - Total Annual Outflows
    """
    # Realistic test scenario with dynamic amounts each month
    initial_opening = 50_000_000.0
    inflows_raw = [
        {"CROP_SALES": 5_000_000.0 * (i + 1)} for i in range(12)
    ]
    outflows_raw = [
        {"OPERATING_EXPENSES": 3_500_000.0 * (i + 1)} for i in range(12)
    ]
    debt_service = [10_000_000.0] * 12

    summary = FinancialEngine.calculate_12m_cash_flow(
        initial_opening_balance=initial_opening,
        monthly_inflows_raw=inflows_raw,
        monthly_outflows_raw=outflows_raw,
        monthly_debt_service=debt_service
    )

    for i in range(11):
        current_month = summary.monthly_data[i]
        next_month = summary.monthly_data[i + 1]

        # Invariant 1: Opening(N+1) == Closing(N)
        assert next_month.opening_balance == current_month.closing_balance, (
            f"Month {i+2} opening balance ({next_month.opening_balance}) does not match "
            f"Month {i+1} closing balance ({current_month.closing_balance})"
        )

        # Invariant 2: Closing(N) == Opening(N) + Inflows(N) - Outflows(N)
        expected_closing = round(current_month.opening_balance + current_month.total_inflows - current_month.total_outflows, 2)
        assert current_month.closing_balance == expected_closing

    # Verify final year closing reconciliation
    assert summary.is_mathematically_reconciled is True
    assert summary.final_closing_balance == summary.monthly_data[11].closing_balance
