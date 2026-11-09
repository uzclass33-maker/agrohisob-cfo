"""
Historical Cash Flow Processing Module.
Pure, deterministic Decimal calculations for cash inflows, outflows,
monthly continuity, category breakdown, and completeness checks.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Tuple
from collections import defaultdict

from app.financial_engine.schemas import (
    CashFlowAnalysisRequest, CashFlowAnalysisResponse,
    MonthlyCashFlowItem, TransactionDirection, CurrencyEnum
)
from app.financial_engine.exceptions import CurrencyMismatchError

MONTH_NAMES_UZ = [
    "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
    "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
]

TWO_PLACES = Decimal("0.01")

def round_money(val: Decimal) -> Decimal:
    """Rounds a Decimal value to 2 decimal places using standard financial ROUND_HALF_UP."""
    return val.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def process_historical_cashflow(req: CashFlowAnalysisRequest) -> CashFlowAnalysisResponse:
    """
    Processes a stream of cash transactions for an organization.
    Computes exact monthly and annual cash flow roll-forward balances:
    Closing(t) = Opening(t) + Inflows(t) - Outflows(t)
    Opening(t+1) = Closing(t)
    """
    # 1. Currency validation
    for tx in req.transactions:
        if tx.currency != req.currency:
            raise CurrencyMismatchError(
                f"Tranzaksiya valyutasi ({tx.currency}) so'rov valyutasiga ({req.currency}) mos kelmadi. "
                f"Valyutalarni konvertatsiyasiz aralashtirish man etiladi."
            )

    # 2. Group transactions by month (1..12)
    monthly_inflows: Dict[int, Decimal] = defaultdict(lambda: Decimal("0.00"))
    monthly_outflows: Dict[int, Decimal] = defaultdict(lambda: Decimal("0.00"))
    monthly_category_breakdown: Dict[int, Dict[str, Decimal]] = defaultdict(lambda: defaultdict(lambda: Decimal("0.00")))
    global_category_totals: Dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))

    reversal_count = 0
    total_tx_count = len(req.transactions)

    for tx in req.transactions:
        m = tx.transaction_date.month
        amt = round_money(tx.amount)

        if tx.is_reversal:
            reversal_count += 1
            # Reversals counteract the original direction
            if tx.direction == TransactionDirection.INFLOW:
                monthly_inflows[m] -= amt
                global_category_totals[tx.category] -= amt
                monthly_category_breakdown[m][tx.category] -= amt
            else:
                monthly_outflows[m] -= amt
                global_category_totals[tx.category] -= amt
                monthly_category_breakdown[m][tx.category] -= amt
        else:
            if tx.direction == TransactionDirection.INFLOW:
                monthly_inflows[m] += amt
                global_category_totals[tx.category] += amt
                monthly_category_breakdown[m][tx.category] += amt
            else:
                monthly_outflows[m] += amt
                global_category_totals[tx.category] += amt
                monthly_category_breakdown[m][tx.category] += amt

    # 3. 12-Month Roll-Forward Continuity
    current_opening = round_money(req.opening_balance)
    monthly_items: List[MonthlyCashFlowItem] = []

    total_annual_inflows = Decimal("0.00")
    total_annual_outflows = Decimal("0.00")

    for month_num in range(1, 13):
        m_name = MONTH_NAMES_UZ[month_num - 1]
        m_in = round_money(monthly_inflows[month_num])
        m_out = round_money(monthly_outflows[month_num])
        net_cf = round_money(m_in - m_out)
        closing = round_money(current_opening + net_cf)
        is_deficit = closing < Decimal("0.00")

        # Category mapping for this month
        cats = {k: round_money(v) for k, v in monthly_category_breakdown[month_num].items()}

        monthly_items.append(
            MonthlyCashFlowItem(
                month_number=month_num,
                month_name=m_name,
                opening_balance=current_opening,
                total_inflows=m_in,
                total_outflows=m_out,
                net_cash_flow=net_cf,
                closing_balance=closing,
                is_deficit=is_deficit,
                categories=cats
            )
        )

        total_annual_inflows += m_in
        total_annual_outflows += m_out
        # Roll forward: Opening(N+1) = Closing(N)
        current_opening = closing

    final_closing = current_opening
    net_annual = round_money(total_annual_inflows - total_annual_outflows)

    # 4. Data Completeness & Integrity Indicators
    expected_closing = round_money(req.opening_balance + total_annual_inflows - total_annual_outflows)
    continuity_verified = (final_closing == expected_closing)

    data_completeness = {
        "transaction_count": total_tx_count,
        "reversal_count": reversal_count,
        "active_months_with_transactions": len([m for m in monthly_inflows if monthly_inflows[m] > 0 or monthly_outflows[m] > 0]),
        "continuity_verified": continuity_verified,
        "rounding_difference_uzs": str(final_closing - expected_closing)
    }

    return CashFlowAnalysisResponse(
        organization_id=req.organization_id,
        reporting_period=req.reporting_period,
        currency=req.currency,
        initial_opening_balance=round_money(req.opening_balance),
        final_closing_balance=final_closing,
        total_inflows=round_money(total_annual_inflows),
        total_outflows=round_money(total_annual_outflows),
        net_cash_flow=net_annual,
        monthly_breakdown=monthly_items,
        category_totals={k: round_money(v) for k, v in global_category_totals.items()},
        data_completeness=data_completeness,
        calculation_version="2.0.0"
    )
