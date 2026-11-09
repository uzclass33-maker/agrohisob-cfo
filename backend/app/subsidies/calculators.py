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


# Regional coefficients for water-scarce / priority zones under PQ-47 (3-band)
# O'zbekiston Respublikasi Prezidentining 2026-yil 5-fevraldagi PQ-47-son qarori 3-bandiga binoan:
# Suv bilan barqaror ta'minlanmagan hududlarda 1.25 oshiruvchi koeffitsiyent qo'llaniladi.
PRIORITY_REGIONS_COEFFICIENT_1_25 = [
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
        return Decimal("11000000.00")  # 11 mln UZS/ha (suv tejovchi bog'lar)
    elif "uzum" in c:
        return Decimal("8000000.00")  # 8 mln UZS/ha
    elif "sabzavot" in c or "poliz" in c or "kartoshka" in c:
        return Decimal("6000000.00")  # 6 mln UZS/ha
    else:
        # Fodder / other crops
        return Decimal("6000000.00")


def calculate_pq47_subsidy(req: PQ47CalculationRequest) -> PQ47CalculationResult:
    """
    PQ-47 Qarori 3-bandi asosida tomchilatib sug'orish tizimi xarajatlarini qoplash subsidiyasini hisoblash.
    Bazaviy me'yorlar:
      - Paxta: 8 mln so'm/ga
      - Mevali bog'dorchilik: 11 mln so'm/ga
      - Uzumzor: 8 mln so'm/ga
      - Sabzavot, poliz, kartoshka: 6 mln so'm/ga
    Hududiy koeffitsiyent:
      - Suv bilan barqaror ta'minlanmagan hududlar (PQ-47 3-band): 1.25x
      - Boshqa hududlar: 1.0x
    Bosqichma-bosqich monitoring (Taxminiy model):
      - 50% 1-bosqich (uskuna o'rnatilgach dastlabki monitoring)
      - 50% 2-bosqich (ekspluatatsiya holati tekshirilgach)
    """
    eval_date = req.assessment_date or date(2026, 6, 1)
    pq47_effective = date(2026, 2, 5)

    is_eligible = eval_date >= pq47_effective

    base_rate = get_pq47_base_rate(req.crop_type)

    # Check regional coefficient (1.25 for water-scarce zones)
    reg_clean = req.region.lower()
    regional_coeff = 1.0
    for prio in PRIORITY_REGIONS_COEFFICIENT_1_25:
        if prio in reg_clean:
            regional_coeff = 1.25
            break

    effective_rate = (base_rate * Decimal(str(regional_coeff))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_estimated = (effective_rate * Decimal(str(req.area_hectares))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Phased disbursement (taxminiy monitoring modeli)
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
        f"Bazaviy stavka: {base_rate:,.0f} UZS/ga, Hududiy koeffitsiyent (PQ-47 3-band): {regional_coeff}x. "
        f"Samarali stavka: {effective_rate:,.0f} UZS/ga. "
        f"Jami taxminiy subsidiya: {total_estimated:,.0f} UZS (Shartli bosqichlar: 1-bosqich {phase_1:,.0f} UZS, 2-bosqich {phase_2:,.0f} UZS)."
    )

    methodology = (
        "O'zbekiston Respublikasi Prezidentining 2026-yil 5-fevraldagi PQ-47-son qarori 3-bandiga asosan "
        "suv tejovchi texnologiyalarni joriy etish xarajatlarining bir qismini qoplash hisob-kitobi. "
        "Suv bilan barqaror ta'minlanmagan hududlar uchun 1.25 koeffitsiyent qo'llaniladi. "
        "Bosqichma-bosqich to'lov taqsimoti shartli texnik monitoring modeliga asoslangan."
    )

    disclaimer = (
        "DIQQAT: Mazkur hisob-kitob indikativ (taxminiy) bo'lib, davlat byudjeti yoki Qishloq xo'jaligi vazirligi "
        "tomonidan subsidiya ajratishning yuridik kafolati hisoblanmaydi. Subsidiya belgilangan tartibda tuman "
        "ishchi guruhi dalolatnomasi va tegishli platforma (Agro-subsidiya) orqali tasdiqlanishi shart."
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
        legal_source="O'zbekiston Respublikasi Prezidentining 2026-yil 5-fevraldagi PQ-47-son qarori 3-bandi",
        effective_date=pq47_effective,
        statutory_status="INDIKATIV_MODELLASHTIRISH",
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
            legal_source="O'zbekiston Respublikasi Prezidentining 2026-yil 8-maydagi PF-82-son Farmoni 1-bandi",
            effective_date=pf82_effective,
            statutory_status="INDIKATIV_MODELLASHTIRISH",
            explanation_uz=(
                "PF-82 1-bandiga binoan qarzdorlik bo'yicha muddati o'tgan qarzlar (prosrochka) mavjud bo'lganda "
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
            legal_source="O'zbekiston Respublikasi Prezidentining 2026-yil 8-maydagi PF-82-son Farmoni 1-bandi",
            effective_date=pf82_effective,
            statutory_status="INDIKATIV_MODELLASHTIRISH",
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
            legal_source="O'zbekiston Respublikasi Prezidentining 2026-yil 8-maydagi PF-82-son Farmoni 1-bandi",
            effective_date=pf82_effective,
            statutory_status="INDIKATIV_MODELLASHTIRISH",
            explanation_uz=f"PF-82 farmoni 2026-yil 8-maydan kuchga kirgan. Baholash sanasi ({eval_date}) ushbu muddatdan oldin.",
            disclaimer_uz="Amal qilish muddatidan oldin.",
        )

    # PF-82 1-bandi bo'yicha tabaqalashtirilgan kompensatsiya stavkasi:
    # 1. Shartnomada belgilangan muddatda qaytarilgan kreditlar: 2.5 foiz punkti
    # 2. Hosil yilining 31-dekabriga qadar to'liq qaytarilgan kreditlar: 5.0 foiz punkti
    if req.repaid_by_year_end:
        comp_pct_points = Decimal("5.00")
        tier_desc = "hosil yili yakuniga (31-dekabrga) qadar to'liq qaytarish sharti bilan 5.0 foiz punkti"
    else:
        comp_pct_points = Decimal("2.50")
        tier_desc = "shartnomaviy muddatda qaytarish sharti bilan 2.5 foiz punkti"

    net_interest_rate = max(Decimal("0.00"), req.contractual_interest_rate_pct - comp_pct_points)

    # Day-based interest compensation formula:
    # Compensation = (Outstanding_balance * comp_pct_points * days_on_time) / 365
    days = req.days_on_time_repaid
    compensation = (
        req.outstanding_balance_uzs * (comp_pct_points / Decimal("100.00")) * Decimal(str(days)) / Decimal("365.00")
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    explanation = (
        f"PF-82 Farmoni 1-bandi: {req.crop_type} yetishtirish krediti bo'yicha shartnomaviy {req.contractual_interest_rate_pct}% stavkadan "
        f"{tier_desc} davlat tomonidan kompensatsiya qilinadi. Fermer uchun samarali yakuniy stavka: {net_interest_rate}%. "
        f"Hisob-kitob bazasi: {req.outstanding_balance_uzs:,.0f} UZS qoldiq, {days} kun intizomli to'lov uchun "
        f"indikativ kompensatsiya summasi: {compensation:,.0f} UZS."
    )

    disclaimer = (
        "DIQQAT: Mazkur hisob-kitob indikativ (taxminiy) modellashtirish bo'lib, yakuniy kompensatsiya "
        "Agrar sohada to'lovlar agentligi va xizmat ko'rsatuvchi tijorat banki o'rtasidagi rasmiy taqqoslash "
        "va to'lov buyurtmanomalari asosida amalga oshiriladi."
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
        legal_source="O'zbekiston Respublikasi Prezidentining 2026-yil 8-maydagi PF-82-son Farmoni 1-bandi",
        effective_date=pf82_effective,
        statutory_status="INDIKATIV_MODELLASHTIRISH",
        explanation_uz=explanation,
        disclaimer_uz=disclaimer,
    )
