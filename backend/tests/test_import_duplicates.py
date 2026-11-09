"""
Unit tests for DuplicateDetector in AgroHisob CFO Smart Import Engine.
"""

from datetime import date
from decimal import Decimal
from app.import_engine.duplicate_detector import DuplicateDetector
from app.import_engine.schemas import NormalizedRowData, TransactionDirection


def setup_function():
    DuplicateDetector.clear_cache_for_org("test-org-01")


def test_file_level_duplicate_detection():
    org = "test-org-01"
    sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    assert DuplicateDetector.is_file_duplicate(org, sha) is False
    DuplicateDetector.register_file(org, sha)
    assert DuplicateDetector.is_file_duplicate(org, sha) is True


def test_row_level_fingerprint_generation():
    org = "test-org-01"
    row1 = NormalizedRowData(
        transaction_date=date(2026, 3, 12),
        amount=Decimal("28000000.00"),
        direction=TransactionDirection.OUTFLOW,
        counterparty_name="Farg'onaAzot AJ",
        counterparty_inn="200025114",
        document_number="PP-101"
    )
    fp1 = DuplicateDetector.generate_row_fingerprint(org, row1)
    assert len(fp1) == 64

    # Identical row produces exact same fingerprint
    row2 = NormalizedRowData(
        transaction_date=date(2026, 3, 12),
        amount=Decimal("28000000.00"),
        direction=TransactionDirection.OUTFLOW,
        counterparty_name="Farg'onaAzot AJ",
        counterparty_inn="200025114",
        document_number="PP-101"
    )
    fp2 = DuplicateDetector.generate_row_fingerprint(org, row2)
    assert fp1 == fp2

    # Different amount produces different fingerprint
    row3 = NormalizedRowData(
        transaction_date=date(2026, 3, 12),
        amount=Decimal("29000000.00"),
        direction=TransactionDirection.OUTFLOW,
        counterparty_name="Farg'onaAzot AJ",
        counterparty_inn="200025114",
        document_number="PP-101"
    )
    fp3 = DuplicateDetector.generate_row_fingerprint(org, row3)
    assert fp1 != fp3


def test_intra_batch_duplicate_detection():
    org = "test-org-01"
    row = NormalizedRowData(
        transaction_date=date(2026, 3, 12),
        amount=Decimal("28000000.00"),
        direction=TransactionDirection.OUTFLOW,
        counterparty_name="Farg'onaAzot AJ",
        counterparty_inn="200025114",
        document_number="PP-101"
    )
    # List containing identical duplicates
    rows = [row, row]
    results = DuplicateDetector.check_intra_batch_duplicates(org, rows)

    assert len(results) == 2
    # First row is fresh, second row is duplicate
    assert results[0][1] is False
    assert results[1][1] is True
