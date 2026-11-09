"""
AgroHisob CFO - Unit Tests for Indicative DCF Valuation & Sensitivity (Assignment 6, Module A)
"""

from decimal import Decimal
from app.collateral.schemas import IndicativeValuationRequest
from app.collateral.sensitivity import run_collateral_sensitivity_analysis
from app.collateral.valuation import calculate_indicative_lease_valuation


def test_dcf_valuation_finite_horizon_and_bonitet():
    req = IndicativeValuationRequest(
        area_hectares=65.0,
        soil_bonitet_score=68,
        remaining_lease_years=25,
        normative_annual_net_benefit_per_ha_uzs=Decimal("8500000.00"),
        discount_rate_pct=Decimal("16.00"),
        annual_benefit_growth_pct=Decimal("2.00"),
        target_ltv_pct=Decimal("65.00"),
    )

    res = calculate_indicative_lease_valuation(req)

    # Bonitet adjustment factor: 68 / 65 ~ 1.046
    assert res.bonitet_adjustment_factor > 1.0
    assert len(res.cash_flow_schedule) == 25
    assert res.indicative_market_value_uzs > 0

    # Max pledge value strictly equals market_value * ltv_pct
    expected_pledge = (res.indicative_market_value_uzs * (Decimal("65.00") / Decimal("100.00"))).quantize(
        Decimal("0.01")
    )
    assert abs(res.max_pledge_value_uzs - expected_pledge) <= Decimal("0.05")

    # Verify zero terminal value: last period cumulative PV exactly equals indicative_market_value_uzs
    last_pv = res.cash_flow_schedule[-1].cumulative_pv_uzs
    assert abs(last_pv - res.indicative_market_value_uzs) <= Decimal("0.05")


def test_collateral_sensitivity_analysis():
    req = IndicativeValuationRequest(
        area_hectares=65.0,
        soil_bonitet_score=68,
        remaining_lease_years=25,
        normative_annual_net_benefit_per_ha_uzs=Decimal("8500000.00"),
        discount_rate_pct=Decimal("16.00"),
        annual_benefit_growth_pct=Decimal("2.00"),
        target_ltv_pct=Decimal("65.00"),
    )

    sens = run_collateral_sensitivity_analysis(req)

    # Base vs Optimistic vs Pessimistic
    assert sens.optimistic_scenario.indicative_valuation_uzs > sens.base_scenario.indicative_valuation_uzs
    assert sens.pessimistic_scenario.indicative_valuation_uzs < sens.base_scenario.indicative_valuation_uzs

    # Volatility range = Optimistic - Pessimistic
    expected_range = sens.optimistic_scenario.indicative_valuation_uzs - sens.pessimistic_scenario.indicative_valuation_uzs
    assert sens.volatility_range_uzs == expected_range
    assert len(sens.key_risk_drivers_uz) >= 3
