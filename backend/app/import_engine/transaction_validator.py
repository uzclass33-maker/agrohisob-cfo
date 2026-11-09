"""
AgroHisob CFO - Row-Level Transaction Validator
Validates extracted financial row data, verifies integrity constraints, direction rules,
and produces validation status and error messages.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from app.import_engine.schemas import (
    DocumentTypeEnum,
    NormalizedRowData,
    RowValidationStatus,
    TransactionDirection,
)
from app.import_engine.normalizer import Normalizer


class TransactionValidator:
    """Validates individual financial records against business and accounting rules."""

    @classmethod
    def resolve_direction(
        cls, 
        amount: Optional[Decimal], 
        raw_direction: Optional[str], 
        debit: Optional[Decimal], 
        credit: Optional[Decimal]
    ) -> Tuple[Optional[Decimal], Optional[TransactionDirection], List[str]]:
        """
        Determines the effective transaction direction (INFLOW vs OUTFLOW) and effective amount.
        """
        messages = []

        # Case 1: Separate Debit and Credit columns mapped
        if debit is not None or credit is not None:
            deb_val = debit or Decimal("0.00")
            cred_val = credit or Decimal("0.00")

            if cred_val > 0 and deb_val == 0:
                return cred_val, TransactionDirection.INFLOW, messages
            elif deb_val > 0 and cred_val == 0:
                return deb_val, TransactionDirection.OUTFLOW, messages
            elif cred_val > 0 and deb_val > 0:
                messages.append("Bir vaqtda debet va kredit mavjud. Kredit (kirim) ustuni tanlandi.")
                return cred_val, TransactionDirection.INFLOW, messages
            elif deb_val == 0 and cred_val == 0:
                return Decimal("0.00"), TransactionDirection.OUTFLOW, ["Debet va kredit miqdori 0 ga teng."]

        # Case 2: Unified Amount column mapped
        if amount is not None:
            if amount < 0:
                # Negative amount represents outflow / debit
                return abs(amount), TransactionDirection.OUTFLOW, messages

            if raw_direction:
                d_str = Normalizer.clean_text(raw_direction).lower()
                inflow_keywords = ["kirim", "kredit", "cr", "credit", "inflow", "+", "приход", "поступление", "зачисление"]
                outflow_keywords = ["chiqim", "debet", "db", "debit", "outflow", "-", "расход", "списание", "тўлов"]

                if any(k in d_str for k in inflow_keywords):
                    return amount, TransactionDirection.INFLOW, messages
                elif any(k in d_str for k in outflow_keywords):
                    return amount, TransactionDirection.OUTFLOW, messages
                else:
                    messages.append(f"Yo'nalish matni aniqlanmadi: '{raw_direction}'. Standart Chiqim (OUTFLOW) qabul qilindi.")
                    return amount, TransactionDirection.OUTFLOW, messages

            # If no raw direction provided, default to OUTFLOW for expenses/obligations unless positive context
            return amount, TransactionDirection.OUTFLOW, messages

        return None, None, ["Tranzaksiya summasi topilmadi."]

    @classmethod
    def validate_row(
        cls,
        row_dict: Dict[str, Any],
        mappings: Dict[str, str],  # target_field -> source_header
        document_type: DocumentTypeEnum,
        row_index: int
    ) -> Tuple[Optional[NormalizedRowData], RowValidationStatus, List[str]]:
        """
        Extracts mapped fields, normalizes them, and runs validation invariants.
        """
        messages: List[str] = []
        status = RowValidationStatus.VALID

        # Helper to get raw value by target field
        def get_val(target: str) -> Any:
            src_header = mappings.get(target)
            if src_header and src_header in row_dict:
                return row_dict[src_header]
            return None

        # 1. Date
        raw_date = get_val("transaction_date")
        tx_date = Normalizer.parse_date(raw_date)
        if not tx_date:
            messages.append(f"Qator {row_index}: Sana ko'rsatilmagan yoki format noto'g'ri ('{raw_date}').")
            status = RowValidationStatus.ERROR
        else:
            # Future date check (> 365 days ahead)
            max_future = date.today() + timedelta(days=365)
            if tx_date > max_future:
                messages.append(f"Qator {row_index}: Tranzaksiya sanasi kelajakda joylashgan ({tx_date}).")
                status = RowValidationStatus.WARNING

        # 2. Amounts and Direction
        raw_amount = Normalizer.parse_amount(get_val("amount"))
        raw_direction = get_val("direction")
        raw_debit = Normalizer.parse_amount(get_val("debit"))
        raw_credit = Normalizer.parse_amount(get_val("credit"))

        eff_amount, eff_direction, dir_msgs = cls.resolve_direction(
            amount=raw_amount,
            raw_direction=raw_direction,
            debit=raw_debit,
            credit=raw_credit
        )
        messages.extend(dir_msgs)

        if not eff_amount or eff_amount <= 0:
            messages.append(f"Qator {row_index}: Tranzaksiya summasi 0 dan katta bo'lishi shart.")
            status = RowValidationStatus.ERROR

        if not eff_direction:
            eff_direction = TransactionDirection.OUTFLOW

        # 3. Counterparty
        cp_name = Normalizer.clean_text(get_val("counterparty_name"))
        if not cp_name:
            messages.append(f"Qator {row_index}: Kontragent nomi ko'rsatilmagan.")
            if status != RowValidationStatus.ERROR:
                status = RowValidationStatus.WARNING
            cp_name = "Noma'lum kontragent"

        raw_inn = get_val("counterparty_inn")
        cp_inn = Normalizer.parse_inn(raw_inn)
        if raw_inn and not cp_inn:
            messages.append(f"Qator {row_index}: Kontragent INN/STIR formati noto'g'ri ('{raw_inn}').")
            if status == RowValidationStatus.VALID:
                status = RowValidationStatus.WARNING

        # 4. Optional fields
        doc_num = Normalizer.clean_text(get_val("document_number")) or None
        purpose = Normalizer.clean_text(get_val("purpose")) or None
        mxik_code = Normalizer.parse_mxik(get_val("mxik_code"))
        vat_amount = Normalizer.parse_amount(get_val("vat_amount")) or Decimal("0.00")
        bank_account = Normalizer.parse_bank_account(get_val("bank_account"))

        # 5. Document-Specific Invariants
        if document_type == DocumentTypeEnum.E_FAKTURA:
            if eff_amount and vat_amount > eff_amount:
                messages.append(f"Qator {row_index}: QQS summasi ({vat_amount}) umumiy summadan ({eff_amount}) katta bo'lishi mumkin emas.")
                status = RowValidationStatus.ERROR
            if not doc_num:
                messages.append(f"Qator {row_index}: Faktura raqami ko'rsatilmagan.")
                if status == RowValidationStatus.VALID:
                    status = RowValidationStatus.WARNING

        if status == RowValidationStatus.ERROR or not tx_date or not eff_amount:
            # Return partial normalized row or None
            dummy_date = tx_date or date.today()
            dummy_amount = eff_amount if (eff_amount and eff_amount > 0) else Decimal("0.01")
            normalized = NormalizedRowData(
                transaction_date=dummy_date,
                amount=dummy_amount,
                direction=eff_direction,
                counterparty_name=cp_name,
                counterparty_inn=cp_inn,
                document_number=doc_num,
                purpose=purpose,
                mxik_code=mxik_code,
                vat_amount=vat_amount,
                bank_account=bank_account
            )
            return normalized, RowValidationStatus.ERROR, messages

        normalized = NormalizedRowData(
            transaction_date=tx_date,
            amount=eff_amount,
            direction=eff_direction,
            counterparty_name=cp_name,
            counterparty_inn=cp_inn,
            document_number=doc_num,
            purpose=purpose,
            mxik_code=mxik_code,
            vat_amount=vat_amount,
            bank_account=bank_account
        )

        return normalized, status, messages
