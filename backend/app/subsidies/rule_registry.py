"""
AgroHisob CFO - Subsidy Program Rule Registry (Assignment 6, Module B)
Stores authoritative, versioned rules for agricultural subsidies under PQ-47 and PF-82.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from app.subsidies.schemas import SubsidyProgram

SUBSIDY_PROGRAMS: Dict[str, SubsidyProgram] = {
    "PQ47-DRIP-COTTON": SubsidyProgram(
        id="sub-pq47-drip-cotton",
        program_code="PQ47-DRIP-COTTON",
        program_name_uz="Paxta maydonlarida tomchilatib sug'orish tizimini joriy etish subsidiyasi",
        managing_authority_uz="Suv xo'jaligi vazirligi va Qishloq xo'jaligi vazirligi",
        legal_source_code="PQ-47",
        legal_source_url="https://lex.uz/uz/docs/-8036872",
        legal_clause="2-ilova, 1-band",
        effective_from=date(2026, 2, 5),
        effective_to=None,
        is_active=True,
        verification_status="VERIFIED_ACTIVE",
        supported_crops=["Paxta", "Paxta xom ashyosi"],
        supported_technologies=["DRIP_IRRIGATION", "TOMCHILATIB"],
        eligible_regions=[],  # All regions
        base_rate_uzs_per_ha=Decimal("8000000.00"),
        rate_description_uz="1 gektar paxta maydoniga 8 000 000 so'm bazaviy subsidiya (2 bosqichda: 50% / 50%)",
        interest_compensation_pct_points=None,
        required_documents_uz=[
            "Suv tejovchi tizim o'rnatilganligi to'g'risida tuman komissiyasi dalolatnomasi",
            "Pudratchi bilan tuzilgan shartnoma va hisob-fakturalar",
            "Tizimning to'liq ishga tushirilganligi haqida foto/video hisobot",
            "Bank rekvizitlari va arizasi"
        ]
    ),
    "PQ47-DRIP-VEGETABLES": SubsidyProgram(
        id="sub-pq47-drip-veg",
        program_code="PQ47-DRIP-VEGETABLES",
        program_name_uz="Sabzavot, poliz va kartoshka maydonlarida tomchilatib sug'orish subsidiyasi",
        managing_authority_uz="Qishloq xo'jaligi vazirligi",
        legal_source_code="PQ-47",
        legal_source_url="https://lex.uz/uz/docs/-8036872",
        legal_clause="2-ilova, 2-band",
        effective_from=date(2026, 2, 5),
        effective_to=None,
        is_active=True,
        verification_status="VERIFIED_ACTIVE",
        supported_crops=["Sabzavot", "Poliz", "Kartoshka", "Mavsumiy Sabzavotlar"],
        supported_technologies=["DRIP_IRRIGATION", "TOMCHILATIB"],
        eligible_regions=[],
        base_rate_uzs_per_ha=Decimal("6000000.00"),
        rate_description_uz="1 gektar sabzavot maydoniga 6 000 000 so'm bazaviy subsidiya (2 bosqichda: 50% / 50%)",
        interest_compensation_pct_points=None,
        required_documents_uz=[
            "Tizim o'rnatilganligi haqida tuman ishchi guruhi dalolatnomasi",
            "Hisob-faktura va to'lov hujjatlari"
        ]
    ),
    "PQ47-DRIP-ORCHARD": SubsidyProgram(
        id="sub-pq47-drip-orchard",
        program_code="PQ47-DRIP-ORCHARD",
        program_name_uz="Meva va intensiv bog'larda tomchilatib sug'orish subsidiyasi",
        managing_authority_uz="Qishloq xo'jaligi vazirligi va Bog'dorchilik agentligi",
        legal_source_code="PQ-47",
        legal_source_url="https://lex.uz/uz/docs/-8036872",
        legal_clause="3-band",
        effective_from=date(2026, 2, 5),
        effective_to=None,
        is_active=True,
        verification_status="VERIFIED_ACTIVE",
        supported_crops=["Meva", "Bog'dorchilik", "Intensiv bog'", "Gilos", "Olma"],
        supported_technologies=["DRIP_IRRIGATION", "TOMCHILATIB"],
        eligible_regions=[],
        base_rate_uzs_per_ha=Decimal("11000000.00"),
        rate_description_uz="1 gektar mevali bog' maydoniga 11 000 000 so'm bazaviy subsidiya (suv tanqis hududlarda 1.25x koeffitsiyent)",
        interest_compensation_pct_points=None,
        required_documents_uz=[
            "Intensiv bog' loyihasi va dalolatnoma",
            "Xarid qilingan uskunalar va o'rnatish dalolatnomasi"
        ]
    ),
    "PQ47-DRIP-VINEYARD": SubsidyProgram(
        id="sub-pq47-drip-vineyard",
        program_code="PQ47-DRIP-VINEYARD",
        program_name_uz="Uzumzorlarda tomchilatib sug'orish tizimini joriy etish subsidiyasi",
        managing_authority_uz="Qishloq xo'jaligi vazirligi",
        legal_source_code="PQ-47",
        legal_source_url="https://lex.uz/uz/docs/-8036872",
        legal_clause="2-ilova, 4-band",
        effective_from=date(2026, 2, 5),
        effective_to=None,
        is_active=True,
        verification_status="VERIFIED_ACTIVE",
        supported_crops=["Uzum", "Uzumzor", "Xo'raki uzum"],
        supported_technologies=["DRIP_IRRIGATION", "TOMCHILATIB"],
        eligible_regions=[],
        base_rate_uzs_per_ha=Decimal("8000000.00"),
        rate_description_uz="1 gektar uzumzorga 8 000 000 so'm bazaviy subsidiya",
        interest_compensation_pct_points=None,
        required_documents_uz=[
            "Uzumzor kadastr hujjati va o'rnatilganlik dalolatnomasi"
        ]
    ),
    "PQ47-INTEREST-COMPENSATION": SubsidyProgram(
        id="sub-pq47-int-comp",
        program_code="PQ47-INTEREST-COMPENSATION",
        program_name_uz="Suv tejovchi texnologiyalar kreditlari bo'yicha foiz kompensatsiyasi",
        managing_authority_uz="Qishloq xo'jaligini qo'llab-quvvatlash jamg'armasi",
        legal_source_code="PQ-47",
        legal_source_url="https://lex.uz/uz/docs/-8036872",
        legal_clause="3-band",
        effective_from=date(2026, 2, 5),
        effective_to=None,
        is_active=True,
        verification_status="VERIFIED_ACTIVE",
        supported_crops=["Paxta", "G'alla", "Sabzavot", "Bog'dorchilik", "Uzum"],
        supported_technologies=["DRIP_IRRIGATION", "SPRINKLER"],
        eligible_regions=[],
        base_rate_uzs_per_ha=None,
        rate_description_uz="Kredit foiz stavkasining 4 foiz bandi davlat Jamg'armasi hisobidan qoplab beriladi",
        interest_compensation_pct_points=Decimal("4.00"),
        required_documents_uz=[
            "Bank kredit shartnomasi va so'ndirish grafigi",
            "Mablag' maqsadli ishlatilganligi haqida dalolatnoma"
        ]
    ),
    "PF82-COTTON-INTEREST": SubsidyProgram(
        id="sub-pf82-cotton-int",
        program_code="PF82-COTTON-INTEREST",
        program_name_uz="Paxta yetishtiruvchilar uchun imtiyozli kredit foizini kompensatsiya qilish",
        managing_authority_uz="Agrar sohada to'lovlar agentligi",
        legal_source_code="PF-82",
        legal_source_url="https://lex.uz/uz/acts/-8187068",
        legal_clause="1-band",
        effective_from=date(2026, 5, 8),
        effective_to=None,
        is_active=True,
        verification_status="VERIFIED_ACTIVE",
        supported_crops=["Paxta", "Paxta xom ashyosi"],
        supported_technologies=[],
        eligible_regions=[],
        base_rate_uzs_per_ha=None,
        rate_description_uz="Shartnomada belgilangan muddatda qaytarilganda 2.5 foiz punkti; hosil yili 31-dekabriga qadar to'liq qaytarilganda 5.0 foiz punkti kompensatsiya qilinadi",
        interest_compensation_pct_points=Decimal("5.00"),
        required_documents_uz=[
            "Paxta yetishtirish uchun kredit shartnomasi",
            "Bank ma'lumotnomasi (qarz o'z vaqtida to'langanligi to'g'risida)",
            "Muddati o'tgan qarzdorlik yo'qligi dalolatnomasi"
        ]
    ),
    "PF82-WHEAT-INTEREST": SubsidyProgram(
        id="sub-pf82-wheat-int",
        program_code="PF82-WHEAT-INTEREST",
        program_name_uz="G'alla yetishtiruvchilar uchun imtiyozli kredit foizini kompensatsiya qilish",
        managing_authority_uz="Agrar sohada to'lovlar agentligi",
        legal_source_code="PF-82",
        legal_source_url="https://lex.uz/uz/acts/-8187068",
        legal_clause="1-band",
        effective_from=date(2026, 5, 8),
        effective_to=None,
        is_active=True,
        verification_status="VERIFIED_ACTIVE",
        supported_crops=["G'alla", "Bug'doy"],
        supported_technologies=[],
        eligible_regions=[],
        base_rate_uzs_per_ha=None,
        rate_description_uz="Shartnomada belgilangan muddatda qaytarilganda 2.5 foiz punkti; hosil yili 31-dekabriga qadar to'liq qaytarilganda 5.0 foiz punkti kompensatsiya qilinadi",
        interest_compensation_pct_points=Decimal("5.00"),
        required_documents_uz=[
            "G'alla agrotexnikasi uchun kredit shartnomasi",
            "Bank ma'lumotnomasi"
        ]
    )
}


def get_subsidy_program(code: str) -> Optional[SubsidyProgram]:
    return SUBSIDY_PROGRAMS.get(code.upper())


def list_subsidy_programs() -> List[SubsidyProgram]:
    return list(SUBSIDY_PROGRAMS.values())
