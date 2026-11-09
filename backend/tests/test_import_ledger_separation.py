"""
Unit tests for Accounting Ledger Separation and Invoice-Cash Reconciliation in AgroHisob CFO.
"""

from datetime import date
from decimal import Decimal
import pytest
from app.import_engine.reconciliation import ReconciliationEngine
from app.import_engine.schemas import (
    DocumentTypeEnum,
    NormalizedRowData,
    TransactionDirection,
)
from app.import_engine.exceptions import LedgerSeparationViolationError


def setup_function():
    ReconciliationEngine.reset()


def test_strict_ledger_separation_enforcement():
    # Attempting to post E-Faktura as cash must raise violation
    with pytest.raises(LedgerSeparationViolationError):
        ReconciliationEngine.enforce_ledger_separation(
            doc_type=DocumentTypeEnum.E_FAKTURA,
            attempt_to_modify_cash=True
        )

    # Bank statement modifying cash is valid and permitted
    ReconciliationEngine.enforce_ledger_separation(
        doc_type=DocumentTypeEnum.BANK_STATEMENT,
        attempt_to_modify_cash=True
    )


def test_invoice_posting_does_not_affect_cash_balance():
    org = "test-org-ledger-01"

    # Post E-Faktura invoice: 28,000,000 UZS payable for fertilizer
    invoice_row = NormalizedRowData(
        transaction_date=date(2026, 3, 15),
        amount=Decimal("28000000.00"),
        direction=TransactionDirection.OUTFLOW,
        counterparty_name="Farg'onaAzot AJ",
        counterparty_inn="200025114",
        document_number="SF-2026/0114"
    )
    count = ReconciliationEngine.post_invoice_batch(org, "batch-inv-01", [invoice_row])
    assert count == 1

    ledgers = ReconciliationEngine.get_ledgers(org)
    assert ledgers["invoice_count"] == 1
    assert ledgers["cash_transaction_count"] == 0
    # Crucial Invariant: Net cash flow remains 0!
    assert ledgers["net_cash_flow"] == Decimal("0.00")
    assert ledgers["unsettled_payables"] == Decimal("28000000.00")


def test_bank_statement_posting_updates_cash_balance():
    org = "test-org-ledger-02"

    # Post bank inflow: 100,000,000 UZS
    inflow_row = NormalizedRowData(
        transaction_date=date(2026, 6, 20),
        amount=Decimal("100000000.00"),
        direction=TransactionDirection.INFLOW,
        counterparty_name="Toshkent Agro Klaster",
        counterparty_inn="305112233"
    )
    # Post bank outflow: 40,000,000 UZS
    outflow_row = NormalizedRowData(
        transaction_date=date(2026, 6, 25),
        amount=Decimal("40000000.00"),
        direction=TransactionDirection.OUTFLOW,
        counterparty_name="O'zbekneftgaz",
        counterparty_inn="200115542"
    )

    count = ReconciliationEngine.post_cash_batch(org, "batch-bank-01", [inflow_row, outflow_row])
    assert count == 2

    ledgers = ReconciliationEngine.get_ledgers(org)
    assert ledgers["cash_transaction_count"] == 2
    # Net cash flow = 100M - 40M = 60M
    assert ledgers["net_cash_flow"] == Decimal("60000000.00")


def test_reconciliation_matching_invoice_with_bank_payment():
    org = "test-org-ledger-03"

    # 1. Post invoice
    inv_row = NormalizedRowData(
        transaction_date=date(2026, 3, 10),
        amount=Decimal("25000000.00"),
        direction=TransactionDirection.OUTFLOW,
        counterparty_name="Farg'onaAzot AJ",
        counterparty_inn="200025114",
        document_number="SF-7788"
    )
    ReconciliationEngine.post_invoice_batch(org, "batch-inv", [inv_row])

    # 2. Post matching bank transaction
    bank_row = NormalizedRowData(
        transaction_date=date(2026, 3, 12),
        amount=Decimal("25000000.00"),
        direction=TransactionDirection.OUTFLOW,
        counterparty_name="Farg'onaAzot AJ",
        counterparty_inn="200025114",
        purpose="To'lov SF-7788 bo'yicha"
    )
    ReconciliationEngine.post_cash_batch(org, "batch-bank", [bank_row])

    # 3. Match
    matches = ReconciliationEngine.match_invoices_with_cash(org)
    assert len(matches) == 1
    assert matches[0].matched_amount == Decimal("25000000.00")
    assert matches[0].match_confidence >= 0.90

    # Payables are now settled
    ledgers = ReconciliationEngine.get_ledgers(org)
    assert ledgers["unsettled_payables"] == Decimal("0.00")
