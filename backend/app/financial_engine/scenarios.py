"""
Scenario & Sensitivity Analysis Engine for AgroHisob CFO.
Reruns complete underlying deterministic cash-flow models with adjusted assumptions.
Supports: Base, Optimistic, Pessimistic, and Custom Scenarios.
"""

import copy
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple

from app.financial_engine.schemas import (
    ScenarioAnalysisRequest, ScenarioComparisonResponse,
    ScenarioTypeEnum, ScenarioAdjustments, SeasonalForecastRequest
)
from app.financial_engine.forecasting import calculate_seasonal_forecast

TWO_PLACES = Decimal("0.01")
THREE_PLACES = Decimal("0.001")

def round_money(val: Decimal) -> Decimal:
    return val.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def round_ratio(val: Decimal) -> Decimal:
    return val.quantize(THREE_PLACES, rounding=ROUND_HALF_UP)

def run_scenario_analysis(req: ScenarioAnalysisRequest) -> ScenarioComparisonResponse:
    """
    Executes a scenario comparison by recomputing full underlying cash flows.
    Guarantees that all dependent variables (monthly receipts, opex, CFADS, DSCR, deficits)
    are recalculated from scratch.
    """
    # 1. Calculate baseline forecast
    base_forecast = calculate_seasonal_forecast(req.base_forecast_request)

    # 2. Determine adjustments based on scenario type
    adjustments: ScenarioAdjustments
    if req.scenario_type == ScenarioTypeEnum.BASE:
        adjustments = ScenarioAdjustments(
            revenue_change_pct=Decimal("0.00"),
            cost_change_pct=Decimal("0.00"),
            collection_delay_months=0,
            interest_rate_delta_pct=Decimal("0.00")
        )
    elif req.scenario_type == ScenarioTypeEnum.OPTIMISTIC:
        adjustments = ScenarioAdjustments(
            revenue_change_pct=Decimal("20.00"),
            cost_change_pct=Decimal("-10.00"),
            collection_delay_months=0,
            interest_rate_delta_pct=Decimal("0.00")
        )
    elif req.scenario_type == ScenarioTypeEnum.PESSIMISTIC:
        adjustments = ScenarioAdjustments(
            revenue_change_pct=Decimal("-20.00"),
            cost_change_pct=Decimal("15.00"),
            collection_delay_months=1,
            interest_rate_delta_pct=Decimal("2.00")
        )
    else: # CUSTOM
        adjustments = req.adjustments or ScenarioAdjustments()

    # 3. Create stressed copy of base forecast request
    stressed_request: SeasonalForecastRequest = copy.deepcopy(req.base_forecast_request)

    # Apply revenue change to crop selling prices and collection delay
    rev_multiplier = Decimal("1.0") + (adjustments.revenue_change_pct / Decimal("100"))
    rev_multiplier = max(Decimal("0.1"), rev_multiplier) # prevent negative prices

    for crop in stressed_request.crop_assumptions:
        crop.selling_price_per_ton_uzs = round_money(crop.selling_price_per_ton_uzs * rev_multiplier)
        crop.collection_delay_months += adjustments.collection_delay_months

    # Apply cost change to seasonality arrays
    cost_multiplier = Decimal("1.0") + (adjustments.cost_change_pct / Decimal("100"))
    cost_multiplier = max(Decimal("0.1"), cost_multiplier)

    costs = stressed_request.cost_assumptions
    costs.seeds_planting_by_month = [round_money(c * cost_multiplier) for c in costs.seeds_planting_by_month]
    costs.fertilizer_chemicals_by_month = [round_money(c * cost_multiplier) for c in costs.fertilizer_chemicals_by_month]
    costs.fuel_lubricants_by_month = [round_money(c * cost_multiplier) for c in costs.fuel_lubricants_by_month]
    costs.labor_salaries_by_month = [round_money(c * cost_multiplier) for c in costs.labor_salaries_by_month]
    costs.fixed_monthly_opex_uzs = round_money(costs.fixed_monthly_opex_uzs * cost_multiplier)

    # Apply interest rate delta to debt service if applicable
    if adjustments.interest_rate_delta_pct != Decimal("0.00"):
        debt_multiplier = Decimal("1.0") + (adjustments.interest_rate_delta_pct / Decimal("100"))
        stressed_request.existing_monthly_debt_service = [
            round_money(d * debt_multiplier) for d in stressed_request.existing_monthly_debt_service
        ]

    # 4. Recompute stressed forecast from underlying models
    stressed_forecast = calculate_seasonal_forecast(stressed_request)

    # 5. Compute comparative variances
    variance_net_cf = round_money(stressed_forecast.net_annual_cash_flow - base_forecast.net_annual_cash_flow)
    variance_closing = round_money(stressed_forecast.final_closing_balance - base_forecast.final_closing_balance)

    variance_dscr: Decimal | None = None
    if stressed_forecast.annual_dscr is not None and base_forecast.annual_dscr is not None:
        variance_dscr = round_ratio(stressed_forecast.annual_dscr - base_forecast.annual_dscr)

    # 6. Solvency impact assessment
    if stressed_forecast.months_in_deficit == 0 and (stressed_forecast.annual_dscr is None or stressed_forecast.annual_dscr >= Decimal("1.250")):
        solvency_impact = "RESILIENT (Korxona shoklarga to'liq bardoshli)"
    elif stressed_forecast.months_in_deficit > 0 or (stressed_forecast.annual_dscr is not None and stressed_forecast.annual_dscr < Decimal("1.000")):
        solvency_impact = "CRITICAL_DEFICIT (Kritik kassa uzilishi va defolt xatari)"
    else:
        solvency_impact = "VULNERABLE (Mo''tadil zaiflik — likvidlik monitoringi talab etiladi)"

    # Formulate risk summary in Uzbek
    risk_summary_uz: List[str] = []
    if adjustments.revenue_change_pct != Decimal("0.00"):
        sign = "+" if adjustments.revenue_change_pct > 0 else ""
        risk_summary_uz.append(f"Daromad o'zgarishi: {sign}{adjustments.revenue_change_pct}%")
    if adjustments.cost_change_pct != Decimal("0.00"):
        sign = "+" if adjustments.cost_change_pct > 0 else ""
        risk_summary_uz.append(f"Xarajatlar inflyatsiyasi: {sign}{adjustments.cost_change_pct}%")
    if adjustments.collection_delay_months > 0:
        risk_summary_uz.append(f"Tushumlar kechikishi: +{adjustments.collection_delay_months} oy")

    risk_summary_uz.append(
        f"Kassa qoldig'i farqi: {variance_closing:,.2f} UZS; Defitsitli oylar: {stressed_forecast.months_in_deficit} oy"
    )

    return ScenarioComparisonResponse(
        scenario_type=req.scenario_type,
        adjustments_applied=adjustments,
        baseline=base_forecast,
        stressed=stressed_forecast,
        variance_net_cash_flow=variance_net_cf,
        variance_closing_balance=variance_closing,
        variance_dscr=variance_dscr,
        solvency_impact=solvency_impact,
        risk_summary_uz=risk_summary_uz,
        calculation_version="2.0.0"
    )
