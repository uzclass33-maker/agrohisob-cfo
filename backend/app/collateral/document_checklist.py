"""
AgroHisob CFO - Collateral Document Checklist (Assignment 6, Module A)
Provides comprehensive checklist of statutory and procedural documents
mandated by VMQ-613 and commercial bank underwriting procedures.
"""

from typing import List
from app.collateral.schemas import (
    ChecklistItemStatusEnum,
    CollateralChecklistItem,
    CollateralDocumentChecklist,
    LandLeaseProfile,
)


def build_collateral_checklist(profile: LandLeaseProfile) -> CollateralDocumentChecklist:
    """
    Constructs an interactive collateral preparation checklist evaluated against
    the applicant's land lease profile.
    """
    items: List[CollateralChecklistItem] = [
        CollateralChecklistItem(
            id="col-doc-lease-contract",
            code="DOC-LEASE-CONTRACT",
            title_uz="Uzoq muddatli yer ijarasi shartnomasi",
            document_name_uz="Uzoq muddatli yer ijarasi shartnomasi",
            category_uz="Huquqiy hujjatlar",
            status=ChecklistItemStatusEnum.AVAILABLE,
            status_label_uz="Mavjud",
            is_statutory=True,
            is_mandatory=True,
            legal_source="VMQ-613, 5-band",
            statutory_reference="VMQ-613, 5-band",
            rationale_uz="Yer uchastkasidan foydalanish va ijara huquqini tasdiqlovchi asosiy hujjat.",
            description_uz="Tuman hokimligi va fermer o'rtasida tuzilgan uzoq muddatli ijara shartnomasi.",
            issuing_body_uz="Tuman hokimligi / Qishloq xo'jaligi bo'limi",
        ),
        CollateralChecklistItem(
            id="col-doc-cadastre-reg",
            code="DOC-CADASTRE-REG",
            title_uz="Davlat kadastri reyestridan ro'yxatga olish guvohnomasi / ko'chirma",
            document_name_uz="Davlat kadastri reyestridan ro'yxatga olish guvohnomasi",
            category_uz="Huquqiy hujjatlar",
            status=ChecklistItemStatusEnum.AVAILABLE if profile.is_registered_in_cadastre else ChecklistItemStatusEnum.MISSING,
            status_label_uz="Mavjud" if profile.is_registered_in_cadastre else "Yetishmaydi",
            is_statutory=True,
            is_mandatory=True,
            legal_source="VMQ-613, 5-band",
            statutory_reference="VMQ-613, 5-band",
            rationale_uz="Ijara huquqi davlat ro'yxatidan o'tganligini va qonuniyligini tasdiqlaydi.",
            description_uz="Davlat kadastrlari palatasi reyestridan elektron ko'chirma yoki QR-kodli guvohnoma.",
            issuing_body_uz="Davlat kadastrlari palatasi",
        ),
        CollateralChecklistItem(
            id="col-doc-cadastre-passport",
            code="DOC-CADASTRE-PASSPORT",
            title_uz="Yer uchastkasi kadastr pasporti va chegaralar xaritasi",
            document_name_uz="Yer uchastkasi kadastr pasporti va chegaralar xaritasi",
            category_uz="Kadastr ma'lumotlari",
            status=ChecklistItemStatusEnum.AVAILABLE,
            status_label_uz="Mavjud",
            is_statutory=True,
            is_mandatory=True,
            legal_source="VMQ-613, 6-band",
            statutory_reference="VMQ-613, 6-band",
            rationale_uz="Yerning aniq maydoni, chegaralari va joylashuv koordinatalarini belgilaydi.",
            description_uz="Geodezik koordinatalar bilan tasdiqlangan kadastr yig'majildi.",
            issuing_body_uz="Davlat kadastrlari palatasi",
        ),
        CollateralChecklistItem(
            id="col-doc-no-encumbrance",
            code="DOC-NO-ENCUMBRANCE",
            title_uz="Taqiq (arest), xatlov va garov majburiyatlari yo'qligi to'g'risida ma'lumotnoma",
            document_name_uz="Taqiq va garov yuklamalari yo'qligi haqida ma'lumotnoma",
            category_uz="Huquqiy tozalik",
            status=ChecklistItemStatusEnum.AVAILABLE if not profile.has_legal_restrictions else ChecklistItemStatusEnum.NEEDS_VERIFICATION,
            status_label_uz="Mavjud" if not profile.has_legal_restrictions else "Tekshiruv talab",
            is_statutory=True,
            is_mandatory=True,
            legal_source="VMQ-613, 12-band",
            statutory_reference="VMQ-613, 12-band",
            rationale_uz="Uchinchi shaxslarning da'vosi yoki oldingi garov yuklamalari yo'qligini isbotlaydi.",
            description_uz="Notarial idora yoki reyestr orqali taqiq yo'qligini tasdiqlovchi rasmiy ma'lumotnoma.",
            issuing_body_uz="Notarius / Notarial palata",
        ),
        CollateralChecklistItem(
            id="col-doc-no-dispute",
            code="DOC-NO-DISPUTE",
            title_uz="Sud nizosi yoki shartnomani bekor qilish jarayoni yo'qligi to'g'risida dalolatnoma",
            document_name_uz="Sud nizosi yo'qligi to'g'risida ma'lumotnoma",
            category_uz="Huquqiy tozalik",
            status=ChecklistItemStatusEnum.AVAILABLE if not profile.is_disputed else ChecklistItemStatusEnum.NEEDS_VERIFICATION,
            status_label_uz="Mavjud" if not profile.is_disputed else "Tekshiruv talab",
            is_statutory=True,
            is_mandatory=True,
            legal_source="VMQ-613, 12-band",
            statutory_reference="VMQ-613, 12-band",
            rationale_uz="Ijara huquqi nizoli emasligini va barqarorligini tasdiqlaydi.",
            description_uz="Sud idoralarida yoki ma'muriy tartibda ko'rilayotgan nizo yo'qligi.",
            issuing_body_uz="Iqtisodiy sud / Adliya bo'limi",
        ),
        CollateralChecklistItem(
            id="col-doc-sublease-permission",
            code="DOC-SUBLEASE-PERM",
            title_uz="Ikkilamchi ijarada (sub-lease) ijaraga beruvchi organning yozma ruxsati",
            document_name_uz="Ikkilamchi ijarada ijaraga beruvchi yozma ruxsati",
            category_uz="Ikkilamchi ijara",
            status=(
                ChecklistItemStatusEnum.NOT_APPLICABLE if not profile.is_secondary_lease
                else (ChecklistItemStatusEnum.AVAILABLE if profile.has_sublease_authority_permission else ChecklistItemStatusEnum.MISSING)
            ),
            status_label_uz="Qo'llanilmaydi" if not profile.is_secondary_lease else ("Mavjud" if profile.has_sublease_authority_permission else "Yetishmaydi"),
            is_statutory=True,
            is_mandatory=profile.is_secondary_lease,
            legal_source="VMQ-613, 14-band",
            statutory_reference="VMQ-613, 14-band",
            rationale_uz="Ikkilamchi ijaraga olingan yerni garovga qo'yish faqat vakolatli hokimlik/organ ruxsati bilan qonuniydir.",
            description_uz="Birlamchi ijaraga beruvchi vakolatli organning rasmiy rozilik xati.",
            issuing_body_uz="Tuman hokimligi / Qishloq xo'jaligi vazirligi",
        ),
        CollateralChecklistItem(
            id="col-doc-appraisal-report",
            code="DOC-APPRAISAL-REPORT",
            title_uz="Litsenziyali mustaqil baholovchi tashkilotning rasmiy baholash hisoboti",
            document_name_uz="Mustaqil baholovchi hisoboti",
            category_uz="Baholash hisoboti",
            status=ChecklistItemStatusEnum.AVAILABLE if profile.has_independent_appraisal else ChecklistItemStatusEnum.MISSING,
            status_label_uz="Mavjud" if profile.has_independent_appraisal else "Yetishmaydi",
            is_statutory=True,
            is_mandatory=True,
            legal_source="VMQ-613, 15-band",
            statutory_reference="VMQ-613, 15-band",
            rationale_uz="Bank kredit qo'mitasi faqat litsenziyaga ega baholovchining rasmiy xulosasini qabul qiladi.",
            description_uz="Mustaqil baholovchi tashkilot tomonidan tuzilgan baholash hisoboti va ekspertiza xulosasi.",
            issuing_body_uz="Litsenziyali baholovchi tashkilot",
        ),
        CollateralChecklistItem(
            id="col-doc-bonitet-cert",
            code="DOC-BONITET-CERT",
            title_uz="Tuproq boniteti baholash xulosasi («O'zdaverloyiha»)",
            document_name_uz="Tuproq boniteti xulosasi",
            category_uz="Agrar xususiyatlar",
            status=ChecklistItemStatusEnum.AVAILABLE,
            status_label_uz="Mavjud",
            is_statutory=False,
            is_mandatory=False,
            legal_source="Bank amaliyoti tavsiyasi",
            statutory_reference="Bank anderrayting qo'llanmasi",
            rationale_uz="Yerning unumdorligi va me'yoriy daromad olish salohiyatini tasdiqlaydi.",
            description_uz="Tuproq bonitet bali va unumdorlik ko'rsatkichlari bo'yicha davlat xulosasi.",
            issuing_body_uz="«O'zdaverloyiha» davlat ilmiy-loyihalash instituti",
        ),
        CollateralChecklistItem(
            id="col-doc-corporate-consent",
            code="DOC-CORP-CONSENT",
            title_uz="Korxona ta'sischilari/a'zolarining mulkiy huquqni garovga qo'yish to'g'risidagi qarori",
            document_name_uz="Ta'sischilar qarori / bayonnoma",
            category_uz="Korporativ hujjatlar",
            status=ChecklistItemStatusEnum.AVAILABLE,
            status_label_uz="Mavjud",
            is_statutory=True,
            is_mandatory=True,
            legal_source="Fuqarolik Kodeksi, 271-modda",
            statutory_reference="Fuqarolik Kodeksi, 271-modda",
            rationale_uz="Garov qo'yish bo'yicha ta'sischilarning qonuniy vakolati va roziligini tasdiqlaydi.",
            description_uz="Fermer xo'jaligi yoki MCHJ ta'sischilarining umumiy yig'ilish bayonnomasi.",
            issuing_body_uz="Fermer xo'jaligi ta'sischilari",
        ),
    ]

    total = len(items)
    avail = sum(1 for i in items if i.status == ChecklistItemStatusEnum.AVAILABLE)
    miss = sum(1 for i in items if i.status == ChecklistItemStatusEnum.MISSING)
    needs_ver = sum(1 for i in items if i.status == ChecklistItemStatusEnum.NEEDS_VERIFICATION)
    
    applicable_items = [i for i in items if i.status != ChecklistItemStatusEnum.NOT_APPLICABLE]
    comp_pct = round((avail / len(applicable_items) * 100.0), 1) if applicable_items else 100.0

    if comp_pct >= 85.0:
        verdict = "Yuqori tayyorgarlik"
    elif comp_pct >= 60.0:
        verdict = "O'rtacha tayyorgarlik (mustaqil baholash talab)"
    else:
        verdict = "Kam tayyorgarlik (muhim hujjatlar yetishmaydi)"

    disclaimer = (
        "Mazkur ro'yxat VMQ-613 va tijorat banklarining amaldagi qoidalariga moslashtirilgan indikativ "
        "tayyorgarlik vositasi bo'lib, bank anderrayteri tomonidan qo'shimcha hujjatlar talab etilishi mumkin."
    )

    return CollateralDocumentChecklist(
        items=items,
        total_count=total,
        available_count=avail,
        missing_count=miss,
        needs_verification_count=needs_ver,
        completeness_pct=comp_pct,
        checklist_disclaimer_uz=disclaimer,
        total_documents=total,
        readiness_percentage=comp_pct,
        readiness_verdict_uz=verdict,
    )
