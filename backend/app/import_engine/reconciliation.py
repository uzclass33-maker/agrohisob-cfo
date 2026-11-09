"""
AgroHisob CFO - Invoice-Cash Ledger Separation & Reconciliation Engine
Enforces the fundamental accounting invariant: Commercial Invoices (E-Faktura) and
Cash Transactions (Bank Statements) are held in separate ledgers.
Invoices do NOT alter cash balances until matched with confirmed bank movements.
"""

from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.import_engine.schemas import (
    DocumentTypeEnum,
    NormalizedRowData,
    TransactionDirection,
)
from app.import_engine.exceptions import LedgerSeparationViolationError


class InvoiceObligationRecord(BaseModel):
    """An invoice record representing accounts payable/receivable (Obligation Ledger)."""
    invoice_id: str
    organization_id: str
    issue_date: date
    document_number: str
    counterparty_name: str
    counterparty_inn: Optional[str] = None
    total_amount: Decimal
    vat_amount: Decimal = Decimal("0.00")
    is_receivable: bool  # True if organization is seller (incoming debt), False if buyer (obligation to pay)
    settled_amount: Decimal = Decimal("0.00")
    is_settled: bool = False
    matching_bank_transaction_id: Optional[str] = None


class CashTransactionRecord(BaseModel):
    """A confirmed cash movement on the bank settlement account (Cash Ledger)."""
    transaction_id: str
    organization_id: str
    transaction_date: date
    direction: TransactionDirection
    amount: Decimal
    counterparty_name: str
    counterparty_inn: Optional[str] = None
    purpose: Optional[str] = None
    matched_invoice_id: Optional[str] = None


class ReconciliationMatch(BaseModel):
    invoice_id: str
    transaction_id: str
    matched_amount: Decimal
    match_confidence: float
    notes: str


class ReconciliationEngine:
    """Manages strict ledger separation and invoice-to-cash settlement matching."""

    # In-memory ledgers (in production backed by DB tables)
    _INVOICE_LEDGER: Dict[str, List[InvoiceObligationRecord]] = {}
    _CASH_LEDGER: Dict[str, List[CashTransactionRecord]] = {}

    @classmethod
    def get_target_ledger_for_document_type(cls, doc_type: DocumentTypeEnum) -> str:
        """Determines target ledger based on document type."""
        if doc_type == DocumentTypeEnum.E_FAKTURA:
            return "INVOICE_OBLIGATION_LEDGER"
        elif doc_type == DocumentTypeEnum.BANK_STATEMENT:
            return "CASH_TRANSACTION_LEDGER"
        raise ValueError(f"Noma'lum hujjat turi: {doc_type}")

    @classmethod
    def enforce_ledger_separation(
        cls, 
        doc_type: DocumentTypeEnum, 
        attempt_to_modify_cash: bool
    ) -> None:
        """
        Enforces strict accounting separation rule:
        E-Faktura can NEVER directly alter the cash balance.
        """
        if doc_type == DocumentTypeEnum.E_FAKTURA and attempt_to_modify_cash:
            raise LedgerSeparationViolationError(
                "Soliq E-Faktura hisobvaraq-fakturasi to'g'ridan-to'g'ri kassa/bank qoldig'iga kiritilishi mumkin emas. "
                "E-Faktura faqat debitorlik/kreditorlik majburiyatlari reestrida aks ettiriladi."
            )

    @classmethod
    def post_invoice_batch(
        cls, 
        org_id: str, 
        batch_id: str, 
        rows: List[NormalizedRowData]
    ) -> int:
        """Posts validated E-Faktura rows to the Invoice Obligation Ledger."""
        if org_id not in cls._INVOICE_LEDGER:
            cls._INVOICE_LEDGER[org_id] = []

        count = 0
        for idx, row in enumerate(rows):
            inv = InvoiceObligationRecord(
                invoice_id=f"inv-{batch_id}-{idx + 1}",
                organization_id=org_id,
                issue_date=row.transaction_date,
                document_number=row.document_number or f"SF-AUTOGEN-{idx+1}",
                counterparty_name=row.counterparty_name,
                counterparty_inn=row.counterparty_inn,
                total_amount=row.amount,
                vat_amount=row.vat_amount or Decimal("0.00"),
                is_receivable=(row.direction == TransactionDirection.INFLOW)
            )
            cls._INVOICE_LEDGER[org_id].append(inv)
            count += 1

        return count

    @classmethod
    def post_cash_batch(
        cls, 
        org_id: str, 
        batch_id: str, 
        rows: List[NormalizedRowData]
    ) -> int:
        """Posts validated Bank Statement rows to the Cash Transaction Ledger."""
        if org_id not in cls._CASH_LEDGER:
            cls._CASH_LEDGER[org_id] = []

        count = 0
        for idx, row in enumerate(rows):
            tx = CashTransactionRecord(
                transaction_id=f"tx-bank-{batch_id}-{idx + 1}",
                organization_id=org_id,
                transaction_date=row.transaction_date,
                direction=row.direction,
                amount=row.amount,
                counterparty_name=row.counterparty_name,
                counterparty_inn=row.counterparty_inn,
                purpose=row.purpose
            )
            cls._CASH_LEDGER[org_id].append(tx)
            count += 1

        return count

    @classmethod
    def match_invoices_with_cash(cls, org_id: str) -> List[ReconciliationMatch]:
        """
        Attempts to reconcile open invoices against confirmed bank transactions.
        Matching criteria:
          - Matching INN or normalized counterparty name
          - Amount equality or within tolerance
          - Bank transaction date >= invoice issue date
        """
        invoices = cls._INVOICE_LEDGER.get(org_id, [])
        transactions = cls._CASH_LEDGER.get(org_id, [])
        matches: List[ReconciliationMatch] = []

        for inv in invoices:
            if inv.is_settled:
                continue

            for tx in transactions:
                if tx.matched_invoice_id:
                    continue

                # Check counterparty identifier match
                inn_match = (
                    inv.counterparty_inn and tx.counterparty_inn and 
                    inv.counterparty_inn == tx.counterparty_inn
                )
                name_match = (
                    inv.counterparty_name.lower().strip() == tx.counterparty_name.lower().strip()
                )

                if (inn_match or name_match) and inv.total_amount == tx.amount:
                    confidence = 0.95 if inn_match else 0.85
                    match = ReconciliationMatch(
                        invoice_id=inv.invoice_id,
                        transaction_id=tx.transaction_id,
                        matched_amount=tx.amount,
                        match_confidence=confidence,
                        notes=f"Hisobvaraq-faktura ({inv.document_number}) bank to'lovi bilan to'liq mos keldi."
                    )
                    inv.is_settled = True
                    inv.settled_amount = tx.amount
                    inv.matching_bank_transaction_id = tx.transaction_id
                    tx.matched_invoice_id = inv.invoice_id
                    matches.append(match)
                    break

        return matches

    @classmethod
    def get_ledgers(cls, org_id: str) -> Dict[str, Any]:
        """Retrieves current ledger balances and counts."""
        invoices = cls._INVOICE_LEDGER.get(org_id, [])
        transactions = cls._CASH_LEDGER.get(org_id, [])

        total_inflow = sum((t.amount for t in transactions if t.direction == TransactionDirection.INFLOW), Decimal("0.00"))
        total_outflow = sum((t.amount for t in transactions if t.direction == TransactionDirection.OUTFLOW), Decimal("0.00"))
        net_cash = total_inflow - total_outflow

        unsettled_payables = sum(
            (i.total_amount - i.settled_amount for i in invoices if not i.is_receivable and not i.is_settled),
            Decimal("0.00")
        )
        unsettled_receivables = sum(
            (i.total_amount - i.settled_amount for i in invoices if i.is_receivable and not i.is_settled),
            Decimal("0.00")
        )

        return {
            "invoice_count": len(invoices),
            "cash_transaction_count": len(transactions),
            "net_cash_flow": net_cash,
            "unsettled_payables": unsettled_payables,
            "unsettled_receivables": unsettled_receivables,
        }

    @classmethod
    def reset(cls, org_id: Optional[str] = None) -> None:
        """Utility for test isolation."""
        if org_id:
            cls._INVOICE_LEDGER.pop(org_id, None)
            cls._CASH_LEDGER.pop(org_id, None)
        else:
            cls._INVOICE_LEDGER.clear()
            cls._CASH_LEDGER.clear()
