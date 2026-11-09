"""
AgroHisob CFO - Agricultural Subsidy Calculators (Assignment 6, Module B)
Strict deterministic calculators for PQ-47 (water saving) and PF-82 (cotton & wheat interest compensation).
"""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from app.subsidies.schemas import (
    PQ47CalculationRequest,
    PQ47CalculationResult,
    PF82CalculationRequest,
    PF82CalculationResult,
)


# Regional coefficients for water-scarce / priority zones under PQ-47
PRIORITY_REGIONS_COEFFICIENT_1_2 = [
    "qoraqalpog'iston",
    "karakalpakstan",
    "xorazm",
    "navoiy",
    "buxoro",
]


def get_pq47_base_rate(crop_type: str) -> Decimal:
    c = crop_type.strip().lower()
    if "paxta" in c:
        return Decimal("8000000.00")  # 8 mln UZS/ha
    elif "bog'" in c or "bogdorchilik" in c or "meva" in c or "olma" in c or "gilos" in c:
        return Decimal("10000000.00")  # 10 mln UZS/ha
    elif "uzum" in c:
        return Decimal("8000000.00")  # 8 mln UZS/ha
    elif "sabzavot" in c or "poliz" in c or "kartoshka" in c:
        return Decimal("6000000.00")  # 6 mln UZS/ha
    else:
        # Default vegetable / fodder rate
        return Decimal("6000000.00")


def calculate_pq47_subsidy(req: PQ47CalculationRequest) -> PQ47CalculationResult:
    """
    PQ-47 Qarori asosida tomchilatib sug'orish tizimi xarajatlarini qoplash subsidiyasini hisoblash.
    Bazaviy stavkalar:
      - Paxta: 8 mln so'm/ga
      - Sabzavot: 6 mln so'm/ga
      - Mevali bog': 10 mln so'm/ga
      - Uzumzor: 8 mln so'm/ga
    Bosqichma-bosqich to'lov:
      - 50% Dastlabki to'lov (uskuna o'rnatilgach)
      - 50% Yakuniy to'lov (mavsum yakunida ish holati tekshirilgach)
    """
    eval_date = req.assessment_date or date(2026, 6, 1)
    pq47_effective = date(2026, 2, 5)

    is_eligible = eval_date >= pq47_effective

    base_rate = get_pq47_base_rate(req.crop_type)

    # Check regional coefficient
    reg_clean = req.region.lower()
    regional_coeff = 1.0
    for prio in PRIORITY_REGIONS_COEFFICIENT_1_2:
        if prio in reg_clean:
            regional_coeff = 1.2
            break

    effective_rate = (base_rate * Decimal(str(regional_coeff))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_estimated = (effective_rate * Decimal(str(req.area_hectares))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Phased disbursement: 50% initial, 50% conditional post-season
    phase_1 = (total_estimated * Decimal("0.50")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    phase_2 = total_estimated - phase_1

    # Interest compensation if bank loan used
    int_comp_annual = None
    int_comp_pct = None
    if req.financed_via_bank_loan and req.loan_principal_uzs and req.loan_principal_uzs > 0:
        int_comp_pct = Decimal("4.00")  # 4 percentage points
        int_comp_annual = (req.loan_principal_uzs * (int_comp_pct / Decimal("100.00"))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    breakdown = (
        f"Maydon: {req.area_hectares:.1f} ga, Ekin: {req.crop_type}. "
        f"Bazaviy stavka: {base_rate:,.0f} UZS/ga, Hududiy koeffitsiyent: {regional_coeff}x. "
        f"Samarali stavka: {effective_rate:,.0f} UZS/ga. "
        f"Jami subsidiya: {total_estimated:,.0f} UZS (1-bosqich: {phase_1:,.0f} UZS, 2-bosqich: {phase_2:,.0f} UZS)."
    )

    methodology = (
        "O'zbekiston Respublikasi Prezidentining 2026-yil 5-fevraldagi PQ-47-son qaroriga asosan "
        "suv tejovchi texnologiyalarni joriy etish xarajatlarining bir qismini qoplash mexanizmi. "
        "To'lov 2 bosqichda amalga oshiriladi: 50% montajdan so'ng, 50% ekspluatatsiya holati tekshirilgach."
    )

    disclaimer = (
        "DIQQAT: Mazkur hisob-kitob indikativ (taxminiy) bo'lib, davlat byudjeti yoki Qishloq xo'jaligi vazirligi "
        "tomonidan subsidiya ajratishning yuridik kafolati hisoblanmaydi. Subsidiya belgilangan tartibda tuman "
        "ishchi guruhi dalolatnomasi va tegishli platforma (Agro-subsidiya) orqali tasdiqlanishi lozim."
    )

    return PQ47CalculationResult(
        program_code="PQ47-WATER-SAVING",
        crop_type=req.crop_type,
        area_hectares=req.area_hectares,
        technology_type=req.technology_type,
        region=req.region,
        is_eligible=is_eligible,
        base_rate_per_ha_uzs=base_rate,
        regional_coefficient=regional_coeff,
        effective_rate_per_ha_uzs=effective_rate,
        estimated_total_subsidy_uzs=total_estimated,
        phase_1_initial_disbursement_uzs=phase_1,
        phase_2_conditional_disbursement_uzs=phase_2,
        interest_compensation_annual_uzs=int_comp_annual,
        interest_compensation_pct_points=int_comp_pct,
        calculation_breakdown_uz=breakdown,
        methodology_uz=methodology,
        statutory_disclaimer_uz=disclaimer,
    )


def calculate_pf82_compensation(req: PF82CalculationRequest) -> PF82CalculationResult:
    """
    PF-82 Farmoni asosida paxta va g'alla yetishtirish uchun olingan kreditlar bo'yicha
    o'z vaqtida qaytarilgan qarz qoldig'iga 10 foiz bandini kompensatsiya qilish hisobi.
    """
    eval_date = req.assessment_date or date(2026, 6, 1)
    pf82_effective = date(2026, 5, 8)

    crop_clean = req.crop_type.strip().lower()
    is_cotton_or_wheat = ("paxta" in crop_clean) or ("g'alla" in crop_clean) or ("bug'doy" in crop_clean)

    # Ineligibility reasons:
    # 1. Has overdue debt -> completely ineligible
    # 2. Not cotton/wheat
    # 3. Outside effective period
    if req.has_overdue_debt:
        return PF82CalculationResult(
            program_code="PF82-COTTON-WHEAT",
            crop_type=req.crop_type,
            is_eligible=False,
            compensation_pct_points=Decimal("0.00"),
            net_farmer_interest_rate_pct=req.contractual_interest_rate_pct,
            indicative_interest_compensation_uzs=Decimal("0.00"),
            calculation_basis_uzs=req.outstanding_balance_uzs,
            days_compensated=0,
            explanation_uz=(
                "PF-82 bandiga binoan qarzdorlik bo'yicha muddati o'tgan qarzlar (prosrochka) mavjud bo'lganda "
                "foiz stavkasi kompensatsiyasi taqdim etilmaydi. Kompensatsiya faqat o'z vaqtida so'ndirilgan kreditlarga qo'llaniladi."
            ),
            disclaimer_uz="Muddati o'tgan qarzdorlik sababli imtiyoz qo'llanilmaydi.",
        )

    if not is_cotton_or_wheat:
        return PF82CalculationResult(
            program_code="PF82-COTTON-WHEAT",
            crop_type=req.crop_type,
            is_eligible=False,
            compensation_pct_points=Decimal("0.00"),
            net_farmer_interest_rate_pct=req.contractual_interest_rate_pct,
            indicative_interest_compensation_uzs=Decimal("0.00"),
            calculation_basis_uzs=req.outstanding_balance_uzs,
            days_compensated=0,
            explanation_uz=f"PF-82 farmoni faqat paxta va g'alla yetishtirish kreditlariga tatbiq etiladi. '{req.crop_type}' ushbu dasturga kirmaydi.",
            disclaimer_uz="Ekin turi mos emas.",
        )

    if eval_date < pf82_effective:
        return PF82CalculationResult(
            program_code="PF82-COTTON-WHEAT",
            crop_type=req.crop_type,
            is_eligible=False,
            compensation_pct_points=Decimal("0.00"),
            net_farmer_interest_rate_pct=req.contractual_interest_rate_pct,
            indicative_interest_compensation_uzs=Decimal("0.00"),
            calculation_basis_uzs=req.outstanding_balance_uzs,
            days_compensated=0,
            explanation_uz=f"PF-82 farmoni 2026-yil 8-maydan kuchga kirgan. Baholash sanasi ({eval_date}) ushbu muddatdan oldin.",
            disclaimer_uz="Amal qilish muddatidan oldin.",
        )

    comp_pct_points = Decimal("10.00")
    net_interest_rate = max(Decimal("0.00"), req.contractual_interest_rate_pct - comp_pct_points)

    # Day-based interest compensation formula:
    # Compensation = (Outstanding_balance * 10% * days_on_time) / 365
    days = req.days_on_time_repaid
    compensation = (
        req.outstanding_balance_uzs * (comp_pct_points / Decimal("100.00")) * Decimal(str(days)) / Decimal("365.00")
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    explanation = (
        f"PF-82 Farmoni: {req.crop_type} yetishtirish krediti bo'yicha shartnomaviy {req.contractual_interest_rate_pct}% stavkadan "
        f"10 foiz bandi davlat tomonidan kompensatsiya qilinadi. Fermer uchun samarali yakuniy stavka: {net_interest_rate}%. "
        f"Hisob-kitob bazasi: {req.outstanding_balance_uzs:,.0f} UZS qoldiq, {days} kun intizomli to'lov uchun "
        f"kompensatsiya summasi: {compensation:,.0f} UZS."
    )

    disclaimer = (
        "DIQQAT: Mazkur hisob-kitob indikativ bo'lib, yakuniy kompensatsiya Qishloq xo'jaligini qo'llab-quvvatlash "
        "jamg'armasi va xizmat ko'rsatuvchi tijorat banki o'rtasidagi ma'lumotlar almashinuvi asosida to'lanadi."
    )

    return PF82CalculationResult(
        program_code="PF82-COTTON-WHEAT",
        crop_type=req.crop_type,
        is_eligible=True,
        compensation_pct_points=comp_pct_points,
        net_farmer_interest_rate_pct=net_interest_rate,
        indicative_interest_compensation_uzs=compensation,
        calculation_basis_uzs=req.outstanding_balance_uzs,
        days_compensated=days,
        explanation_uz=explanation,
        disclaimer_uz=disclaimer,
    )
