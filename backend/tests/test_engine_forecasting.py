import pytest
from decimal import Decimal
from app.financial_engine.schemas import (
    SeasonalForecastRequest, CropForecastAssumption, CostSeasonalityAssumption
)
from app.financial_engine.forecasting import calculate_seasonal_forecast

def test_seasonal_forecast_cotton_and_wheat_continuity():
    """
    Tests 12-month forecast for a 50 ha farm producing cotton (harvest Sep-Oct) and wheat (harvest Jun-Jul).
    Verifies roll-forward continuity across all 12 months.
    """
    crops = [
        CropForecastAssumption(
            crop_name="Bug'doy (Wheat)",
            area_ha=Decimal("20.0"),
            expected_yield_tons_per_ha=Decimal("4.5"), # 90 tons
            selling_price_per_ton_uzs=Decimal("2500000.00"), # 225M UZS
            harvest_months=[6, 7], # Jun, Jul
            collection_delay_months=0
        ),
        CropForecastAssumption(
            crop_name="Paxta (Cotton)",
            area_ha=Decimal("30.0"),
            expected_yield_tons_per_ha=Decimal("3.0"), # 90 tons
            selling_price_per_ton_uzs=Decimal("8000000.00"), # 720M UZS
            harvest_months=[9, 10], # Sep, Oct
            collection_delay_months=1 # Payout in Oct, Nov
        )
    ]

    # Seasonality costs: heavy in March-April (planting/fertilizer)
    seeds = [Decimal("0.00")] * 12
    seeds[2] = Decimal("25000000.00") # March
    fert = [Decimal("0.00")] * 12
    fert[3] = Decimal("30000000.00") # April
    fuel = [Decimal("10000000.00")] * 12
    labor = [Decimal("15000000.00")] * 12

    costs = CostSeasonalityAssumption(
        seeds_planting_by_month=seeds,
        fertilizer_chemicals_by_month=fert,
        fuel_lubricants_by_month=fuel,
        labor_salaries_by_month=labor,
        fixed_monthly_opex_uzs=Decimal("5000000.00")
    )

    debt = [Decimal("10000000.00")] * 12 # 10M / month debt service

    req = SeasonalForecastRequest(
        organization_id="org-farm-test",
        fiscal_year=2026,
        beginning_cash_balance=Decimal("40000000.00"),
        min_liquidity_buffer_uzs=Decimal("15000000.00"),
        crop_assumptions=crops,
        cost_assumptions=costs,
        existing_monthly_debt_service=debt
    )

    res = calculate_seasonal_forecast(req)

    assert len(res.monthly_forecast) == 12
    assert res.initial_cash_balance == Decimal("40000000.00")

    # Invariant: Opening(t+1) == Closing(t) for all months
    for i in range(11):
        cur = res.monthly_forecast[i]
        nxt = res.monthly_forecast[i+1]
        assert nxt.opening_balance == cur.closing_balance
        assert cur.closing_balance == cur.opening_balance + cur.net_cash_flow

    # Verify final closing balance matches annual net cash flow identity
    expected_closing = res.initial_cash_balance + res.total_annual_inflows - res.total_annual_outflows
    assert res.final_closing_balance == expected_closing

    # Verify collection delay for cotton: delivered Sep/Oct, paid Oct/Nov
    october_item = res.monthly_forecast[9] # Month 10
    assert october_item.projected_inflows > Decimal("0.00")

def test_seasonal_forecast_zero_revenue_spring_deficit():
    """
    Tests spring liquidity gap (deficit) detection when farming expenditures occur before harvest.
    """
    crops = [
        CropForecastAssumption(
            crop_name="Late Vegetables",
            area_ha=Decimal("10.0"),
            expected_yield_tons_per_ha=Decimal("20.0"),
            selling_price_per_ton_uzs=Decimal("1000000.00"),
            harvest_months=[8, 9] # Aug, Sep
        )
    ]
    # Heavy spending in Jan-Feb with minimal starting cash
    costs = CostSeasonalityAssumption(
        fixed_monthly_opex_uzs=Decimal("20000000.00") # 20M per month
    )
    req = SeasonalForecastRequest(
        organization_id="org-deficit-test",
        beginning_cash_balance=Decimal("10000000.00"), # 10M cash, 20M opex -> Month 1 deficit
        crop_assumptions=crops,
        cost_assumptions=costs
    )
    res = calculate_seasonal_forecast(req)
    # Month 1: 10M - 20M = -10M
    m1 = res.monthly_forecast[0]
    assert m1.closing_balance == Decimal("-10000000.00")
    assert m1.is_deficit is True
    assert res.months_in_deficit >= 1
    # Check that alert was triggered
    deficit_alerts = [a for a in m1.alerts if a.warning_type == "NEGATIVE_CASH"]
    assert len(deficit_alerts) == 1
    assert deficit_alerts[0].severity == "CRITICAL"
