"""
AgroHisob CFO - Financial Readiness Assessment & Checklist Service
Builds the illustrative Document Readiness Checklist and evaluates deterministic Credit Readiness.
"""

from decimal import Decimal
from typing import List
from app.financial_engine.schemas import SeasonalForecastResponse
from app.reporting.report_schemas import (
    ChecklistItem,
    ChecklistItemStatus,
    CreditProfile,
    DocumentReadinessChecklist,
    FinancialReadinessAssessment,
    ReadinessStatusEnum,
)


def build_document_readiness_checklist(org_id: str, is_imported: bool = False) -> DocumentReadinessChecklist:
    """
    Constructs an intelligent, transparent pre-underwriting document readiness checklist.
    Categorized into 5 vital domains for Uzbek agricultural lending.
    """
    items: List[ChecklistItem] = [
        # 1. Company Information
        ChecklistItem(
            id="chk-comp-reg",
            category="COMPANY_INFO",
            category_title_uz="Korxona yuridik ma'lumotlari",
            title_uz="Davlat ro'yxatidan o'tganlik to'g'risida guvohnoma (Guvohnoma)",
            status=ChecklistItemStatus.AVAILABLE,
            rationale_uz="Yuridik shaxs yoki fermer xo'jaligi maqomini tasdiqlovchi birlamchi hujjat.",
            is_critical=True
        ),
        ChecklistItem(
            id="chk-comp-charter",
            category="COMPANY_INFO",
            category_title_uz="Korxona yuridik ma'lumotlari",
            title_uz="Ustav va ta'sis shartnomasi (agar mavjud bo'lsa)",
            status=ChecklistItemStatus.AVAILABLE if "cluster" in org_id or "exporter" in org_id else ChecklistItemStatus.NOT_APPLICABLE,
            rationale_uz="Korxona boshqaruv vakolatlari va ta'sischilar ulushini belgilaydi.",
            is_critical=False
        ),
        ChecklistItem(
            id="chk-comp-passport",
            category="COMPANY_INFO",
            category_title_uz="Korxona yuridik ma'lumotlari",
            title_uz="Rahbar va bosh buxgalter shaxsini tasdiqlovchi hujjatlar",
            status=ChecklistItemStatus.AVAILABLE,
            rationale_uz="Imzo huquqiga ega mansabdor shaxslarni identifikatsiyalash.",
            is_critical=True
        ),

        # 2. Financial Information
        ChecklistItem(
            id="chk-fin-bank-stmt",
            category="FINANCIAL_INFO",
            category_title_uz="Moliyaviy ko'rsatkichlar va hisobotlar",
            title_uz="So'nggi 12 oylik bank hisobvarag'i ko'chirmasi (Bank Statement)",
            status=ChecklistItemStatus.AVAILABLE if is_imported else ChecklistItemStatus.NEEDS_REVIEW,
            rationale_uz="Haqiqiy pul tushumlari, o'g'it/yoqilg'i chiqimlari va mavsumiy aylanmani baholash.",
            is_critical=True
        ),
        ChecklistItem(
            id="chk-fin-tax",
            category="FINANCIAL_INFO",
            category_title_uz="Moliyaviy ko'rsatkichlar va hisobotlar",
            title_uz="Soliq qo'mitasi solishtirma dalolatnomasi va 1/2-sonli moliyaviy hisobotlar",
            status=ChecklistItemStatus.AVAILABLE,
            rationale_uz="Soliq qarzdorligi yo'qligini va yillik daromad deklaratsiyasini tasdiqlash.",
            is_critical=True
        ),
        ChecklistItem(
            id="chk-fin-debt-cert",
            category="FINANCIAL_INFO",
            category_title_uz="Moliyaviy ko'rsatkichlar va hisobotlar",
            title_uz="Mavjud kreditlar va lizing majburiyatlari bo'yicha bank ma'lumotnomasi",
            status=ChecklistItemStatus.AVAILABLE,
            rationale_uz="Joriy kredit yuki va foiz to'lovlari grafigini tekshirish.",
            is_critical=True
        ),

        # 3. Agricultural & Land Information
        ChecklistItem(
            id="chk-agro-land-lease",
            category="AGRICULTURAL_INFO",
            category_title_uz="Agrar faoliyat va yer maydoni",
            title_uz="Uzoq muddatli yer ijarasi shartnomasi va kadastr pasporti",
            status=ChecklistItemStatus.AVAILABLE,
            rationale_uz="VMQ-613 bo'yicha yer ijarasi huquqini garov sifatida baholash uchun zarur.",
            is_critical=True
        ),
        ChecklistItem(
            id="chk-agro-bonitet",
            category="AGRICULTURAL_INFO",
            category_title_uz="Agrar faoliyat va yer maydoni",
            title_uz="Tuproq boniteti baholash xulosasi (O'zdaverloyiha)",
            status=ChecklistItemStatus.AVAILABLE,
            rationale_uz="Yer unumdorligi va hosildorlik salohiyatini aniqlash.",
            is_critical=False
        ),
        ChecklistItem(
            id="chk-agro-crop-plan",
            category="AGRICULTURAL_INFO",
            category_title_uz="Agrar faoliyat va yer maydoni",
            title_uz="Ekin ekish xaritasi va hosil yig'ishtirish rejasi",
            status=ChecklistItemStatus.AVAILABLE,
            rationale_uz="Mavsumiy tushumlar kalendarini prognoz qilish uchun asos.",
            is_critical=True
        ),

        # 4. Business & Contracts
        ChecklistItem(
            id="chk-biz-plan",
            category="BUSINESS_INFO",
            category_title_uz="Biznes reja va bozor aloqalari",
            title_uz="Moliyalashtirish maqsadi bo'yicha Biznes Reja / TIA",
            status=ChecklistItemStatus.AVAILABLE,
            rationale_uz="Kredit mablag'larining o'zini oqlashi va qaytarilish manbalarini isbotlash.",
            is_critical=True
        ),
        ChecklistItem(
            id="chk-biz-offtake",
            category="BUSINESS_INFO",
            category_title_uz="Biznes reja va bozor aloqalari",
            title_uz="Klaster yoki xaridorlar bilan fyuchers/kontraktatsiya shartnomalari",
            status=ChecklistItemStatus.NEEDS_REVIEW,
            rationale_uz="Yetishtirilgan mahsulotning kafolatlangan sotilishini tasdiqlash.",
            is_critical=False
        ),

        # 5. Financing & Collateral
        ChecklistItem(
            id="chk-fin-collateral",
            category="FINANCING_INFO",
            category_title_uz="Garov ta'minoti va kredit parametrlari",
            title_uz="Taklif etilayotgan garov ta'minoti mulk hujjatlari yoki VMQ-613 ijara huquqi",
            status=ChecklistItemStatus.AVAILABLE,
            rationale_uz="Kredit qaytmaslik xatarini sug'urtalash va ta'minot koeffitsientini ta'minlash.",
            is_critical=True
        )
    ]

    avail = sum(1 for i in items if i.status == ChecklistItemStatus.AVAILABLE)
    miss = sum(1 for i in items if i.status == ChecklistItemStatus.MISSING)
    review = sum(1 for i in items if i.status == ChecklistItemStatus.NEEDS_REVIEW)
    total = len(items)
    pct = round((avail / total) * 100, 1)

    return DocumentReadinessChecklist(
        items=items,
        total_items=total,
        available_count=avail,
        missing_count=miss,
        needs_review_count=review,
        completeness_percentage=pct
    )


def assess_financial_readiness(
    forecast: SeasonalForecastResponse,
    checklist: DocumentReadinessChecklist,
    profile: CreditProfile
) -> FinancialReadinessAssessment:
    """
    Executes an explainable, deterministic credit readiness assessment.
    Combines data completeness, DSCR coverage, cash-flow continuity, and debt load.
    Does NOT output fake probability of bank loan approval.
    """
    score = 50  # Baseline
    strengths: List[str] = []
    risks: List[str] = []
    limitations: List[str] = []

    # 1. Checklist Completeness Impact (+/- 20 pts)
    if checklist.completeness_percentage >= 80.0:
        score += 20
        strengths.append(f"Hujjatlar to'liqligi yuqori ({checklist.completeness_percentage}%) — birlamchi tahlil uchun yetarli.")
    elif checklist.completeness_percentage >= 60.0:
        score += 10
        strengths.append(f"Hujjatlar to'liqligi o'rtacha ({checklist.completeness_percentage}%).")
    else:
        score -= 10
        risks.append("Kredit arizasi uchun muhim hujjatlar yetishmaydi (60% dan past).")

    # 2. DSCR Factor (+/- 25 pts)
    dscr = forecast.annual_dscr
    if dscr is not None:
        if dscr >= Decimal("1.50"):
            score += 20
            strengths.append(f"Mustahkam DSCR koeffitsienti ({dscr:.2f}x) — qarz to'lovlarini xavfsiz qoplash imkoniyati mavjud.")
            dscr_uz = f"Yetarli va ishonchli ({dscr:.2f}x). Bankning 1.25x minimal talabidan yuqori."
        elif dscr >= Decimal("1.20"):
            score += 10
            strengths.append(f"Mo'tadil DSCR koeffitsienti ({dscr:.2f}x) — bank tavsiyaviy talablariga mos.")
            dscr_uz = f"Mo'tadil qoplash darajasi ({dscr:.2f}x)."
        elif dscr >= Decimal("1.00"):
            score -= 5
            risks.append(f"Cheklangan DSCR ({dscr:.2f}x) — tushum biroz kamaysa, kredit to'lashda qiyinchilik tug'ilishi mumkin.")
            dscr_uz = f"Cheklangan oraliq ({dscr:.2f}x)."
        else:
            score -= 20
            risks.append(f"Kritik darajadagi DSCR ({dscr:.2f}x) — operatsion kassa oqimi qarz xizmatini qoplashga yetmaydi.")
            dscr_uz = f"Kritik yetarsiz ({dscr:.2f}x)."
    else:
        dscr_uz = "Mavjud qarz yuki aniqlanmadi."
        strengths.append("Amaldagi bank kreditlari yuki mavjud emas.")

    # 3. Cash Flow Deficit Factor (+/- 15 pts)
    if forecast.months_in_deficit == 0:
        score += 10
        strengths.append("Yil davomida kassa defitsiti (manfiy qoldiq) kuzatilmadi.")
        cf_stability_uz = "Barqaror: Yil davomida barcha oylarda ijobiy kassa balansi saqlanadi."
    else:
        score -= 10
        risks.append(f"Bahorgi ekin ekish davrida {forecast.months_in_deficit} oy kassa taqchilligi (uzilishi) mavjud.")
        cf_stability_uz = f"Mavsumiy kassa uzilishi: {forecast.lowest_cash_month} oyida eng past kassa nuqtasi ({forecast.lowest_cash_point:,.2f} so'm)."

    # 4. Operating History & Land Collateral (+/- 10 pts)
    if profile.operating_years >= 5:
        score += 5
        strengths.append(f"Korxonaning {profile.operating_years} yillik barqaror faoliyat tajribasi mavjud.")
    if profile.land_hectares >= 50.0:
        score += 5
        strengths.append(f"Katta ekin maydoni ({profile.land_hectares} ga) va barqaror ishlab chiqarish bazasi.")

    # Clamp Score (0-100)
    final_score = max(0, min(100, score))

    # Determine Readiness Status
    if final_score >= 70 and checklist.completeness_percentage >= 75.0:
        status = ReadinessStatusEnum.READY_FOR_REVIEW
        status_label = "BANK KREDIT QO'MITASI KO'RIB CHIQISHIGA TAYYOR"
    elif final_score >= 50:
        status = ReadinessStatusEnum.ADDITIONAL_INFO_REQUIRED
        status_label = "QO'SHIMCHA MA'LUMOT VA HUJJATLAR TALAB ETILADI"
    else:
        status = ReadinessStatusEnum.INSUFFICIENT_DATA
        status_label = "MOLIYAVIY MA'LUMOTLAR VA TAHLIL YETARLI EMAS"

    # Limitations
    limitations.append("Tahlil taqdim etilgan bank ko'chirmalari va farazlarga asoslangan bo'lib, to'liq buxgalteriya balansi hisoblanmaydi.")
    limitations.append("Tashqi auditorlik xulosasi yoki mustaqil baholovchi garov bahosi o'rnini bosmaydi.")
    limitations.append("Mazkur xulosa bank tomonidan kredit ajratilishi kafolatini bermaydi.")

    disclaimer = (
        "DIQQAT: Ushbu kreditga tayyorgarlik bahosi AgroHisob CFO avtomatlashtirilgan moliyaviy tahlil tizimi "
        "tomonidan shakllantirilgan. U bank kredit qo'mitasining rasmiy qarori hisoblanmaydi va tijorat "
        "banklari tomonidan qo'shimcha tekshiruvlar talab etilishi mumkin."
    )

    return FinancialReadinessAssessment(
        overall_status=status,
        status_label_uz=status_label,
        readiness_score=final_score,
        data_completeness_pct=checklist.completeness_percentage,
        cash_flow_stability_uz=cf_stability_uz,
        dscr_capacity_uz=dscr_uz,
        forecast_confidence_uz="Deterministik agrar tsikl va hosildorlik farazlariga asoslangan",
        key_strengths_uz=strengths,
        identified_risks_uz=risks,
        critical_limitations_uz=limitations,
        audit_disclaimer_uz=disclaimer
    )
