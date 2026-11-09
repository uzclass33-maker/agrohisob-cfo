import pytest
from decimal import Decimal
from app.financial_engine.schemas import (
    SeasonalForecastRequest, CropForecastAssumption, CostSeasonalityAssumption,
    ScenarioAnalysisRequest, ScenarioTypeEnum, ScenarioAdjustments
)
from app.financial_engine.scenarios import run_scenario_analysis

@pytest.fixture
def base_request():
    crops = [
        CropForecastAssumption(
            crop_name="Gilos (Cherry)",
            area_ha=Decimal("25.0"),
            expected_yield_tons_per_ha=Decimal("8.0"), # 200 tons
            selling_price_per_ton_uzs=Decimal("20000000.00"), # 4,000,000,000 UZS
            harvest_months=[5, 6],
            collection_delay_months=0
        )
    ]
    fuel = [Decimal("10000000.00")] * 12
    labor = [Decimal("30000000.00")] * 12
    costs = CostSeasonalityAssumption(
        fuel_lubricants_by_month=fuel,
        labor_salaries_by_month=labor,
        fixed_monthly_opex_uzs=Decimal("15000000.00")
    )
    debt = [Decimal("25000000.00")] * 12
    return SeasonalForecastRequest(
        organization_id="org-exporter-test",
        beginning_cash_balance=Decimal("100000000.00"),
        crop_assumptions=crops,
        cost_assumptions=costs,
        existing_monthly_debt_service=debt
    )

def test_optimistic_scenario_analysis(base_request):
    """Verifies that the Optimistic scenario genuinely increases revenues and improves closing balance."""
    req = ScenarioAnalysisRequest(
        base_forecast_request=base_request,
        scenario_type=ScenarioTypeEnum.OPTIMISTIC
    )
    res = run_scenario_analysis(req)
    assert res.stressed.total_annual_inflows > res.baseline.total_annual_inflows
    assert res.stressed.total_annual_outflows < res.baseline.total_annual_outflows
    assert res.variance_closing_balance > Decimal("0.00")
    assert res.variance_net_cash_flow > Decimal("0.00")

def test_pessimistic_scenario_analysis(base_request):
    """Verifies that the Pessimistic scenario depresses revenues, inflates costs, and detects solvency risk."""
    req = ScenarioAnalysisRequest(
        base_forecast_request=base_request,
        scenario_type=ScenarioTypeEnum.PESSIMISTIC
    )
    res = run_scenario_analysis(req)
    assert res.stressed.total_annual_inflows < res.baseline.total_annual_inflows
    assert res.stressed.total_annual_outflows > res.baseline.total_annual_outflows
    assert res.variance_closing_balance < Decimal("0.00")
    assert len(res.risk_summary_uz) > 0

def test_custom_scenario_analysis(base_request):
    """Verifies custom scenario adjustments (revenue -15%, cost +10%)."""
    adj = ScenarioAdjustments(
        revenue_change_pct=Decimal("-15.00"),
        cost_change_pct=Decimal("10.00"),
        collection_delay_months=1,
        interest_rate_delta_pct=Decimal("0.00")
    )
    req = ScenarioAnalysisRequest(
        base_forecast_request=base_request,
        scenario_type=ScenarioTypeEnum.CUSTOM,
        adjustments=adj
    )
    res = run_scenario_analysis(req)
    assert res.adjustments_applied.revenue_change_pct == Decimal("-15.00")
    assert res.stressed.final_closing_balance < res.baseline.final_closing_balance
