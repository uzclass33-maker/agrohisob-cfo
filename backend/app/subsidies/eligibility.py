"""
AgroHisob CFO - Agricultural Subsidy Eligibility Screening Engine (Assignment 6, Module B)
Screens farm profile against statutory rules in the SubsidyProgram registry.
Yields one of five deterministic statuses:
  - POTENTIALLY_ELIGIBLE
  - NOT_ELIGIBLE_UNDER_VERIFIED_RULE
  - MORE_INFORMATION_REQUIRED
  - RULE_NOT_VERIFIED
  - OUTSIDE_EFFECTIVE_PERIOD
"""

from datetime import date
from decimal import Decimal
from typing import List, Tuple

from app.subsidies.schemas import (
    SubsidyEligibilityStatusEnum,
    SubsidyMatchItem,
    SubsidyMatchRequest,
    SubsidyProgram,
)


def evaluate_subsidy_eligibility(
    program: SubsidyProgram, req: SubsidyMatchRequest
) -> Tuple[SubsidyEligibilityStatusEnum, str, List[str], List[str], Decimal]:
    """
    Evaluates an organization against a specific SubsidyProgram.
    Returns:
      (status, label_uz, match_reasons_uz, missing_conditions_uz, indicative_amount_uzs)
    """
    eval_date = req.assessment_date or date(2026, 6, 1)
    match_reasons: List[str] = []
    missing_conditions: List[str] = []
    indicative_amount = Decimal("0.00")

    # 1. Check rule verification status
    if program.verification_status != "VERIFIED_ACTIVE" or not program.is_active:
        return (
            SubsidyEligibilityStatusEnum.RULE_NOT_VERIFIED,
            "Huquqiy asos to'liq verifikatsiya qilinmagan",
            ["Dastur ro'yxatda mavjud"],
            ["Me'yoriy hujjat qoidasi rasmiy tahrirda to'liq tasdiqlanmagan"],
            Decimal("0.00"),
        )

    # 2. Check effective period
    if eval_date < program.effective_from:
        return (
            SubsidyEligibilityStatusEnum.OUTSIDE_EFFECTIVE_PERIOD,
            "Dasturning amal qilish muddati hali boshlanmagan",
            [],
            [f"Dastur {program.effective_from.isoformat()} sanasidan kuchga kiradi. Baholash sanasi: {eval_date.isoformat()}"],
            Decimal("0.00"),
        )
    if program.effective_to and eval_date > program.effective_to:
        return (
            SubsidyEligibilityStatusEnum.OUTSIDE_EFFECTIVE_PERIOD,
            "Dasturning amal qilish muddati tugagan",
            [],
            [f"Dastur {program.effective_to.isoformat()} sanasida yakunlangan."],
            Decimal("0.00"),
        )

    # 3. Check for essential required information
    if req.land_hectares <= 0:
        return (
            SubsidyEligibilityStatusEnum.MORE_INFORMATION_REQUIRED,
            "Yer maydoni ko'rsatilmagan",
            [],
            ["Ekin maydoni (gektar) kiritilishi shart"],
            Decimal("0.00"),
        )

    if not req.crop_types:
        return (
            SubsidyEligibilityStatusEnum.MORE_INFORMATION_REQUIRED,
            "Ekin turlari ma'lumotlari yetarli emas",
            [],
            ["Fermer xo'jaligining ekadigan ekin turlari ro'yxati talab qilinadi"],
            Decimal("0.00"),
        )

    # 4. Crop match check
    crop_matched = False
    matched_crop_name = ""
    req_crops_lower = [c.lower() for c in req.crop_types]

    if not program.supported_crops:
        crop_matched = True
    else:
        for p_crop in program.supported_crops:
            for r_crop in req_crops_lower:
                if p_crop.lower() in r_crop or r_crop in p_crop.lower():
                    crop_matched = True
                    matched_crop_name = r_crop
                    break
            if crop_matched:
                break

    if not crop_matched:
        return (
            SubsidyEligibilityStatusEnum.NOT_ELIGIBLE_UNDER_VERIFIED_RULE,
            "Ekin turi dastur talablariga mos kelmaydi",
            [],
            [f"Dastur faqat {', '.join(program.supported_crops)} ekinlariga tatbiq etiladi. Sizning ekinlaringiz: {', '.join(req.crop_types)}"],
            Decimal("0.00"),
        )

    match_reasons.append(f"Ekin turi mos keladi: {matched_crop_name or ', '.join(req.crop_types)}")

    # 5. Technology match check (for PQ-47 water saving)
    if program.supported_technologies:
        if not req.has_drip_irrigation:
            return (
                SubsidyEligibilityStatusEnum.NOT_ELIGIBLE_UNDER_VERIFIED_RULE,
                "Suv tejovchi texnologiya talabi bajarilmagan",
                match_reasons,
                ["Dastur suv tejovchi (tomchilatib) sug'orish tizimi joriy etilishini talab qiladi"],
                Decimal("0.00"),
            )
        match_reasons.append("Tomchilatib sug'orish tizimi rejalashtirilgan / mavjud")

    # 6. Regional check
    if program.eligible_regions:
        reg_match = any(r.lower() in req.region.lower() for r in program.eligible_regions)
        if not reg_match:
            return (
                SubsidyEligibilityStatusEnum.NOT_ELIGIBLE_UNDER_VERIFIED_RULE,
                "Hududiy qamrovga to'g'ri kelmaydi",
                match_reasons,
                [f"Dastur faqat {', '.join(program.eligible_regions)} hududlarida amal qiladi. Sizning hududingiz: {req.region}"],
                Decimal("0.00"),
            )
        match_reasons.append(f"Hudud dastur doirasida: {req.region}")
    else:
        match_reasons.append("Respublikaning barcha hududlariga tatbiq etiladi")

    # 7. Calculate indicative support amount if applicable
    if program.base_rate_uzs_per_ha:
        # Base rate * hectares (approximate calculation for matching overview)
        indicative_amount = program.base_rate_uzs_per_ha * Decimal(str(req.land_hectares))
        match_reasons.append(f"Bazaviy subsidiya me'yori: {program.base_rate_uzs_per_ha:,.0f} so'm/ga")

    if program.interest_compensation_pct_points:
        match_reasons.append(f"Kredit stavkasidan {program.interest_compensation_pct_points}% bandi kompensatsiya qilinadi")

    return (
        SubsidyEligibilityStatusEnum.POTENTIALLY_ELIGIBLE,
        "Dastlabki mezonlarga to'liq mos keladi",
        match_reasons,
        missing_conditions,
        indicative_amount,
    )
