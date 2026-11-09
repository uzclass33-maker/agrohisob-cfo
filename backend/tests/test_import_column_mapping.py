"""
Unit tests for ColumnMapper in AgroHisob CFO Smart Import Engine.
"""

import pytest
from app.import_engine.column_mapper import ColumnMapper
from app.import_engine.schemas import DocumentTypeEnum
from app.import_engine.exceptions import UnmappedColumnError


def test_multilingual_synonym_matching():
    # Uzbek Latin
    field, score = ColumnMapper.match_header("Sana")
    assert field == "transaction_date"
    assert score == 1.0

    field, score = ColumnMapper.match_header("To'lov summasi")
    assert field == "amount"
    assert score == 1.0

    field, score = ColumnMapper.match_header("Kontragent INN")
    assert field == "counterparty_inn"
    assert score == 1.0

    # Uzbek Cyrillic
    field, score = ColumnMapper.match_header("Сана")
    assert field == "transaction_date"
    assert score == 1.0

    field, score = ColumnMapper.match_header("Сумма")
    assert field == "amount"
    assert score == 1.0

    field, score = ColumnMapper.match_header("Тўлов мақсади")
    assert field == "purpose"
    assert score == 1.0

    # Russian
    field, score = ColumnMapper.match_header("Дата операции")
    assert field == "transaction_date"
    assert score == 1.0

    field, score = ColumnMapper.match_header("Назначение платежа")
    assert field == "purpose"
    assert score == 1.0

    field, score = ColumnMapper.match_header("Код ИКПУ")
    assert field == "mxik_code"
    assert score == 1.0


def test_detect_mappings_bank_statement_headers():
    headers = [
        "Sana",
        "Debet",
        "Kredit",
        "Kontragent nomi",
        "STIR",
        "Hujjat №",
        "To'lov maqsadi"
    ]
    detected = ColumnMapper.detect_mappings(headers)
    target_map = {item.target_field: item.source_header for item in detected}

    assert target_map.get("transaction_date") == "Sana"
    assert target_map.get("debit") == "Debet"
    assert target_map.get("credit") == "Kredit"
    assert target_map.get("counterparty_name") == "Kontragent nomi"
    assert target_map.get("counterparty_inn") == "STIR"
    assert target_map.get("purpose") == "To'lov maqsadi"


def test_validate_required_mappings_success():
    valid_map = {
        "transaction_date": "Sana",
        "counterparty_name": "Hamkor",
        "amount": "Summa"
    }
    # Should not raise
    ColumnMapper.validate_required_mappings(valid_map, DocumentTypeEnum.BANK_STATEMENT)


def test_validate_required_mappings_missing_date():
    invalid_map = {
        "counterparty_name": "Hamkor",
        "amount": "Summa"
    }
    with pytest.raises(UnmappedColumnError) as exc_info:
        ColumnMapper.validate_required_mappings(invalid_map, DocumentTypeEnum.BANK_STATEMENT)
    assert "transaction_date" in exc_info.value.details["missing_columns"]


def test_validate_required_mappings_missing_amount_and_split_flows():
    invalid_map = {
        "transaction_date": "Sana",
        "counterparty_name": "Hamkor",
        "debit": "Debet"  # missing credit
    }
    with pytest.raises(UnmappedColumnError):
        ColumnMapper.validate_required_mappings(invalid_map, DocumentTypeEnum.BANK_STATEMENT)
