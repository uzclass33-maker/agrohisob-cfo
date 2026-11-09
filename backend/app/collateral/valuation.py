"""
AgroHisob CFO - Indicative Land Lease Valuation Engine (Assignment 6, Module A)
Calculates the present value of attributable net economic benefit of agricultural land lease rights
using discounted cash flow (DCF). Strictly bounds the analysis horizon to the legal lease duration
with no unsupported terminal values.
"""

from decimal import Decimal, ROUND_HALF_UP
import math
from typing import List
from app.collateral.schemas import (
    DCFCashFlowPeriod,
    IndicativeValuationRequest,
    IndicativeValuationResult,
)


def calculate_indicative_lease_valuation(
    req: IndicativeValuationRequest
) -> IndicativeValuationResult:
    """
    Computes indicative DCF present value for agricultural land lease right.
    
    Formula:
    Adjusted Benefit Per Ha = Base Benefit * (Bonitet / 65)
    Annual Attributable Benefit = Adjusted Benefit Per Ha * Area (ha)
    PV = sum [ CF_t / (1 + r)^t ] over t = 1..N
    Indicative Secured Amount = PV * Target LTV
    """
    # 1. Soil Bonitet Adjustment (Standard benchmark bonitet = 65)
    bonitet_factor = max(0.3, min(1.8, req.soil_bonitet_score / 65.0))
    bonitet_factor_dec = Decimal(str(round(bonitet_factor, 4)))

    # 2. Attributable Annual Net Economic Benefit
    adjusted_benefit_per_ha = (req.normative_annual_net_benefit_per_ha_uzs * bonitet_factor_dec).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    area_dec = Decimal(str(req.area_hectares))
    annual_attributable_benefit = (adjusted_benefit_per_ha * area_dec).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # 3. Horizon and Discount Rate
    horizon_years = req.remaining_lease_years
    if req.discount_rate_pct <= Decimal("0.00"):
        r_float = 0.0001
    else:
        r_float = float(req.discount_rate_pct) / 100.0

    # 4. Generate period-by-period DCF schedule
    cash_flow_schedule: List[DCFCashFlowPeriod] = []
    cumulative_pv = Decimal("0.00")

    for year in range(1, horizon_years + 1):
        df = 1.0 / math.pow(1.0 + r_float, year)
        discounted_cf = (annual_attributable_benefit * Decimal(str(round(df, 8)))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        cumulative_pv += discounted_cf
        cash_flow_schedule.append(
            DCFCashFlowPeriod(
                year=year,
                nominal_cash_flow_uzs=annual_attributable_benefit,
                discount_factor=round(df, 4),
                discounted_cash_flow_uzs=discounted_cf,
                cumulative_pv_uzs=cumulative_pv,
            )
        )

    indicative_pv = cumulative_pv

    # 5. Indicative Secured Amount under Target LTV
    ltv_factor = req.target_ltv_pct / Decimal("100.00")
    indicative_secured = (indicative_pv * ltv_factor).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    annuity_factor = (1.0 - math.pow(1.0 + r_float, -horizon_years)) / r_float if r_float > 0 else float(horizon_years)

    methodology = (
        f"Indikativ baholash modeli: Gektariga sof normativ daromad ({req.normative_annual_net_benefit_per_ha_uzs:,.0f} so'm) "
        f"tuproq boniteti ({req.soil_bonitet_score} ball / 65 bazaviy = {bonitet_factor:.2f}x) bo'yicha tuzatilib, "
        f"{req.area_hectares} gektar maydonga ko'paytirildi. Yillik sof iqtisodiy foyda: {annual_attributable_benefit:,.0f} so'm. "
        f"Qolgan {horizon_years} yillik ijara muddati davomida {req.discount_rate_pct}% diskont stavkasida diskontlandi "
        f"(Annuity koeffitsiyenti: {annuity_factor:.4f}). Ijara muddatidan tashqari hech qanday terminal qiymat qo'shilmadi."
    )

    disclaimer = (
        "MUHIM HUQUQIY VA MOLIYAVIY OGOHLANTIRISH: Mazkur hisob-kitob korxona kiritgan parametrlarga asoslangan "
        "indikativ (namunaviy) moliyaviy ssenariy hisoblanadi. Ushbu natija O'zbekiston Respublikasining "
        "«Baholash faoliyati to'g'risida»gi Qonuniga muvofiq litsenziyalangan mustaqil baholovchi tashkilotning "
        "rasmiy baholash hisoboti yoki tijorat bankining qat'iy garov qiymati hisoblanmaydi. "
        "Bank garov sifatida qabul qilishda faqat rasmiy mustaqil baholash hisobotiga tayanadi."
    )

    return IndicativeValuationResult(
        indicative_present_value_uzs=indicative_pv,
        annual_attributable_net_benefit_uzs=annual_attributable_benefit,
        adjusted_benefit_per_ha_uzs=adjusted_benefit_per_ha,
        bonitet_adjustment_factor=round(bonitet_factor, 4),
        discount_rate_pct=req.discount_rate_pct,
        analysis_horizon_years=horizon_years,
        annuity_factor=round(annuity_factor, 4),
        target_ltv_pct=req.target_ltv_pct,
        indicative_secured_amount_uzs=indicative_secured,
        methodology_uz=methodology,
        statutory_disclaimer_uz=disclaimer,
        indicative_market_value_uzs=indicative_pv,
        max_pledge_value_uzs=indicative_secured,
        valuation_horizon_years=horizon_years,
        adjusted_annual_net_benefit_per_ha_uzs=adjusted_benefit_per_ha,
        cash_flow_schedule=cash_flow_schedule,
    )
