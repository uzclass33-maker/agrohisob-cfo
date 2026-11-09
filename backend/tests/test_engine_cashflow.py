import pytest
from datetime import date
from decimal import Decimal
from app.financial_engine.schemas import (
    CashFlowAnalysisRequest, CashTransactionInput,
    TransactionDirection, CurrencyEnum
)
from app.financial_engine.cashflow import process_historical_cashflow
from app.financial_engine.exceptions import CurrencyMismatchError

def test_cashflow_positive_and_monthly_continuity():
    """Verifies positive cash flow calculation and roll-forward continuity across all 12 months."""
    txs = [
        CashTransactionInput(
            transaction_date=date(2024, 1, 15),
            direction=TransactionDirection.INFLOW,
            amount=Decimal("15000000.00"),
            category="CROP_SALES"
        ),
        CashTransactionInput(
            transaction_date=date(2024, 1, 20),
            direction=TransactionDirection.OUTFLOW,
            amount=Decimal("5000000.00"),
            category="SEEDS"
        ),
        CashTransactionInput(
            transaction_date=date(2024, 2, 10),
            direction=TransactionDirection.INFLOW,
            amount=Decimal("20000000.00"),
            category="CROP_SALES"
        ),
        CashTransactionInput(
            transaction_date=date(2024, 2, 18),
            direction=TransactionDirection.OUTFLOW,
            amount=Decimal("8000000.00"),
            category="FERTILIZER"
        ),
    ]

    req = CashFlowAnalysisRequest(
        organization_id="org-test-01",
        reporting_period="2024",
        opening_balance=Decimal("10000000.00"),
        transactions=txs,
        currency=CurrencyEnum.UZS
    )

    res = process_historical_cashflow(req)

    # Month 1 checks:
    # Opening 10M + Inflows 15M - Outflows 5M = Net 10M, Closing 20M
    m1 = res.monthly_breakdown[0]
    assert m1.opening_balance == Decimal("10000000.00")
    assert m1.total_inflows == Decimal("15000000.00")
    assert m1.total_outflows == Decimal("5000000.00")
    assert m1.net_cash_flow == Decimal("10000000.00")
    assert m1.closing_balance == Decimal("20000000.00")
    assert m1.is_deficit is False

    # Month 2 checks:
    # Opening 20M + Inflows 20M - Outflows 8M = Net 12M, Closing 32M
    m2 = res.monthly_breakdown[1]
    assert m2.opening_balance == m1.closing_balance
    assert m2.total_inflows == Decimal("20000000.00")
    assert m2.total_outflows == Decimal("8000000.00")
    assert m2.net_cash_flow == Decimal("12000000.00")
    assert m2.closing_balance == Decimal("32000000.00")

    # Invariant: Opening(t+1) == Closing(t) for all 11 transitions
    for i in range(11):
        assert res.monthly_breakdown[i+1].opening_balance == res.monthly_breakdown[i].closing_balance

    assert res.final_closing_balance == res.monthly_breakdown[11].closing_balance
    assert res.data_completeness["continuity_verified"] is True

def test_cashflow_negative_and_deficit_flag():
    """Verifies that outsized outflows produce a negative net cash flow and deficit alert."""
    txs = [
        CashTransactionInput(
            transaction_date=date(2024, 3, 5),
            direction=TransactionDirection.OUTFLOW,
            amount=Decimal("25000000.00"),
            category="EQUIPMENT_MAINTENANCE"
        )
    ]
    req = CashFlowAnalysisRequest(
        organization_id="org-test-02",
        reporting_period="2024",
        opening_balance=Decimal("10000000.00"),
        transactions=txs
    )
    res = process_historical_cashflow(req)
    m3 = res.monthly_breakdown[2]
    # Opening 10M - 25M = -15M
    assert m3.closing_balance == Decimal("-15000000.00")
    assert m3.is_deficit is True

def test_cashflow_reversal_handling():
    """Verifies that reversed transactions counteract inflows or outflows accurately."""
    txs = [
        CashTransactionInput(
            transaction_date=date(2024, 5, 10),
            direction=TransactionDirection.INFLOW,
            amount=Decimal("12000000.00"),
            category="CROP_SALES"
        ),
        CashTransactionInput(
            transaction_date=date(2024, 5, 12),
            direction=TransactionDirection.INFLOW,
            amount=Decimal("2000000.00"),
            category="CROP_SALES",
            is_reversal=True
        )
    ]
    req = CashFlowAnalysisRequest(
        organization_id="org-test-03",
        reporting_period="2024",
        opening_balance=Decimal("0.00"),
        transactions=txs
    )
    res = process_historical_cashflow(req)
    m5 = res.monthly_breakdown[4]
    # Net inflow should be 12M - 2M = 10M
    assert m5.total_inflows == Decimal("10000000.00")
    assert res.category_totals["CROP_SALES"] == Decimal("10000000.00")
    assert res.data_completeness["reversal_count"] == 1

def test_cashflow_currency_mismatch_rejection():
    """Verifies that mixing un-converted currencies raises CurrencyMismatchError."""
    txs = [
        CashTransactionInput(
            transaction_date=date(2024, 6, 1),
            direction=TransactionDirection.INFLOW,
            amount=Decimal("5000.00"),
            category="EXPORT",
            currency=CurrencyEnum.USD
        )
    ]
    req = CashFlowAnalysisRequest(
        organization_id="org-test-04",
        reporting_period="2024",
        opening_balance=Decimal("0.00"),
        transactions=txs,
        currency=CurrencyEnum.UZS
    )
    with pytest.raises(CurrencyMismatchError):
        process_historical_cashflow(req)

def test_cashflow_zero_activity():
    """Verifies that an empty transaction list preserves balance with zero activity."""
    req = CashFlowAnalysisRequest(
        organization_id="org-test-05",
        reporting_period="2024",
        opening_balance=Decimal("50000000.00"),
        transactions=[]
    )
    res = process_historical_cashflow(req)
    assert res.initial_opening_balance == Decimal("50000000.00")
    assert res.final_closing_balance == Decimal("50000000.00")
    assert res.total_inflows == Decimal("0.00")
    assert res.total_outflows == Decimal("0.00")
    assert res.net_cash_flow == Decimal("0.00")
    for m in res.monthly_breakdown:
        assert m.opening_balance == Decimal("50000000.00")
        assert m.closing_balance == Decimal("50000000.00")
        assert m.is_deficit is False
