"""
Twelve-Month Seasonal Cash-Flow Forecasting Engine for Agribusinesses.
Pure, deterministic model combining crop harvest calendars, collection delays,
agricultural input seasonality, and debt amortizations.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict
from collections import defaultdict

from app.financial_engine.schemas import (
    SeasonalForecastRequest, SeasonalForecastResponse,
    MonthlyForecastItem, LiquidityAlert
)
from app.financial_engine.risk import detect_monthly_liquidity_risks

MONTH_NAMES_UZ = [
    "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
    "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
]

TWO_PLACES = Decimal("0.01")
THREE_PLACES = Decimal("0.001")

def round_money(val: Decimal) -> Decimal:
    return val.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def round_ratio(val: Decimal) -> Decimal:
    return val.quantize(THREE_PLACES, rounding=ROUND_HALF_UP)

def calculate_seasonal_forecast(req: SeasonalForecastRequest) -> SeasonalForecastResponse:
    """
    Executes forward-looking 12-month agricultural cash-flow projection.
    Strictly preserves:
    Closing(t) = Opening(t) + Inflows(t) - Outflows(t)
    Opening(t+1) = Closing(t)
    """
    # 1. Map projected crop receipts by month
    monthly_inflows: Dict[int, Decimal] = defaultdict(lambda: Decimal("0.00"))

    for crop in req.crop_assumptions:
        total_production_tons = crop.area_ha * crop.expected_yield_tons_per_ha
        total_crop_revenue = total_production_tons * crop.selling_price_per_ton_uzs

        if not crop.harvest_months:
            continue

        revenue_per_harvest_month = total_crop_revenue / Decimal(len(crop.harvest_months))

        for h_month in crop.harvest_months:
            receipt_month = h_month + crop.collection_delay_months
            # Clamp or map within horizon 1..req.horizon_months
            if 1 <= receipt_month <= req.horizon_months:
                monthly_inflows[receipt_month] += revenue_per_harvest_month

    # 2. Map projected monthly operating expenses
    monthly_operating_outflows: Dict[int, Decimal] = defaultdict(lambda: Decimal("0.00"))
    costs = req.cost_assumptions

    for m_idx in range(req.horizon_months):
        m_num = m_idx + 1
        arr_idx = m_idx % 12  # loop or access 12 calendar month seasonality

        seeds = costs.seeds_planting_by_month[arr_idx] if arr_idx < len(costs.seeds_planting_by_month) else Decimal("0.00")
        fert = costs.fertilizer_chemicals_by_month[arr_idx] if arr_idx < len(costs.fertilizer_chemicals_by_month) else Decimal("0.00")
        fuel = costs.fuel_lubricants_by_month[arr_idx] if arr_idx < len(costs.fuel_lubricants_by_month) else Decimal("0.00")
        labor = costs.labor_salaries_by_month[arr_idx] if arr_idx < len(costs.labor_salaries_by_month) else Decimal("0.00")
        fixed_opex = costs.fixed_monthly_opex_uzs

        month_cost = seeds + fert + fuel + labor + fixed_opex
        monthly_operating_outflows[m_num] = month_cost

    # 3. Monthly Roll-forward calculation
    current_opening = round_money(req.beginning_cash_balance)
    monthly_items: List[MonthlyForecastItem] = []
    all_alerts: List[LiquidityAlert] = []

    total_annual_inflows = Decimal("0.00")
    total_annual_operating_outflows = Decimal("0.00")
    total_annual_debt_service = Decimal("0.00")
    total_annual_outflows = Decimal("0.00")

    months_in_deficit = 0
    lowest_cash_point = Decimal("Infinity")
    lowest_cash_month = "Yanvar"

    for m_idx in range(req.horizon_months):
        m_num = m_idx + 1
        m_name = MONTH_NAMES_UZ[(m_num - 1) % 12]

        inflows_amt = round_money(monthly_inflows[m_num])
        opex_amt = round_money(monthly_operating_outflows[m_num])
        
        debt_amt = Decimal("0.00")
        if m_idx < len(req.existing_monthly_debt_service):
            debt_amt = round_money(req.existing_monthly_debt_service[m_idx])

        total_month_outflows = round_money(opex_amt + debt_amt)
        net_cf = round_money(inflows_amt - total_month_outflows)
        closing = round_money(current_opening + net_cf)

        # CFADS and Monthly DSCR
        cfads = round_money(inflows_amt - opex_amt)
        month_dscr: Decimal | None = None
        if debt_amt > Decimal("0.00"):
            month_dscr = round_ratio(cfads / debt_amt)

        # Track deficits and buffer breaches
        is_deficit = closing < Decimal("0.00")
        is_below_buffer = (closing >= Decimal("0.00")) and (closing < req.min_liquidity_buffer_uzs)

        if is_deficit:
            months_in_deficit += 1

        if closing < lowest_cash_point:
            lowest_cash_point = closing
            lowest_cash_month = m_name

        # Detect alerts for this month
        month_alerts = detect_monthly_liquidity_risks(
            month_number=m_num,
            month_name=m_name,
            opening_balance=current_opening,
            inflows=inflows_amt,
            operating_outflows=opex_amt,
            debt_service=debt_amt,
            closing_balance=closing,
            min_buffer_uzs=req.min_liquidity_buffer_uzs,
            dscr=month_dscr
        )
        all_alerts.extend(month_alerts)

        monthly_items.append(
            MonthlyForecastItem(
                month_number=m_num,
                month_name=m_name,
                opening_balance=current_opening,
                projected_inflows=inflows_amt,
                projected_operating_outflows=opex_amt,
                debt_service=debt_amt,
                total_outflows=total_month_outflows,
                net_cash_flow=net_cf,
                closing_balance=closing,
                cfads=cfads,
                monthly_dscr=month_dscr,
                is_deficit=is_deficit,
                is_below_buffer=is_below_buffer,
                alerts=month_alerts
            )
        )

        total_annual_inflows += inflows_amt
        total_annual_operating_outflows += opex_amt
        total_annual_debt_service += debt_amt
        total_annual_outflows += total_month_outflows

        # Next month roll-forward
        current_opening = closing

    final_closing = current_opening
    net_annual = round_money(total_annual_inflows - total_annual_outflows)

    # Annual DSCR
    annual_cfads = total_annual_inflows - total_annual_operating_outflows
    if total_annual_debt_service > Decimal("0.00"):
        annual_dscr = round_ratio(annual_cfads / total_annual_debt_service)
        if annual_dscr >= Decimal("1.500"):
            dscr_rating = "STRONG (A'lo darajada qoplanadi)"
        elif annual_dscr >= Decimal("1.250"):
            dscr_rating = "HEALTHY (Barqaror qoplanadi)"
        elif annual_dscr >= Decimal("1.000"):
            dscr_rating = "WATCHLIST (Cheklangan / Nazorat ostida)"
        else:
            dscr_rating = "CRITICAL (Kritik yetarsiz)"
    else:
        annual_dscr = None
        dscr_rating = "NO_DEBT (Qarz majburiyati yo'q)"

    return SeasonalForecastResponse(
        organization_id=req.organization_id,
        fiscal_year=req.fiscal_year,
        currency=req.currency,
        initial_cash_balance=round_money(req.beginning_cash_balance),
        final_closing_balance=final_closing,
        total_annual_inflows=round_money(total_annual_inflows),
        total_annual_outflows=round_money(total_annual_outflows),
        total_debt_service=round_money(total_annual_debt_service),
        net_annual_cash_flow=net_annual,
        annual_dscr=annual_dscr,
        dscr_rating=dscr_rating,
        months_in_deficit=months_in_deficit,
        lowest_cash_point=round_money(lowest_cash_point) if lowest_cash_point != Decimal("Infinity") else Decimal("0.00"),
        lowest_cash_month=lowest_cash_month,
        monthly_forecast=monthly_items,
        all_alerts=all_alerts,
        calculation_version="2.0.0"
    )
