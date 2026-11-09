"""
AgroHisob CFO - Regulatory Source Registry & Legal Rule Verification (Assignment 6)
Stores authoritative, versioned metadata for official Uzbek agricultural regulations:
- VMQ-613 (Land Lease Collateral)
- PQ-47 (Water-Saving Technology Subsidies)
- PF-82 (Cotton & Wheat Financial Support)
"""

from datetime import date
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class VerificationStatusEnum(str, Enum):
    VERIFIED_ACTIVE = "VERIFIED_ACTIVE"
    VERIFIED_AMENDED = "VERIFIED_AMENDED"
    UNVERIFIED = "UNVERIFIED"
    SUPERSEDED = "SUPERSEDED"


class RegulatorySourceRecord(BaseModel):
    id: str
    document_code: str                     # e.g. "VMQ-613", "PQ-47", "PF-82"
    document_title_uz: str
    official_lex_url: str
    issuing_authority_uz: str
    effective_from: date
    effective_to: Optional[date] = None
    verification_status: VerificationStatusEnum = VerificationStatusEnum.VERIFIED_ACTIVE
    last_verified_at: str = "2026-11-09"
    key_clauses_summary_uz: Dict[str, str] = Field(default_factory=dict)
    applicable_beneficiaries_uz: List[str] = Field(default_factory=list)


REGULATORY_SOURCES: Dict[str, RegulatorySourceRecord] = {
    "VMQ-613": RegulatorySourceRecord(
        id="reg-vmq-613",
        document_code="VMQ-613",
        document_title_uz=(
            "Vazirlar Mahkamasining 2025-yil 30-sentabrdagi 613-son qarori "
            "«Qishloq xo'jaligiga mo'ljallangan yer uchastkalarini ijaraga berish huquqini kredit ta'minoti sifatida garovga qo'yish tartibi to'g'risida»"
        ),
        official_lex_url="https://lex.uz/uz/docs/-7750301",
        issuing_authority_uz="O'zbekiston Respublikasi Vazirlar Mahkamasi",
        effective_from=date(2025, 9, 30),
        effective_to=None,
        verification_status=VerificationStatusEnum.VERIFIED_ACTIVE,
        last_verified_at="2026-11-09",
        key_clauses_summary_uz={
            "clause_5": "Yer uchastkasiga bo'lgan ijara huquqi davlat ro'yxatidan o'tkazilgan bo'lishi shart.",
            "clause_8": "Yer ijara shartnomasining qolgan muddati kreditni qaytarish muddatidan kamida 5 (besh) yil ko'p bo'lishi shart.",
            "clause_12": "Yer ijara huquqi bo'yicha taqiq (arest), xatlov, nizo yoki bekor qilish jarayoni bo'lmasligi shart.",
            "clause_14": "Ikkilamchi ijara (sub-lease) huquqi asosiy ijaraga beruvchi davlat organining yozma ruxsatisiz garovga qo'yilishi mumkin emas.",
            "clause_15": "Garovga qo'yiladigan yer ijara huquqining bozor qiymati qonunchilikda belgilangan tartibda litsenziyaga ega baholovchi tashkilot tomonidan baholanadi."
        },
        applicable_beneficiaries_uz=[
            "Fermer xo'jaliklari",
            "Qishloq xo'jaligi korxonalari",
            "Agrosanoat klasterlari"
        ]
    ),
    "PQ-47": RegulatorySourceRecord(
        id="reg-pq-47",
        document_code="PQ-47",
        document_title_uz=(
            "O'zbekiston Respublikasi Prezidentining 2026-yil 5-fevraldagi PQ-47-son qarori "
            "«Qishloq xo'jaligida suv tejovchi texnologiyalarni joriy etishni yanada jadallashtirish chora-tadbirlari to'g'risida»"
        ),
        official_lex_url="https://lex.uz/uz/docs/-8036872",
        issuing_authority_uz="O'zbekiston Respublikasi Prezidenti",
        effective_from=date(2026, 2, 5),
        effective_to=None,
        verification_status=VerificationStatusEnum.VERIFIED_ACTIVE,
        last_verified_at="2026-11-09",
        key_clauses_summary_uz={
            "clause_1": "Tomchilatib va yomg'irlatib sug'orish tizimlarini joriy etish uchun davlat byudjetidan subsidiyalar ajratish.",
            "clause_2": "Subsidiya to'lovlari 2 bosqichda amalga oshiriladi: 50% dalolatnoma tuzilgach, 50% 1 vegetatsiya mavsumida samarali ishlagach.",
            "clause_3": "Tijorat banklari tomonidan ajratiladigan imtiyozli kreditlar bo'yicha foiz xarajatining belgilangan qismi (asosiy stavkadan oshgan qismi) qoplab beriladi.",
            "clause_annex_2": "Ekin turlari bo'yicha 1 gektarga 6 mln dan 10 mln so'mgacha bazaviy me'yorlar."
        },
        applicable_beneficiaries_uz=[
            "Paxta-g'alla yetishtiruvchilar",
            "Meva-sabzavot agrofirmalari",
            "Bog'dorchilik va uzumchilik xo'jaliklari"
        ]
    ),
    "PF-82": RegulatorySourceRecord(
        id="reg-pf-82",
        document_code="PF-82",
        document_title_uz=(
            "O'zbekiston Respublikasi Prezidentining 2026-yil 8-maydagi PF-82-son Farmoni "
            "«Paxta va g'alla yetishtiruvchi qishloq xo'jaligi korxonalarini moliyaviy qo'llab-quvvatlash chora-tadbirlari to'g'risida»"
        ),
        official_lex_url="https://lex.uz/uz/acts/-8187068",
        issuing_authority_uz="O'zbekiston Respublikasi Prezidenti",
        effective_from=date(2026, 5, 8),
        effective_to=None,
        verification_status=VerificationStatusEnum.VERIFIED_ACTIVE,
        last_verified_at="2026-11-09",
        key_clauses_summary_uz={
            "clause_1": "Paxta va g'alla ekinlari uchun olingan agrotexnik kreditlar bo'yicha foiz xarajatlarini kompensatsiya qilish tartibi.",
            "clause_2": "Kredit to'lovlarini muddatida to'lagan intizomli fermerlarga yillik 10 foiz bandi davlat Jamg'armasi hisobidan kompensatsiya qilinadi.",
            "clause_3": "Muddati o'tgan (overdue) qarzdorlik mavjud bo'lgan kunlar uchun foiz kompensatsiyasi hisoblanmaydi."
        },
        applicable_beneficiaries_uz=[
            "Paxta xom ashyosi yetishtiruvchi fermer xo'jaliklari",
            "G'allachilik korxonalari va klasterlar"
        ]
    )
}


def get_regulatory_source(doc_code: str) -> Optional[RegulatorySourceRecord]:
    return REGULATORY_SOURCES.get(doc_code.upper())


def list_regulatory_sources() -> List[RegulatorySourceRecord]:
    return list(REGULATORY_SOURCES.values())
