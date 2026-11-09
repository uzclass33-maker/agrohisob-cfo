"""
Unit tests for Normalizer in AgroHisob CFO Smart Import Engine.
"""

from datetime import date
from decimal import Decimal
from app.import_engine.normalizer import Normalizer


def test_numeric_normalization_uzs_formats():
    # Uzbek standard space thousand separator with comma decimal
    assert Normalizer.parse_amount("1 250 000,50") == Decimal("1250000.50")
    assert Normalizer.parse_amount("1 250 000,50 so'm") == Decimal("1250000.50")
    assert Normalizer.parse_amount("28 000 000") == Decimal("28000000.00")
    assert Normalizer.parse_amount("28 000 000 сум") == Decimal("28000000.00")

    # Standard dot decimal with comma thousands
    assert Normalizer.parse_amount("1,250,000.50") == Decimal("1250000.50")

    # Negative accounting numbers
    assert Normalizer.parse_amount("-15 000.00") == Decimal("-15000.00")
    assert Normalizer.parse_amount("(45 000,00)") == Decimal("-45000.00")

    # Empty, zero or dash representations
    assert Normalizer.parse_amount("0") == Decimal("0.00")
    assert Normalizer.parse_amount("-") is None
    assert Normalizer.parse_amount("") is None
    assert Normalizer.parse_amount(None) is None


def test_date_parsing_various_formats():
    # ISO
    assert Normalizer.parse_date("2026-03-15") == date(2026, 3, 15)

    # CIS / Uzbekistan standard DD.MM.YYYY
    assert Normalizer.parse_date("15.03.2026") == date(2026, 3, 15)
    assert Normalizer.parse_date("28/07/2026") == date(2026, 7, 28)

    # Excel serial number date: 45350 -> 2024-02-29
    parsed_excel_date = Normalizer.parse_date(45350)
    assert parsed_excel_date is not None
    assert parsed_excel_date.year == 2024

    # Invalid string
    assert Normalizer.parse_date("not_a_date") is None
    assert Normalizer.parse_date("") is None


def test_inn_stir_parsing():
    # Standard 9-digit INN
    assert Normalizer.parse_inn("200025114") == "200025114"
    assert Normalizer.parse_inn("STIR: 309 876 543") == "309876543"
    assert Normalizer.parse_inn("200025114000") == "200025114"

    # Too short or invalid
    assert Normalizer.parse_inn("123") is None
    assert Normalizer.parse_inn("") is None


def test_mxik_parsing():
    assert Normalizer.parse_mxik("20.15.10.101") == "20.15.10.101"
    assert Normalizer.parse_mxik("01111000001000000") == "01111000001000000"
    assert Normalizer.parse_mxik("") is None
