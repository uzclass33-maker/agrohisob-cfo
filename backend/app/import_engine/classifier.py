"""
AgroHisob CFO - Three-Tier Financial Classifier
Classifies transactions deterministically via MXIK codes, multilingual keyword heuristics,
and counterparty domain knowledge.
"""

from typing import Optional
from app.import_engine.schemas import (
    AgroFinancialCategory,
    ClassificationResult,
    DocumentTypeEnum,
    NormalizedRowData,
    TransactionDirection,
)
from app.import_engine.classification_rules import (
    CATEGORY_NAMES_UZ,
    MXIK_PREFIX_MAP,
    KEYWORD_RULES,
    COUNTERPARTY_RULES,
)
from app.import_engine.normalizer import Normalizer


class Classifier:
    """Deterministic, rule-based classification engine for agricultural transactions."""

    @classmethod
    def classify_by_mxik(cls, mxik_code: Optional[str]) -> Optional[ClassificationResult]:
        """Tier 1: Evaluates official State Tax Committee MXIK/IKPU prefixes."""
        if not mxik_code:
            return None

        clean_mxik = Normalizer.clean_text(mxik_code).replace(" ", "")
        if not clean_mxik:
            return None

        # Check prefixes of varying lengths (e.g., '01.11', '0111', '20.15', '2015')
        for prefix, (cat, conf) in MXIK_PREFIX_MAP.items():
            if clean_mxik.startswith(prefix):
                return ClassificationResult(
                    category=cat,
                    category_name_uz=CATEGORY_NAMES_UZ[cat],
                    confidence=conf,
                    rule_source="MXIK_DICTIONARY",
                    applied_rule=f"MXIK kodi prefiksi: {prefix}"
                )

        return None

    @classmethod
    def classify_by_keywords(cls, text_corpus: str) -> Optional[ClassificationResult]:
        """Tier 2: Evaluates Uzbek Latin, Uzbek Cyrillic, and Russian keyword patterns."""
        norm_text = Normalizer.clean_text(text_corpus).lower()
        if not norm_text:
            return None

        for cat, keywords, conf in KEYWORD_RULES:
            for kw in keywords:
                if kw in norm_text:
                    return ClassificationResult(
                        category=cat,
                        category_name_uz=CATEGORY_NAMES_UZ[cat],
                        confidence=conf,
                        rule_source="KEYWORD_HEURISTIC",
                        applied_rule=f"Kalit so'z: '{kw}'"
                    )

        return None

    @classmethod
    def classify_by_counterparty(cls, counterparty_name: str) -> Optional[ClassificationResult]:
        """Tier 3: Evaluates domain-specific counterparties (monopolies, banks, fuel suppliers)."""
        norm_cp = Normalizer.clean_text(counterparty_name).lower()
        if not norm_cp:
            return None

        for entity, cat, conf in COUNTERPARTY_RULES:
            if entity in norm_cp:
                return ClassificationResult(
                    category=cat,
                    category_name_uz=CATEGORY_NAMES_UZ[cat],
                    confidence=conf,
                    rule_source="COUNTERPARTY_RULE",
                    applied_rule=f"Kontragent profili: '{entity}'"
                )

        return None

    @classmethod
    def classify(
        cls, 
        row: NormalizedRowData, 
        document_type: DocumentTypeEnum = DocumentTypeEnum.BANK_STATEMENT
    ) -> ClassificationResult:
        """
        Executes hierarchical classification pipeline:
          Tier 1 (MXIK) -> Tier 2 (Keywords) -> Tier 3 (Counterparty) -> Tier 4 (Fallback)
        """
        # Tier 1: MXIK Code
        mxik_result = cls.classify_by_mxik(row.mxik_code)
        if mxik_result:
            return mxik_result

        # Tier 2: Keywords in payment purpose or description
        if row.purpose:
            keyword_result = cls.classify_by_keywords(row.purpose)
            if keyword_result:
                return keyword_result

        # Tier 3: Known Counterparty domain rules
        cp_result = cls.classify_by_counterparty(row.counterparty_name)
        if cp_result:
            return cp_result

        # Supplemental: Check keywords in counterparty name if not matched yet
        cp_keyword_result = cls.classify_by_keywords(row.counterparty_name)
        if cp_keyword_result:
            return cp_keyword_result

        # Tier 4: Fallback based on direction
        if row.direction == TransactionDirection.INFLOW:
            cat = AgroFinancialCategory.UNCATEGORIZED_INCOME
        else:
            cat = AgroFinancialCategory.UNCATEGORIZED_EXPENSE

        return ClassificationResult(
            category=cat,
            category_name_uz=CATEGORY_NAMES_UZ[cat],
            confidence=0.30,
            rule_source="DEFAULT_FALLBACK",
            applied_rule="Standart yo'nalish bo'yicha toifalash"
        )
