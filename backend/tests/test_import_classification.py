"""
Unit tests for Classifier in AgroHisob CFO Smart Import Engine.
"""

from datetime import date
from decimal import Decimal
from app.import_engine.classifier import Classifier
from app.import_engine.schemas import (
    AgroFinancialCategory,
    NormalizedRowData,
    TransactionDirection,
)


def test_tier1_mxik_classification():
    # Fertilizer MXIK
    row_fertilizer = NormalizedRowData(
        transaction_date=date(2026, 3, 12),
        amount=Decimal("28000000.00"),
        direction=TransactionDirection.OUTFLOW,
        counterparty_name="Kimyo Ta'minot MChJ",
        mxik_code="20.15.10.101"
    )
    res = Classifier.classify(row_fertilizer)
    assert res.category == AgroFinancialCategory.FERTILIZER_CHEMICALS
    assert res.rule_source == "MXIK_DICTIONARY"
    assert res.confidence >= 0.95

    # Cotton MXIK
    row_cotton = NormalizedRowData(
        transaction_date=date(2026, 7, 20),
        amount=Decimal("150000000.00"),
        direction=TransactionDirection.INFLOW,
        counterparty_name="Paxta Klaster MChJ",
        mxik_code="01.16.10.000"
    )
    res = Classifier.classify(row_cotton)
    assert res.category == AgroFinancialCategory.CROP_SALES_COTTON
    assert res.rule_source == "MXIK_DICTIONARY"


def test_tier2_keyword_classification():
    # Fuel keyword in purpose
    row_fuel = NormalizedRowData(
        transaction_date=date(2026, 3, 24),
        amount=Decimal("18500000.00"),
        direction=TransactionDirection.OUTFLOW,
        counterparty_name="MChJ YoQSh",
        purpose="Traktorlar uchun dizel yoqilg'isi (solyarka) xaridi"
    )
    res = Classifier.classify(row_fuel)
    assert res.category == AgroFinancialCategory.FUEL_LUBRICANTS
    assert res.rule_source == "KEYWORD_HEURISTIC"

    # Payroll keyword
    row_payroll = NormalizedRowData(
        transaction_date=date(2026, 8, 1),
        amount=Decimal("15000000.00"),
        direction=TransactionDirection.OUTFLOW,
        counterparty_name="Ishchilar jamoasi",
        purpose="Mavsumiy terimchilar uchun ish haqi to'lovi"
    )
    res = Classifier.classify(row_payroll)
    assert res.category == AgroFinancialCategory.LABOR_PAYROLL
    assert res.rule_source == "KEYWORD_HEURISTIC"


def test_tier3_counterparty_classification():
    # Known fertilizer plant
    row_fargona = NormalizedRowData(
        transaction_date=date(2026, 4, 1),
        amount=Decimal("35000000.00"),
        direction=TransactionDirection.OUTFLOW,
        counterparty_name="«Farg'onaAzot» AJ",
        purpose="Shartnoma №44 bo'yicha to'lov"  # No explicit fertilizer keyword in purpose
    )
    res = Classifier.classify(row_fargona)
    assert res.category == AgroFinancialCategory.FERTILIZER_CHEMICALS
    assert res.rule_source == "COUNTERPARTY_RULE"


def test_tier4_fallback_classification():
    # Ambiguous transaction with no MXIK, keywords, or known counterparty
    row_generic_outflow = NormalizedRowData(
        transaction_date=date(2026, 5, 10),
        amount=Decimal("2000000.00"),
        direction=TransactionDirection.OUTFLOW,
        counterparty_name="Omega Service MChJ",
        purpose="Shartnoma bo'yicha to'lov"
    )
    res = Classifier.classify(row_generic_outflow)
    assert res.category == AgroFinancialCategory.UNCATEGORIZED_EXPENSE
    assert res.rule_source == "DEFAULT_FALLBACK"
    assert res.confidence == 0.30

    row_generic_inflow = NormalizedRowData(
        transaction_date=date(2026, 5, 10),
        amount=Decimal("5000000.00"),
        direction=TransactionDirection.INFLOW,
        counterparty_name="Alpha Partner MChJ",
        purpose="To'lov"
    )
    res_inflow = Classifier.classify(row_generic_inflow)
    assert res_inflow.category == AgroFinancialCategory.UNCATEGORIZED_INCOME
    assert res_inflow.rule_source == "DEFAULT_FALLBACK"
