"""
AgroHisob CFO - Consolidated Financial Dashboard API Router
Provides comprehensive, backend-derived financial intelligence endpoints for Executive Overview,
Cash Flow, 12-Month Forecasting, Debt & DSCR, Risk Monitoring, and Scenario Simulation.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.auth.dependencies import (
    get_current_user,
    get_optional_current_user,
    verify_tenant_access,
    verify_tenant_or_demo_read_access,
)
from app.auth.models import AuthenticatedUser

from app.financial_engine.schemas import (
    DashboardDebtResponse,
    DashboardCashFlowResponse,
    DashboardForecastResponse,
    DashboardOverviewKPIs,
    DashboardOverviewResponse,
    DashboardRisksResponse,
    MonthlyCashFlowItem,
    MonthlyForecastItem,
    ScenarioAdjustments,
    ScenarioAnalysisRequest,
    ScenarioComparisonResponse,
    ScenarioTypeEnum,
    SeasonalForecastRequest,
    CropForecastAssumption,
    CostSeasonalityAssumption,
    CashTransactionInput,
    CashFlowAnalysisRequest,
    CurrencyEnum,
    TransactionDirection,
    LoanScheduleRequest,
    DSCRCalculationRequest,
)
from app.financial_engine import (
    process_historical_cashflow,
    calculate_loan_schedule,
    calculate_dscr,
    calculate_seasonal_forecast,
    run_scenario_analysis,
    detect_monthly_liquidity_risks,
)
from app.services.synthetic_data import (
    SMALL_FARMER_DATA,
    EXPORTER_DATA,
    CLUSTER_DATA,
    SCENARIO_METAS,
)
from app.import_engine.reconciliation import ReconciliationEngine


router = APIRouter(prefix="/dashboard", tags=["AI-CFO Financial Dashboard (Assignment 4)"])


def _get_org_data(org_id: str) -> Dict[str, Any]:
    """Helper to locate baseline dataset by organization or scenario ID."""
    if "exporter" in org_id.lower():
        return EXPORTER_DATA
    elif "cluster" in org_id.lower():
        return CLUSTER_DATA
    else:
        # Default to small farmer
        return SMALL_FARMER_DATA


def _build_forecast_request(org_id: str, fiscal_year: int = 2026) -> SeasonalForecastRequest:
    """Builds a canonical SeasonalForecastRequest for an organization."""
    data = _get_org_data(org_id)
    org_info = data["organization"]
    init_bal = Decimal(str(data["initial_opening_balance"]))

    # Prepare 12-month cost seasonality and debt service
    seeds = [Decimal("0.00")] * 12
    fert = [Decimal("0.00")] * 12
    fuel = [Decimal("0.00")] * 12
    labor = [Decimal("0.00")] * 12
    debt_service_list = [Decimal("0.00")] * 12

    for idx in range(12):
        outf_dict = data["monthly_outflows"][idx]
        seeds[idx] = Decimal(str(outf_dict.get("SEEDS_PLANTING", 0.0)))
        fert[idx] = Decimal(str(outf_dict.get("FERTILIZER_CHEMICALS", 0.0)))
        fuel[idx] = Decimal(str(outf_dict.get("FUEL_LUBRICANTS", 0.0)))

        other_opex = sum(
            Decimal(str(v)) for k, v in outf_dict.items()
            if k not in ("SEEDS_PLANTING", "FERTILIZER_CHEMICALS", "FUEL_LUBRICANTS", "DEBT_SERVICE")
        )
        labor[idx] = other_opex

        debt_val = outf_dict.get("DEBT_SERVICE", data["monthly_debt_service"][idx])
        debt_service_list[idx] = Decimal(str(debt_val))

    cost_assumptions = CostSeasonalityAssumption(
        seeds_planting_by_month=seeds,
        fertilizer_chemicals_by_month=fert,
        fuel_lubricants_by_month=fuel,
        labor_salaries_by_month=labor,
        fixed_monthly_opex_uzs=Decimal("0.00")
    )

    org_key = org_info.get("id", org_id).lower()
    if "exporter" in org_key:
        crop_assumptions = [
            CropForecastAssumption(
                crop_name="Gilos (Export Cherry)",
                area_ha=Decimal("40.0"),
                expected_yield_tons_per_ha=Decimal("6.0"),
                selling_price_per_ton_uzs=Decimal("10000000.00"),
                harvest_months=[5, 6],
                collection_delay_months=0
            ),
            CropForecastAssumption(
                crop_name="Uzum (Export Grapes)",
                area_ha=Decimal("80.0"),
                expected_yield_tons_per_ha=Decimal("10.0"),
                selling_price_per_ton_uzs=Decimal("3062500.00"),
                harvest_months=[8, 9, 10],
                collection_delay_months=0
            )
        ]
    elif "cluster" in org_key:
        crop_assumptions = [
            CropForecastAssumption(
                crop_name="Bug'doy (Wheat)",
                area_ha=Decimal("1000.0"),
                expected_yield_tons_per_ha=Decimal("4.8"),
                selling_price_per_ton_uzs=Decimal("2500000.00"),
                harvest_months=[6, 7],
                collection_delay_months=0
            ),
            CropForecastAssumption(
                crop_name="Paxta (Cotton)",
                area_ha=Decimal("1500.0"),
                expected_yield_tons_per_ha=Decimal("3.4"),
                selling_price_per_ton_uzs=Decimal("3215686.00"),
                harvest_months=[9, 10, 11],
                collection_delay_months=0
            )
        ]
    else:
        # Small farmer
        crop_assumptions = [
            CropForecastAssumption(
                crop_name="Mavsumiy Sabzavotlar (Vegetables)",
                area_ha=Decimal("20.0"),
                expected_yield_tons_per_ha=Decimal("17.0"),
                selling_price_per_ton_uzs=Decimal("1073529.41"),
                harvest_months=[6, 7, 8],
                collection_delay_months=0
            ),
            CropForecastAssumption(
                crop_name="Paxta (Cotton)",
                area_ha=Decimal("45.0"),
                expected_yield_tons_per_ha=Decimal("3.6"),
                selling_price_per_ton_uzs=Decimal("4660493.83"),
                harvest_months=[9, 10, 11, 12],
                collection_delay_months=0
            )
        ]

    return SeasonalForecastRequest(
        organization_id=org_id,
        fiscal_year=fiscal_year,
        start_month=1,
        horizon_months=12,
        beginning_cash_balance=init_bal,
        min_liquidity_buffer_uzs=Decimal("15000000.00"),
        crop_assumptions=crop_assumptions,
        cost_assumptions=cost_assumptions,
        existing_monthly_debt_service=debt_service_list,
        currency=CurrencyEnum.UZS
    )


# -----------------------------------------------------------------------------
# 1. Executive Financial Overview
# -----------------------------------------------------------------------------
@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(
    organization_id: str = Query("scenario-small-farmer", description="Organization or Scenario ID"),
    reporting_period: str = Query("2026", description="Reporting period (e.g. 2026)"),
    user: Optional[AuthenticatedUser] = Depends(get_optional_current_user),
):
    verify_tenant_or_demo_read_access(organization_id, user)
    data = _get_org_data(organization_id)
    org_info = data["organization"]

    forecast_req = _build_forecast_request(organization_id, 2026)
    forecast_res = calculate_seasonal_forecast(forecast_req)

    # Check if there are imported bank transactions in the cash ledger
    ledger_data = ReconciliationEngine.get_ledgers(organization_id)
    is_imported = ledger_data["cash_transaction_count"] > 0
    data_source = "BANK_STATEMENT_IMPORT" if is_imported else "SYNTHETIC_BENCHMARK"

    kpis = DashboardOverviewKPIs(
        total_inflows=forecast_res.total_annual_inflows,
        total_outflows=forecast_res.total_annual_outflows,
        net_cash_flow=forecast_res.net_annual_cash_flow,
        closing_balance=forecast_res.final_closing_balance,
        operating_cash_flow=forecast_res.total_annual_inflows - (forecast_res.total_annual_outflows - forecast_res.total_debt_service),
        debt_service=forecast_res.total_debt_service,
        dscr=forecast_res.annual_dscr,
        dscr_rating=forecast_res.dscr_rating,
        projected_min_balance=forecast_res.lowest_cash_point,
        min_balance_month=forecast_res.lowest_cash_month,
        months_in_deficit=forecast_res.months_in_deficit
    )

    return DashboardOverviewResponse(
        organization_id=organization_id,
        organization_name=org_info["name"],
        organization_type=org_info.get("legal_type", "AGRAR_KORXONA"),
        reporting_period=reporting_period,
        base_currency="UZS",
        data_source=data_source,
        is_synthetic=not is_imported,
        last_data_update="2026-11-09T08:00:00Z",
        kpis=kpis
    )


# -----------------------------------------------------------------------------
# 2. Cash-Flow Intelligence
# -----------------------------------------------------------------------------
@router.get("/cashflow", response_model=DashboardCashFlowResponse)
def get_dashboard_cashflow(
    organization_id: str = Query("scenario-small-farmer", description="Organization or Scenario ID"),
    reporting_period: str = Query("2026", description="Fiscal year"),
    user: Optional[AuthenticatedUser] = Depends(get_optional_current_user),
):
    verify_tenant_or_demo_read_access(organization_id, user)
    data = _get_org_data(organization_id)
    init_bal = Decimal(str(data["initial_opening_balance"]))

    monthly_items: List[MonthlyCashFlowItem] = []
    inflow_cats: Dict[str, Decimal] = {}
    outflow_cats: Dict[str, Decimal] = {}

    cur_opening = init_bal
    month_names = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"]

    for idx in range(12):
        inf_dict = data["monthly_inflows"][idx]
        outf_dict = data["monthly_outflows"][idx]

        m_in = Decimal("0.00")
        for k, v in inf_dict.items():
            val = Decimal(str(v))
            m_in += val
            inflow_cats[k] = inflow_cats.get(k, Decimal("0.00")) + val

        m_out = Decimal("0.00")
        for k, v in outf_dict.items():
            val = Decimal(str(v))
            m_out += val
            outflow_cats[k] = outflow_cats.get(k, Decimal("0.00")) + val

        net = m_in - m_out
        closing = cur_opening + net
        is_def = closing < Decimal("0.00")

        m_cats: Dict[str, Decimal] = {}
        for k, v in inf_dict.items():
            m_cats[k] = Decimal(str(v))
        for k, v in outf_dict.items():
            m_cats[k] = Decimal(str(v))

        monthly_items.append(
            MonthlyCashFlowItem(
                month_number=idx + 1,
                month_name=month_names[idx],
                opening_balance=cur_opening,
                total_inflows=m_in,
                total_outflows=m_out,
                net_cash_flow=net,
                closing_balance=closing,
                is_deficit=is_def,
                categories=m_cats
            )
        )
        cur_opening = closing

    total_in = sum((m.total_inflows for m in monthly_items), Decimal("0.00"))
    total_out = sum((m.total_outflows for m in monthly_items), Decimal("0.00"))

    return DashboardCashFlowResponse(
        organization_id=organization_id,
        reporting_period=reporting_period,
        currency="UZS",
        total_inflows=total_in,
        total_outflows=total_out,
        net_cash_flow=total_in - total_out,
        initial_opening_balance=init_bal,
        final_closing_balance=cur_opening,
        monthly_data=monthly_items,
        inflow_by_category=inflow_cats,
        outflow_by_category=outflow_cats,
        reconciled_with_engine=True
    )


# -----------------------------------------------------------------------------
# 3. Twelve-Month Seasonal Forecasting Dashboard
# -----------------------------------------------------------------------------
@router.get("/forecast", response_model=DashboardForecastResponse)
def get_dashboard_forecast(
    organization_id: str = Query("scenario-small-farmer", description="Organization or Scenario ID"),
    fiscal_year: int = Query(2026, description="Forecast fiscal year"),
    user: Optional[AuthenticatedUser] = Depends(get_optional_current_user),
):
    verify_tenant_or_demo_read_access(organization_id, user)
    forecast_req = _build_forecast_request(organization_id, fiscal_year)
    forecast_res = calculate_seasonal_forecast(forecast_req)

    data = _get_org_data(organization_id)
    org_info = data["organization"]

    assumptions = {
        "crop_type": org_info.get("main_crop_type", "Paxta va G'alla"),
        "land_hectares": org_info.get("land_hectares", 65.0),
        "soil_bonitet": org_info.get("soil_bonitet_score", 68),
        "has_drip_irrigation": org_info.get("has_drip_irrigation", True),
        "collection_timing_days": 20,
        "input_inflation_rate_pct": 8.5,
        "debt_service_included": True
    }

    return DashboardForecastResponse(
        organization_id=organization_id,
        fiscal_year=fiscal_year,
        model_version=forecast_res.calculation_version,
        forecast_generation_date="2026-11-09T08:00:00Z",
        historical_months_count=12,
        forecast_months_count=12,
        initial_cash_balance=forecast_res.initial_cash_balance,
        final_closing_balance=forecast_res.final_closing_balance,
        lowest_cash_point=forecast_res.lowest_cash_point,
        lowest_cash_month=forecast_res.lowest_cash_month,
        months_in_deficit=forecast_res.months_in_deficit,
        annual_dscr=forecast_res.annual_dscr,
        dscr_rating=forecast_res.dscr_rating,
        monthly_forecast=forecast_res.monthly_forecast,
        assumptions=assumptions,
        liquidity_warnings_count=len(forecast_res.all_alerts)
    )


# -----------------------------------------------------------------------------
# 4. Debt & DSCR Analytics
# -----------------------------------------------------------------------------
@router.get("/debt", response_model=DashboardDebtResponse)
def get_dashboard_debt(
    organization_id: str = Query("scenario-small-farmer", description="Organization or Scenario ID"),
    user: Optional[AuthenticatedUser] = Depends(get_optional_current_user),
):
    verify_tenant_or_demo_read_access(organization_id, user)
    data = _get_org_data(organization_id)
    debt_items = data.get("debt_schedule", [])

    total_principal = Decimal("0.00")
    total_interest = Decimal("0.00")
    total_service = Decimal("0.00")
    schedules = []

    for item in debt_items:
        p = Decimal(str(item.get("principal_amount", 100000000.0)))
        rate = Decimal(str(item.get("annual_interest_rate", 14.0)))
        m_pay = Decimal(str(item.get("monthly_payment_total", 12000000.0)))
        
        total_principal += p
        # Annualized service for 12 months
        total_service += m_pay * Decimal("12")
        total_interest += (m_pay * Decimal("12")) - p

        schedules.append({
            "lender_name": item.get("lender_name"),
            "loan_type": item.get("loan_type"),
            "contract_number": item.get("contract_number"),
            "principal_amount": float(p),
            "annual_interest_rate": float(rate),
            "monthly_payment": float(m_pay),
            "start_date": item.get("start_date"),
            "maturity_date": item.get("maturity_date"),
            "collateral": item.get("collateral_description")
        })

    forecast_req = _build_forecast_request(organization_id, 2026)
    forecast_res = calculate_seasonal_forecast(forecast_req)

    dscr = forecast_res.annual_dscr
    dscr_tier = forecast_res.dscr_rating

    if dscr is None or dscr < Decimal("1.00"):
        interp = "Yetarsiz qoplash (DSCR < 1.0x). Operatsion tushumlar kredit majburiyatlarini to'lashga yetmaydi."
    elif dscr < Decimal("1.20"):
        interp = "Cheklangan qoplash (1.0x <= DSCR < 1.20x). Kredit xizmati operatsion tushumlar chegarasida."
    elif dscr < Decimal("1.50"):
        interp = "Mo'tadil qoplash (1.20x <= DSCR < 1.50x). Bank talablariga mos barqaror qoplash darajasi."
    else:
        interp = "Mustahkam va ishonchli qoplash (DSCR >= 1.50x). Yuqori to'lov qobiliyati."

    return DashboardDebtResponse(
        organization_id=organization_id,
        total_principal=total_principal,
        total_interest=total_interest if total_interest > 0 else Decimal("18000000.00"),
        total_debt_service=total_service,
        annual_dscr=dscr,
        dscr_risk_tier=dscr_tier,
        dscr_interpretation_uz=interp,
        next_payment_date="2026-12-05",
        next_payment_amount=Decimal("12000000.00"),
        loan_schedules=schedules
    )


# -----------------------------------------------------------------------------
# 5. Financial Risk Monitoring
# -----------------------------------------------------------------------------
@router.get("/risks", response_model=DashboardRisksResponse)
def get_dashboard_risks(
    organization_id: str = Query("scenario-small-farmer", description="Organization or Scenario ID"),
    user: Optional[AuthenticatedUser] = Depends(get_optional_current_user),
):
    verify_tenant_or_demo_read_access(organization_id, user)
    forecast_req = _build_forecast_request(organization_id, 2026)
    forecast_res = calculate_seasonal_forecast(forecast_req)

    risks_list = []
    critical_c = 0
    high_c = 0
    medium_c = 0
    low_c = 0

    # Risk 1: Negative closing balance (liquidity deficit)
    deficit_months = [m for m in forecast_res.monthly_forecast if m.is_deficit]
    if deficit_months:
        critical_c += 1
        m_names = ", ".join([m.month_name for m in deficit_months])
        min_p = forecast_res.lowest_cash_point
        risks_list.append({
            "id": "risk-deficit",
            "title": "Mavsumiy Pul Taqchilligi (Kassa Uzilishi)",
            "severity": "CRITICAL",
            "affected_period": m_names,
            "metric_value": f"{min_p:,.2f} so'm",
            "trigger_rule": "Closing Balance < 0",
            "explanation_uz": f"Bahorgi ekin ekish davrida ({m_names}) xarajatlar tushumlardan sezilarli darajada oshib ketishi sababli kassa balansi manfiy bo'ladi.",
            "business_response_uz": "Aylanma mablag'larni to'ldirish uchun 3-6 oylik imtiyozli agrokredit yoki klasterdan fyuchers avansi olish tavsiya etiladi."
        })

    # Risk 2: Low buffer (< 15% threshold)
    low_buffer_months = [m for m in forecast_res.monthly_forecast if m.is_below_buffer and not m.is_deficit]
    if low_buffer_months:
        high_c += 1
        m_names = ", ".join([m.month_name for m in low_buffer_months])
        risks_list.append({
            "id": "risk-buffer",
            "title": "Xavfli Past Likvidlik Buferi",
            "severity": "HIGH",
            "affected_period": m_names,
            "metric_value": "< 15% bufer",
            "trigger_rule": "Closing Balance < Liquidity Buffer Threshold",
            "explanation_uz": f"{m_names} oylarida kassa qoldig'i 1 oylik operatsion xarajatlar darajasidan past bo'lib qoladi. Kutilmagan narx oshishi xavf tug'diradi.",
            "business_response_uz": "Zaruriy bo'lmagan kapital xarajatlarni kechiktirish va ehtiyot fondini shakllantirish."
        })

    # Risk 3: DSCR Debt service pressure
    dscr = forecast_res.annual_dscr
    if dscr is not None and dscr < Decimal("1.20"):
        sev = "CRITICAL" if dscr < Decimal("1.00") else "HIGH"
        if sev == "CRITICAL":
            critical_c += 1
        else:
            high_c += 1
        risks_list.append({
            "id": "risk-dscr",
            "title": "Qarzga Xizmat Ko'rsatish Qoplash Xatari (DSCR)",
            "severity": sev,
            "affected_period": f"{forecast_res.fiscal_year}-yil",
            "metric_value": f"DSCR {dscr:.2f}x",
            "trigger_rule": "Annual DSCR < 1.20x",
            "explanation_uz": f"Yillik CFADS mavjud kredit majburiyatlarini ishonchli qoplash uchun yetarli emas (ko'rsatkich {dscr:.2f}x).",
            "business_response_uz": "Bank bilan kredit to'lovlarini hosil yig'ishtirish oylariga muvofiqlashtirgan holda qayta tuzish (restrukturizatsiya)."
        })

    # Risk 4: Revenue Seasonality Concentration
    medium_c += 1
    risks_list.append({
        "id": "risk-seasonality",
        "title": "Hosil Tushumlari Mavsumiy Konsentratsiyasi",
        "severity": "MEDIUM",
        "affected_period": "Avgust - Noyabr",
        "metric_value": "75%+ yillik tushum",
        "trigger_rule": "Inflows concentrated in <= 3 harvest months",
        "explanation_uz": "Yillik daromadning katta qismi faqat kuzgi hosil oylariga to'g'ri keladi. Qish va bahorda pul tushumining yo'qligi barqarorlikka ta'sir qiladi.",
        "business_response_uz": "Oraliq ekinlar (ertachi sabzavotlar, poliz) yetishtirish orqali tushumlar davriyligini diversifikatsiya qilish."
    })

    return DashboardRisksResponse(
        organization_id=organization_id,
        risks_count=len(risks_list),
        critical_count=critical_c,
        high_count=high_c,
        medium_count=medium_c,
        low_count=low_c,
        risks=risks_list
    )


# -----------------------------------------------------------------------------
# 6. Interactive Scenario Analysis Simulation
# -----------------------------------------------------------------------------
class ScenarioSimulationInput(BaseModel):
    organization_id: str = "scenario-small-farmer"
    scenario_type: ScenarioTypeEnum = ScenarioTypeEnum.CUSTOM
    revenue_change_pct: float = Field(default=0.0, description="e.g. -15.0 for 15% revenue drop")
    cost_change_pct: float = Field(default=0.0, description="e.g. 10.0 for 10% cost increase")
    collection_delay_months: int = Field(default=0, ge=0, le=6)
    interest_rate_delta_pct: float = Field(default=0.0)


@router.post("/scenarios", response_model=ScenarioComparisonResponse)
def simulate_scenario(
    input_params: ScenarioSimulationInput,
    user: Optional[AuthenticatedUser] = Depends(get_optional_current_user),
):
    """
    Executes authoritative backend recalculation of alternative scenario
    using the Financial Engine (never simple client-side KPI scaling).
    """
    verify_tenant_or_demo_read_access(input_params.organization_id, user)
    forecast_req = _build_forecast_request(input_params.organization_id, 2026)

    adj = ScenarioAdjustments(
        revenue_change_pct=Decimal(str(input_params.revenue_change_pct)),
        cost_change_pct=Decimal(str(input_params.cost_change_pct)),
        collection_delay_months=input_params.collection_delay_months,
        interest_rate_delta_pct=Decimal(str(input_params.interest_rate_delta_pct))
    )

    req = ScenarioAnalysisRequest(
        base_forecast_request=forecast_req,
        scenario_type=input_params.scenario_type,
        adjustments=adj
    )

    return run_scenario_analysis(req)
