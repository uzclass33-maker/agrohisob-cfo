"""
AgroHisob CFO - Smart Multilingual Column Mapper
Automatically maps raw spreadsheet headers to canonical system fields using domain-specific
synonym dictionaries covering Uzbek Latin, Uzbek Cyrillic, and Russian accounting practices.
"""

import re
from typing import Dict, List, Optional, Tuple
from app.import_engine.schemas import (
    ColumnMappingItem,
    DocumentTypeEnum,
    MappingProfileSchema,
)
from app.import_engine.exceptions import UnmappedColumnError


SYNONYM_DICTIONARY: Dict[str, List[str]] = {
    "transaction_date": [
        # Uzbek Latin
        "sana", "operatsiya sanasi", "o'tkazma sanasi", "hujjat sanasi", "to'lov sanasi", "vaqt", "data", "kun",
        # Uzbek Cyrillic
        "сана", "операция санаси", "ўтказма санаси", "тўлов санаси", "ҳужжат санаси", "вақт", "кун",
        # Russian
        "дата", "дата операции", "дата проводки", "дата документа", "дата платежа", "число", "дата с/ф"
    ],
    "amount": [
        # Uzbek Latin
        "summa", "operatsiya summasi", "to'lov summasi", "jami", "jami summa", "miqdor", "qiymat", "summa (so'm)", "umumiy summa",
        # Uzbek Cyrillic
        "сумма", "операция суммаси", "тўлов суммаси", "жами", "жами сумма", "қиймат", "умумий сумма",
        # Russian
        "сумма", "сумма операции", "сумма платежа", "всего", "итого", "сумма с ндс", "размер", "общая сумма", "сумма поставки"
    ],
    "direction": [
        # Uzbek Latin
        "yo'nalish", "turi", "operatsiya turi", "harakat", "kirim/chiqim",
        # Uzbek Cyrillic
        "йўналиш", "тури", "операция тури", "ҳаракат", "кирим/чиқим",
        # Russian
        "тип операции", "направление", "вид операции", "приход/расход"
    ],
    "debit": [
        # Uzbek Latin
        "debet", "chiqim", "xarajat", "debet summasi",
        # Uzbek Cyrillic
        "дебет", "чиқим", "харажат", "дебет суммаси",
        # Russian
        "дебет", "расход", "списание", "сумма дебета"
    ],
    "credit": [
        # Uzbek Latin
        "kredit", "kirim", "tushum", "kredit summasi",
        # Uzbek Cyrillic
        "кредит", "кирим", "тушум", "кредит суммаси",
        # Russian
        "кредит", "приход", "поступление", "зачисление", "сумма кредита"
    ],
    "counterparty_name": [
        # Uzbek Latin
        "kontragent", "hamkor", "tashkilot", "ta'minotchi", "xaridor", "yetkazib beruvchi", "oluvchi", "to'lovchi", "korxona nomi", "kontragent nomi",
        # Uzbek Cyrillic
        "контрагент", "ҳамкор", "ташкилот", "таъминотчи", "харидор", "етказиб берувчи", "олувчи", "тўловчи", "корхона номи", "контрагент номи",
        # Russian
        "контрагент", "наименование контрагента", "поставщик", "покупатель", "организация", "плательщик", "получатель", "наименование организации", "клиент"
    ],
    "counterparty_inn": [
        # Uzbek Latin
        "inn", "stir", "kontragent inn", "kontragent stir", "stir/inn", "xaridor inn", "sotuvchi inn", "inn/stir",
        # Uzbek Cyrillic
        "инн", "стир", "контрагент инн", "стир/инн", "инн/стир",
        # Russian
        "инн", "инн контрагента", "инн/кпп", "инн плательщика", "инн получателя", "инн покупателя", "инн поставщика"
    ],
    "document_number": [
        # Uzbek Latin
        "hujjat raqami", "faktura raqami", "shartnoma raqami", "hisobvaraq-faktura raqami", "sf raqami", "order raqami", "raqam", "hujjat №", "faktura №",
        # Uzbek Cyrillic
        "ҳужжат рақами", "фактура рақами", "шартнома рақами", "рақам", "ҳужжат №", "фактура №",
        # Russian
        "номер документа", "номер", "№ документа", "номер счет-фактуры", "счет-фактура №", "документ №", "номер п/п", "№", "номер счета"
    ],
    "purpose": [
        # Uzbek Latin
        "to'lov maqsadi", "tavsif", "izoh", "mazmuni", "maqsad", "to'lov tafsilotlari", "tovar/xizmat nomi", "tovar nomi", "xizmat tavsifi",
        # Uzbek Cyrillic
        "тўлов мақсади", "тавсиф", "изоҳ", "мазмуни", "товар номи", "хизмат номи",
        # Russian
        "назначение платежа", "описание", "содержание", "назначение", "товар/услуга", "наименование товара", "примечание", "детали платежа"
    ],
    "mxik_code": [
        # Uzbek Latin
        "mxik", "mxik kodi", "ikpu", "ikpu kodi", "mxik/ikpu", "tovar kodi", "mahsulot kodi", "ikpu/mxik",
        # Uzbek Cyrillic
        "мхик", "мхик коди", "икпу", "икпу коди", "мхик/икпу",
        # Russian
        "код икпу", "икпу", "мхик", "код мхик", "код товара", "икпу код", "классификатор икпу"
    ],
    "vat_amount": [
        # Uzbek Latin
        "qqs", "qqs summasi", "qo'shilgan qiymat solig'i", "nds",
        # Uzbek Cyrillic
        "ққс", "ққс суммаси",
        # Russian
        "ндс", "сумма ндс", "налог на добавленную стоимость", "в т.ч. ндс"
    ],
    "bank_account": [
        # Uzbek Latin
        "hisob raqam", "hisobraqam", "h/r", "korxona hisob raqami", "kontragent hisob raqami", "hisob varaq",
        # Uzbek Cyrillic
        "ҳисоб рақам", "ҳ/р",
        # Russian
        "расчетный счет", "р/с", "счет", "счет плательщика", "счет получателя", "лицевой счет"
    ]
}


class ColumnMapper:
    """Intelligent column mapper tailored for Uzbekistan financial records."""

    @classmethod
    def clean_header(cls, header: str) -> str:
        """Normalizes header string for comparison."""
        cleaned = header.lower().strip()
        cleaned = re.sub(r"[\s_]+", " ", cleaned)
        cleaned = re.sub(r"[^\w\s\(\)/№#']", "", cleaned)
        return cleaned.strip()

    @classmethod
    def match_header(cls, header: str) -> Tuple[Optional[str], float]:
        """
        Matches a single header against the synonym dictionary.
        Returns (target_field, confidence_score).
        """
        norm_h = cls.clean_header(header)
        if not norm_h:
            return None, 0.0

        # Exact match
        for target_field, synonyms in SYNONYM_DICTIONARY.items():
            for syn in synonyms:
                if norm_h == syn:
                    return target_field, 1.0

        # Substring / Containment match
        best_target = None
        best_score = 0.0

        for target_field, synonyms in SYNONYM_DICTIONARY.items():
            for syn in synonyms:
                # If syn is in norm_h or norm_h is in syn
                if syn in norm_h:
                    score = len(syn) / max(len(norm_h), 1)
                    score = min(0.90, max(0.60, score))
                    if score > best_score:
                        best_score = score
                        best_target = target_field
                elif norm_h in syn:
                    score = len(norm_h) / max(len(syn), 1)
                    score = min(0.85, max(0.55, score))
                    if score > best_score:
                        best_score = score
                        best_target = target_field

        if best_target and best_score >= 0.60:
            return best_target, round(best_score, 2)

        return None, 0.0

    @classmethod
    def detect_mappings(
        cls, 
        headers: List[str], 
        sample_rows: Optional[List[Dict[str, str]]] = None
    ) -> List[ColumnMappingItem]:
        """
        Analyzes provided headers and generates optimal column mappings.
        Ensures each canonical field is mapped at most once to the best scoring header.
        """
        items: List[ColumnMappingItem] = []
        assigned_targets = set()

        # Score all possible (header, target) pairs
        candidates = []
        for h in headers:
            target, score = cls.match_header(h)
            if target and score > 0.5:
                candidates.append((score, h, target))

        # Sort descending by score
        candidates.sort(key=lambda x: x[0], reverse=True)

        assigned_headers = set()
        for score, h, target in candidates:
            if target not in assigned_targets and h not in assigned_headers:
                assigned_targets.add(target)
                assigned_headers.add(h)

                samples = []
                if sample_rows:
                    for row in sample_rows[:3]:
                        val = row.get(h)
                        if val is not None and str(val).strip() != "":
                            samples.append(str(val).strip())

                items.append(
                    ColumnMappingItem(
                        source_header=h,
                        target_field=target,
                        confidence=score,
                        sample_values=samples
                    )
                )

        return items

    @classmethod
    def validate_required_mappings(
        cls, 
        mappings: Dict[str, str], 
        document_type: DocumentTypeEnum
    ) -> None:
        """
        Validates that minimum essential target fields are mapped for the document type.
        Raises UnmappedColumnError if mandatory columns are absent.
        """
        target_keys = set(mappings.keys())

        if "transaction_date" not in target_keys:
            raise UnmappedColumnError("Tranzaksiya sanasi (transaction_date) ustuni majburiy.", ["transaction_date"])

        if "counterparty_name" not in target_keys:
            raise UnmappedColumnError("Kontragent nomi (counterparty_name) ustuni majburiy.", ["counterparty_name"])

        # Check monetary amount mapping:
        # Either 'amount' (with or without 'direction') OR both 'debit' and 'credit'
        has_amount = "amount" in target_keys
        has_split_flows = "debit" in target_keys and "credit" in target_keys

        if not (has_amount or has_split_flows):
            raise UnmappedColumnError(
                "Mablag' ustunlari yetarli emas. Yo 'amount' ustuni, yoki bir vaqtda 'debit' va 'credit' ustunlari moslanishi shart.",
                ["amount", "debit", "credit"]
            )
