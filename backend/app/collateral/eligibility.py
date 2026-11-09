"""
AgroHisob CFO - VMQ-613 Land Lease Collateral Legal Readiness Screening Engine (Assignment 6, Module A)
Strict calendar-aware date arithmetic for 5-year post-maturity buffer rule,
cadastre registration, legal restrictions, and secondary lease (sub-lease) compliance.
"""

from datetime import date, datetime, timezone
from typing import List

from app.collateral.schemas import (
    LandLeaseProfile,
    VMQ613RuleCheckItem,
    VMQ613ScreeningResult,
    VMQ613ScreeningStatusEnum,
)
from app.regulatory.legal_sources import get_regulatory_source


def _add_years_calendar_aware(d: date, years: int) -> date:
    """
    Calendar-aware addition of years handling leap-year (Feb 29 -> Feb 28 on non-leap years).
    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        # Happens only when d is Feb 29 and target year is not a leap year
        return d.replace(year=d.year + years, day=28)


def screen_land_lease_collateral(profile: LandLeaseProfile) -> VMQ613ScreeningResult:
    """
    Performs statutory legal readiness screening of agricultural land lease right under VMQ-613.
    """
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    findings: List[str] = []
    defects: List[str] = []
    missing_evidence: List[str] = []
    human_verifications: List[str] = []
    rule_checks: List[VMQ613RuleCheckItem] = []

    # 1. Lease Duration & 5-Year Post-Maturity Buffer Rule (VMQ-613, 8-band)
    loan_mat = profile.proposed_loan_maturity_date
    lease_exp = profile.lease_expiration_date

    # The lease must extend at least 5 years beyond the loan maturity date
    buffer_required_date = _add_years_calendar_aware(loan_mat, 5)
    is_5_year_buffer_satisfied = lease_exp >= buffer_required_date
    lease_duration_valid = lease_exp > date.today()

    diff_days = (lease_exp - loan_mat).days
    diff_years = round(diff_days / 365.25, 2)

    if is_5_year_buffer_satisfied:
        findings.append(
            f"VMQ-613 8-band talabi bajarildi: Ijara muddati ({lease_exp.isoformat()}) "
            f"kredit qaytish sanasidan ({loan_mat.isoformat()}) so'ng {diff_years} yil davom etadi "
            f"(talab: kamida 5 yil)."
        )
        rule_checks.append(
            VMQ613RuleCheckItem(
                rule_id="RULE-VMQ613-BUFFER-5Y",
                rule_name_uz="5 yillik post-kredit bufer muddati",
                statutory_basis="VMQ-613, 8-band",
                status="COMPLIANT",
                status_label_uz="Talab bajarilgan",
                explanation_uz=f"Ijara muddati kredit tugashidan so'ng {diff_years} yil davom etadi (kamida 5 yil talab etiladi).",
            )
        )
    else:
        findings.append(
            f"DIQQAT: VMQ-613 8-band talabi bajarilmadi! Ijara muddati ({lease_exp.isoformat()}) "
            f"kredit so'ndirilgach atigi {diff_years} yil qolmoqda. Qonun bo'yicha kamida 5 yil ortiq bo'lishi shart "
            f"(kerakli muddat: {buffer_required_date.isoformat()} gacha)."
        )
        defects.append(
            f"5 yillik bufer talabi bajarilmagan: ijara muddati kredit so'ndirilgandan keyin atigi {diff_years} yil "
            f"(kamida 5 yil talab etiladi)."
        )
        human_verifications.append(
            "Kredit muddatini qisqartirish yoki yer ijara shartnomasini uzaytirish masalasini ko'rib chiqish."
        )
        rule_checks.append(
            VMQ613RuleCheckItem(
                rule_id="RULE-VMQ613-BUFFER-5Y",
                rule_name_uz="5 yillik post-kredit bufer muddati",
                statutory_basis="VMQ-613, 8-band",
                status="NON_COMPLIANT",
                status_label_uz="Talab bajarilmagan",
                explanation_uz=f"Ijara muddati kredit tugashidan so'ng atigi {diff_years} yil qolmoqda (kamida 5 yil talab etiladi).",
                action_required_uz="Kredit muddatini qisqartiring yoki ijara shartnomasini uzaytiring.",
            )
        )

    # 2. Registration Verification (VMQ-613, 5-band)
    registration_valid = profile.is_registered_in_cadastre and bool(profile.registration_number)
    if registration_valid:
        findings.append(
            f"Davlat ro'yxatidan o'tganlik tasdiqlandi: Ro'yxatga olish raqami: {profile.registration_number}."
        )
        rule_checks.append(
            VMQ613RuleCheckItem(
                rule_id="RULE-VMQ613-REGISTRATION",
                rule_name_uz="Davlat kadastri ro'yxatidan o'tganlik",
                statutory_basis="VMQ-613, 5-band",
                status="COMPLIANT",
                status_label_uz="Ro'yxatdan o'tgan",
                explanation_uz=f"Kadastr ro'yxatga olish raqami: {profile.registration_number}.",
            )
        )
    else:
        findings.append("Yer ijara huquqining Davlat kadastridan ro'yxatdan o'tganligi to'g'risida ma'lumot yetishmaydi.")
        defects.append("Yer ijara huquqi davlat ro'yxatidan o'tkazilmagan yoki kadastr raqami mavjud emas.")
        missing_evidence.append("Davlat reyestridan ko'chirma yoki kadastr pasporti.")
        human_verifications.append("Davlat kadastrlari palatasidan rasmiy ko'chirma olish.")
        rule_checks.append(
            VMQ613RuleCheckItem(
                rule_id="RULE-VMQ613-REGISTRATION",
                rule_name_uz="Davlat kadastri ro'yxatidan o'tganlik",
                statutory_basis="VMQ-613, 5-band",
                status="NON_COMPLIANT",
                status_label_uz="Ro'yxatdan o'tmagan",
                explanation_uz="Kadastr ro'yxatidan o'tganlik to'g'risida ma'lumot mavjud emas.",
                action_required_uz="Davlat kadastrlari palatasidan ko'chirma oling.",
            )
        )

    # 3. Restrictions & Dispute Verification (VMQ-613, 12-band)
    restrictions_clear = not profile.has_legal_restrictions and not profile.is_terminated
    dispute_clear = not profile.is_disputed

    if not restrictions_clear:
        findings.append(
            "OGOHLANTIRISH: Yer uchastkasi bo'yicha taqiq (arest), xatlov yoki shartnoma bekor qilinishi aniqlandi."
        )
        defects.append("Yer uchastkasi bo'yicha taqiq (arest), xatlov yoki boshqa huquqiy cheklov mavjud.")
    if not dispute_clear:
        findings.append("OGOHLANTIRISH: Yer uchastkasi bo'yicha sud nizosi mavjud.")
        defects.append("Yer ijara huquqi bo'yicha sud nizosi mavjud.")

    rule_checks.append(
        VMQ613RuleCheckItem(
            rule_id="RULE-VMQ613-NO-RESTRICTIONS",
            rule_name_uz="Taqiq va nizolar yo'qligi",
            statutory_basis="VMQ-613, 12-band",
            status="COMPLIANT" if (restrictions_clear and dispute_clear) else "NON_COMPLIANT",
            status_label_uz="Taqiqlar yo'q" if (restrictions_clear and dispute_clear) else "Taqiq yoki nizo mavjud",
            explanation_uz="Yer bo'yicha arest, taqiq yoki sud nizosi aniqlanmadi." if (restrictions_clear and dispute_clear) else "Taqiq yoki sud nizosi mavjud.",
        )
    )

    # 4. Secondary Lease (Sub-lease) Verification (VMQ-613, 14-band)
    secondary_lease_compliant = True
    if profile.is_secondary_lease:
        if profile.has_sublease_authority_permission:
            findings.append("Ikkilamchi ijara (sub-lease) bo'yicha ijaraga beruvchi organning yozma ruxsati mavjud.")
            rule_checks.append(
                VMQ613RuleCheckItem(
                    rule_id="RULE-VMQ613-SUBLEASE",
                    rule_name_uz="Ikkilamchi ijara ruxsati",
                    statutory_basis="VMQ-613, 14-band",
                    status="COMPLIANT",
                    status_label_uz="Ruxsatnoma mavjud",
                    explanation_uz="Ijaraga beruvchining yozma ruxsatnomasi mavjud.",
                )
            )
        else:
            secondary_lease_compliant = False
            findings.append("Ikkilamchi ijara (sub-lease): Asosiy ijaraga beruvchi davlat organining rasmiy yozma roziligi yo'q.")
            defects.append("Ikkilamchi ijara (sub-lease) uchun vakolatli organning yozma roziligi hujjati mavjud emas.")
            missing_evidence.append("Ijaraga beruvchi (hokimlik / vakolatli organ) yozma rozilik xati.")
            human_verifications.append("Ikkilamchi ijarada garov qo'yish uchun ijaraga beruvchidan rasmiy ruxsatnoma olish.")
            rule_checks.append(
                VMQ613RuleCheckItem(
                    rule_id="RULE-VMQ613-SUBLEASE",
                    rule_name_uz="Ikkilamchi ijara ruxsati",
                    statutory_basis="VMQ-613, 14-band",
                    status="NON_COMPLIANT",
                    status_label_uz="Ruxsatnoma yo'q",
                    explanation_uz="Ikkilamchi ijarada ijaraga beruvchi organning yozma roziligi talab qilinadi.",
                    action_required_uz="Hokimlik yoki vakolatli organdan yozma ruxsatnoma oling.",
                )
            )
    else:
        rule_checks.append(
            VMQ613RuleCheckItem(
                rule_id="RULE-VMQ613-SUBLEASE",
                rule_name_uz="Birlamchi ijara holati",
                statutory_basis="VMQ-613, 14-band",
                status="COMPLIANT",
                status_label_uz="Birlamchi ijara",
                explanation_uz="Yer to'g'ridan-to'g'ri birlamchi ijara huquqi asosida foydalanilmoqda.",
            )
        )

    # 5. Independent Appraisal (VMQ-613, 15-band)
    if profile.has_independent_appraisal and profile.independent_appraisal_value_uzs:
        findings.append(
            f"Litsenziyali mustaqil baholovchi hisoboti mavjud: {profile.independent_appraisal_value_uzs:,.2f} UZS."
        )
        rule_checks.append(
            VMQ613RuleCheckItem(
                rule_id="RULE-VMQ613-APPRAISAL",
                rule_name_uz="Mustaqil baholash hisoboti",
                statutory_basis="VMQ-613, 15-band",
                status="COMPLIANT",
                status_label_uz="Hisobot mavjud",
                explanation_uz=f"Litsenziyali baholovchi hisoboti mavjud: {profile.independent_appraisal_value_uzs:,.0f} UZS.",
            )
        )
    else:
        missing_evidence.append("Litsenziyaga ega baholovchi tashkilotning rasmiy baholash hisoboti.")
        human_verifications.append("Tijorat bankiga taqdim etish uchun litsenziyali mustaqil baholovchini jalb qilish.")
        rule_checks.append(
            VMQ613RuleCheckItem(
                rule_id="RULE-VMQ613-APPRAISAL",
                rule_name_uz="Mustaqil baholash hisoboti",
                statutory_basis="VMQ-613, 15-band",
                status="CONDITIONAL_PASS",
                status_label_uz="Mustaqil baholash talab etiladi",
                explanation_uz="Platformaning indikativ bahosi mavjud. Yakuniy qabul uchun litsenziyali baholovchi hisoboti talab qilinadi.",
                action_required_uz="Litsenziyaga ega baholovchi tashkilotni jalb qiling.",
            )
        )

    # 6. Overall Status Determination
    if not restrictions_clear or not dispute_clear or profile.is_terminated:
        overall_status = VMQ613ScreeningStatusEnum.APPARENT_RESTRICTION_IDENTIFIED
        status_label_uz = "Qonuniy cheklov yoki taqiq aniqlandi"
        is_eligible = False
    elif not is_5_year_buffer_satisfied:
        overall_status = VMQ613ScreeningStatusEnum.APPARENT_RESTRICTION_IDENTIFIED
        status_label_uz = "Ijara muddati 5 yillik qonuniy me'yordan kam"
        is_eligible = False
    elif not registration_valid or not secondary_lease_compliant or len(missing_evidence) > 1:
        overall_status = VMQ613ScreeningStatusEnum.ADDITIONAL_VERIFICATION_REQUIRED
        status_label_uz = "Qo'shimcha tekshiruv va hujjatlar talab etiladi"
        is_eligible = False
    else:
        overall_status = VMQ613ScreeningStatusEnum.PRELIMINARY_CONDITIONS_MET
        status_label_uz = "Dastlabki qonuniy shartlar bajarilgan"
        is_eligible = True

    reg_source = get_regulatory_source("VMQ-613")
    legal_url = reg_source.official_lex_url if reg_source else "https://lex.uz/uz/docs/-7750301"

    disclaimer = (
        "DIQQAT: Ushbu huquqiy tahlil VMQ-613 qarori asosidagi dastlabki screening hisoblanadi. "
        "U sud organlari, notariat yoki tijorat banki kredit qo'mitasining rasmiy huquqiy ekspertizasi o'rnini bosmaydi."
    )

    return VMQ613ScreeningResult(
        overall_status=overall_status,
        status_label_uz=status_label_uz,
        screening_date=now_str,
        lease_duration_valid=lease_duration_valid,
        remaining_lease_days_after_maturity=diff_days,
        remaining_lease_years_after_maturity=diff_years,
        required_buffer_years=5,
        is_5_year_buffer_satisfied=is_5_year_buffer_satisfied,
        registration_valid=registration_valid,
        restrictions_clear=restrictions_clear,
        dispute_clear=dispute_clear,
        secondary_lease_compliant=secondary_lease_compliant,
        key_findings_uz=findings,
        missing_evidence_uz=missing_evidence,
        human_verification_requirements_uz=human_verifications,
        is_eligible=is_eligible,
        overall_legal_status_uz=status_label_uz,
        post_maturity_buffer_years=diff_years,
        remaining_lease_years=diff_years,
        defects=defects,
        remediation_steps=human_verifications,
        rule_checks=rule_checks,
        statutory_disclaimer_uz=disclaimer,
        legal_source_code="VMQ-613",
        legal_source_url=legal_url,
        applied_rule_clauses=["5-band", "8-band", "12-band", "14-band", "15-band"],
    )
