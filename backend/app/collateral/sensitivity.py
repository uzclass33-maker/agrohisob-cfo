"""
AgroHisob CFO - Collateral Valuation Sensitivity Engine (Assignment 6, Module A)
Re-evaluates indicative DCF present value under Base, Optimistic, and Pessimistic scenarios.
Strictly recalculates underlying cash flows and discount rates across scenarios.
"""

from decimal import Decimal
from app.collateral.schemas import (
    CollateralSensitivityAnalysis,
    IndicativeValuationRequest,
    ValuationSensitivityCase,
)
from app.collateral.valuation import calculate_indicative_lease_valuation


def run_collateral_sensitivity_analysis(
    req: IndicativeValuationRequest
) -> CollateralSensitivityAnalysis:
    """
    Executes multi-scenario sensitivity recalculation:
    1. Base Case: user-provided inputs.
    2. Optimistic Case: Discount rate - 200 bps, Net benefit + 15%.
    3. Pessimistic Case: Discount rate + 300 bps, Net benefit - 20%.
    """
    # 1. Base Case
    base_res = calculate_indicative_lease_valuation(req)
    base_pv = base_res.indicative_present_value_uzs
    base_sec = base_res.indicative_secured_amount_uzs

    base_case = ValuationSensitivityCase(
        scenario_name_uz="Bazaviy Ssenariy",
        discount_rate_pct=req.discount_rate_pct,
        benefit_growth_pct=req.annual_benefit_growth_pct,
        annual_attributable_benefit_uzs=base_res.annual_attributable_net_benefit_uzs,
        indicative_present_value_uzs=base_pv,
        indicative_secured_amount_uzs=base_sec,
        variance_from_base_pct=0.0,
        indicative_valuation_uzs=base_pv,
        max_pledge_value_uzs=base_sec,
        scenario_label_uz="Bazaviy Ssenariy",
        description_uz="Standart agrotexnik sharoit va amaldagi foiz stavkalari.",
        variance_pct=0.0,
    )

    # 2. Optimistic Case
    opt_rate = max(Decimal("6.00"), req.discount_rate_pct - Decimal("2.00"))
    opt_benefit = req.normative_annual_net_benefit_per_ha_uzs * Decimal("1.15")
    opt_req = IndicativeValuationRequest(
        area_hectares=req.area_hectares,
        soil_bonitet_score=req.soil_bonitet_score,
        remaining_lease_years=req.remaining_lease_years,
        normative_annual_net_benefit_per_ha_uzs=opt_benefit,
        discount_rate_pct=opt_rate,
        annual_benefit_growth_pct=req.annual_benefit_growth_pct,
        target_ltv_pct=req.target_ltv_pct,
    )
    opt_res = calculate_indicative_lease_valuation(opt_req)
    opt_pv = opt_res.indicative_present_value_uzs
    opt_variance = 0.0
    if base_pv > Decimal("0.00"):
        opt_variance = round(float((opt_pv - base_pv) / base_pv) * 100.0, 2)

    optimistic_case = ValuationSensitivityCase(
        scenario_name_uz="Optimistik Ssenariy (Yuqori hosildorlik, past foiz)",
        discount_rate_pct=opt_rate,
        benefit_growth_pct=req.annual_benefit_growth_pct,
        annual_attributable_benefit_uzs=opt_res.annual_attributable_net_benefit_uzs,
        indicative_present_value_uzs=opt_pv,
        indicative_secured_amount_uzs=opt_res.indicative_secured_amount_uzs,
        variance_from_base_pct=opt_variance,
        indicative_valuation_uzs=opt_pv,
        max_pledge_value_uzs=opt_res.indicative_secured_amount_uzs,
        scenario_label_uz="Optimistik Ssenariy",
        description_uz="Hosildorlik +15% va diskont stavkasi -200 bps pasayishi.",
        variance_pct=opt_variance,
    )

    # 3. Pessimistic Case
    pes_rate = min(Decimal("35.00"), req.discount_rate_pct + Decimal("3.00"))
    pes_benefit = req.normative_annual_net_benefit_per_ha_uzs * Decimal("0.80")
    pes_req = IndicativeValuationRequest(
        area_hectares=req.area_hectares,
        soil_bonitet_score=req.soil_bonitet_score,
        remaining_lease_years=req.remaining_lease_years,
        normative_annual_net_benefit_per_ha_uzs=pes_benefit,
        discount_rate_pct=pes_rate,
        annual_benefit_growth_pct=req.annual_benefit_growth_pct,
        target_ltv_pct=req.target_ltv_pct,
    )
    pes_res = calculate_indicative_lease_valuation(pes_req)
    pes_pv = pes_res.indicative_present_value_uzs
    pes_variance = 0.0
    if base_pv > Decimal("0.00"):
        pes_variance = round(float((pes_pv - base_pv) / base_pv) * 100.0, 2)

    pessimistic_case = ValuationSensitivityCase(
        scenario_name_uz="Pessimistik Ssenariy (Shok narxlar, yuqori xatar)",
        discount_rate_pct=pes_rate,
        benefit_growth_pct=req.annual_benefit_growth_pct,
        annual_attributable_benefit_uzs=pes_res.annual_attributable_net_benefit_uzs,
        indicative_present_value_uzs=pes_pv,
        indicative_secured_amount_uzs=pes_res.indicative_secured_amount_uzs,
        variance_from_base_pct=pes_variance,
        indicative_valuation_uzs=pes_pv,
        max_pledge_value_uzs=pes_res.indicative_secured_amount_uzs,
        scenario_label_uz="Pessimistik Ssenariy",
        description_uz="Hosildorlik -20% va diskont stavkasi +300 bps o'sishi.",
        variance_pct=pes_variance,
    )

    volatility_range = opt_pv - pes_pv

    summary_uz = (
        f"Sezgirlik tahlili natijasi: Bazaviy indikativ qiymat {base_pv:,.0f} so'm. "
        f"Diskont stavkasi {opt_rate}% ga tushganda va sof daromad +15% oshganda qiymat {opt_variance:+}% ga oshadi ({opt_pv:,.0f} so'm). "
        f"Pessimistik holatda (diskont {pes_rate}%, daromad -20%) qiymat {pes_variance}% ga kamayadi ({pes_pv:,.0f} so'm)."
    )

    risk_drivers = [
        "Hosildorlik va qishloq xo'jaligi mahsulotlari narxlari tebranishi (±15-20%)",
        "Markaziy bank asosiy stavkasi va tijorat banklari kredit foizlari o'zgarishi (±200-300 bps)",
        "Iqlimiy va suv ta'minoti xatarlari natijasida yillik sof daromadning pasayishi",
    ]

    return CollateralSensitivityAnalysis(
        base_case=base_case,
        optimistic_case=optimistic_case,
        pessimistic_case=pessimistic_case,
        analysis_summary_uz=summary_uz,
        base_scenario=base_case,
        optimistic_scenario=optimistic_case,
        pessimistic_scenario=pessimistic_case,
        volatility_range_uzs=volatility_range,
        key_risk_drivers_uz=risk_drivers,
    )
