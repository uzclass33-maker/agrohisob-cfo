"""
AgroHisob CFO - Smart Import Orchestration Service
Coordinates file validation, parsing, multilingual column mapping, transaction normalization,
deterministic classification, duplicate prevention, and financial engine ledger posting.
"""

from datetime import datetime, timezone
from decimal import Decimal
import uuid
from typing import Any, Dict, List, Optional
from app.import_engine.exceptions import (
    ImportEngineError,
    DuplicateFileError,
    UnmappedColumnError,
)
from app.import_engine.schemas import (
    AgroFinancialCategory,
    BatchCommitRequest,
    BatchCommitResponse,
    ColumnMappingItem,
    DocumentTypeEnum,
    ImportBatchStatus,
    ImportHistoryItem,
    ImportPreviewResponse,
    NormalizedRowData,
    ParsedRowSchema,
    RowOverride,
    RowValidationStatus,
    TransactionDirection,
)
from app.import_engine.file_validator import FileValidator
from app.import_engine.spreadsheet_parser import SpreadsheetParser, RawSpreadsheetData
from app.import_engine.column_mapper import ColumnMapper
from app.import_engine.transaction_validator import TransactionValidator
from app.import_engine.duplicate_detector import DuplicateDetector
from app.import_engine.classifier import Classifier
from app.import_engine.reconciliation import ReconciliationEngine
from app.financial_engine.dscr import calculate_dscr
from app.financial_engine.schemas import DSCRCalculationRequest


class ImportBatchState:
    """Internal staging container for an active import batch."""
    def __init__(
        self,
        batch_id: str,
        org_id: str,
        file_name: str,
        file_hash: str,
        document_type: DocumentTypeEnum,
        raw_data: RawSpreadsheetData
    ):
        self.batch_id = batch_id
        self.org_id = org_id
        self.file_name = file_name
        self.file_hash = file_hash
        self.document_type = document_type
        self.raw_data = raw_data
        self.status = ImportBatchStatus.PARSED
        self.mappings: Dict[str, str] = {}
        self.detected_mapping_items: List[ColumnMappingItem] = []
        self.parsed_rows: List[ParsedRowSchema] = []
        self.created_at = datetime.now(timezone.utc)
        self.committed_at: Optional[datetime] = None


class ImportService:
    """Enterprise service orchestrating end-to-end financial data import workflows."""

    # Active staging storage
    _BATCHES: Dict[str, ImportBatchState] = {}
    _HISTORY: Dict[str, List[ImportHistoryItem]] = {}

    @classmethod
    def upload_and_stage(
        cls,
        file_name: str,
        content: bytes,
        document_type: DocumentTypeEnum,
        org_id: str = "demo-org-agro-01"
    ) -> ImportPreviewResponse:
        """
        Validates uploaded file, parses tabular contents, detects column mappings,
        and generates an initial preview with automatic classifications.
        """
        # 1. Security & format validation
        validation_res = FileValidator.validate(file_name, content)

        # 2. Duplicate file detection
        if DuplicateDetector.is_file_duplicate(org_id, validation_res.sha256_hash):
            raise DuplicateFileError(
                f"Ushbu fayl ('{file_name}') avvalroq import qilingan (SHA-256: {validation_res.sha256_hash[:12]}...).",
                file_hash=validation_res.sha256_hash
            )

        # 3. Parse spreadsheet
        raw_spreadsheet = SpreadsheetParser.parse(
            content=content,
            file_name=file_name,
            encoding=validation_res.detected_encoding if validation_res.detected_encoding != "binary" else "utf-8"
        )

        batch_id = str(uuid.uuid4())
        batch_state = ImportBatchState(
            batch_id=batch_id,
            org_id=org_id,
            file_name=file_name,
            file_hash=validation_res.sha256_hash,
            document_type=document_type,
            raw_data=raw_spreadsheet
        )

        # 4. Auto-detect column mapping
        mapping_items = ColumnMapper.detect_mappings(
            headers=raw_spreadsheet.headers,
            sample_rows=raw_spreadsheet.rows[:5]
        )
        batch_state.detected_mapping_items = mapping_items
        batch_state.mappings = {item.target_field: item.source_header for item in mapping_items}

        # 5. Process rows with initial mappings
        cls._process_rows_for_batch(batch_state)

        # 6. Store in active staging
        cls._BATCHES[batch_id] = batch_state

        return cls._build_preview_response(batch_state)

    @classmethod
    def apply_custom_mapping(
        cls,
        batch_id: str,
        mappings: Dict[str, str]
    ) -> ImportPreviewResponse:
        """Applies user-provided or adjusted column mappings and recalculates preview."""
        batch_state = cls._get_batch(batch_id)

        # Validate minimum required fields
        ColumnMapper.validate_required_mappings(mappings, batch_state.document_type)

        batch_state.mappings = mappings
        batch_state.status = ImportBatchStatus.MAPPED

        # Re-process rows
        cls._process_rows_for_batch(batch_state)

        return cls._build_preview_response(batch_state)

    @classmethod
    def override_row(
        cls,
        batch_id: str,
        row_id: str,
        override: RowOverride
    ) -> ParsedRowSchema:
        """Applies manual correction to a specific row before committing."""
        batch_state = cls._get_batch(batch_id)

        target_row = None
        for r in batch_state.parsed_rows:
            if r.row_id == row_id:
                target_row = r
                break

        if not target_row:
            raise ImportEngineError(f"Qator topilmadi: {row_id}")

        if target_row.normalized:
            if override.category:
                from app.import_engine.classification_rules import CATEGORY_NAMES_UZ
                from app.import_engine.schemas import ClassificationResult
                target_row.classification = ClassificationResult(
                    category=override.category,
                    category_name_uz=CATEGORY_NAMES_UZ.get(override.category, override.category.value),
                    confidence=1.0,
                    rule_source="MANUAL_USER_OVERRIDE",
                    applied_rule="Foydalanuvchi tomonidan qo'lda to'g'rilandi"
                )
            if override.direction:
                target_row.normalized.direction = override.direction
            if override.amount and override.amount > 0:
                target_row.normalized.amount = override.amount
            if override.counterparty_name:
                target_row.normalized.counterparty_name = override.counterparty_name
            if override.purpose:
                target_row.normalized.purpose = override.purpose

            # If it was marked as error or needs review, re-check
            if target_row.validation_status in (RowValidationStatus.ERROR, RowValidationStatus.NEEDS_REVIEW):
                target_row.validation_status = RowValidationStatus.VALID
                target_row.validation_messages.append("Foydalanuvchi tomonidan tahrirlandi va tasdiqlandi.")

        return target_row

    @classmethod
    def commit_batch(cls, request: BatchCommitRequest) -> BatchCommitResponse:
        """
        Finalizes an import batch, posts records into the appropriate ledger,
        and triggers financial engine recalculations.
        """
        batch_state = cls._get_batch(request.batch_id)

        # Apply any ad-hoc overrides provided in commit request
        for ovr in request.overrides:
            cls.override_row(request.batch_id, ovr.row_id, ovr)

        target_ledger = ReconciliationEngine.get_target_ledger_for_document_type(batch_state.document_type)

        # Enforce ledger separation invariant: E-faktura cannot be posted as cash
        ReconciliationEngine.enforce_ledger_separation(
            doc_type=batch_state.document_type,
            attempt_to_modify_cash=False  # Normal posting follows document nature
        )

        # Select valid rows to commit
        valid_rows: List[NormalizedRowData] = []
        skipped_count = 0

        for r in batch_state.parsed_rows:
            if r.validation_status == RowValidationStatus.ERROR:
                skipped_count += 1
                continue
            if r.is_duplicate and not request.ignore_duplicates:
                skipped_count += 1
                continue
            if r.normalized:
                valid_rows.append(r.normalized)

        if not valid_rows:
            raise ImportEngineError("Tasdiqlash uchun yaroqli tranzaksiyalar mavjud emas (barcha qatorlarda xatolik yoki takrorlanish).")

        # Post to respective ledger
        updated_cash_balance: Optional[Decimal] = None
        updated_dscr: Optional[Decimal] = None

        if batch_state.document_type == DocumentTypeEnum.E_FAKTURA:
            committed_count = ReconciliationEngine.post_invoice_batch(
                org_id=request.organization_id,
                batch_id=batch_state.batch_id,
                rows=valid_rows
            )
            # Try reconciling with existing bank payments
            ReconciliationEngine.match_invoices_with_cash(request.organization_id)
            message = (
                f"Soliq E-Faktura muvaffaqiyatli import qilindi: {committed_count} ta invoys "
                "Invoys majburiyatlari reestriga (AR/AP Ledger) kiritildi. Naqd pul qoldig'i o'zgarmadi."
            )
        else:
            # BANK_STATEMENT
            committed_count = ReconciliationEngine.post_cash_batch(
                org_id=request.organization_id,
                batch_id=batch_state.batch_id,
                rows=valid_rows
            )
            # Register transaction fingerprints
            for r in batch_state.parsed_rows:
                if r.fingerprint and r.normalized in valid_rows:
                    DuplicateDetector.register_transaction_fingerprint(request.organization_id, r.fingerprint)

            # Reconcile with open invoices if any
            ReconciliationEngine.match_invoices_with_cash(request.organization_id)

            # Recalculate cash metrics and DSCR using Financial Engine
            ledgers = ReconciliationEngine.get_ledgers(request.organization_id)
            updated_cash_balance = ledgers["net_cash_flow"]

            total_inflows = sum((r.amount for r in valid_rows if r.direction == TransactionDirection.INFLOW), Decimal("0.00"))
            total_outflows = sum((r.amount for r in valid_rows if r.direction == TransactionDirection.OUTFLOW), Decimal("0.00"))
            
            # Indicative annual DSCR computation for the organization
            debt_service_est = Decimal("10000000.00")  # Baseline annual debt service estimate
            dscr_req = DSCRCalculationRequest(
                operating_cash_inflows=total_inflows,
                operating_cash_outflows=total_outflows,
                debt_service_principal=debt_service_est * Decimal("0.70"),
                debt_service_interest=debt_service_est * Decimal("0.30")
            )
            dscr_res = calculate_dscr(dscr_req)
            updated_dscr = dscr_res.dscr

            message = (
                f"Bank aylanmasi muvaffaqiyatli import qilindi: {committed_count} ta bank tranzaksiyasi "
                f"Kassa/Bank reestriga yozildi. Yangilangan sof pul oqimi: {updated_cash_balance:,.2f} so'm."
            )

        # Register file hash so identical file cannot be uploaded again
        DuplicateDetector.register_file(request.organization_id, batch_state.file_hash)

        batch_state.status = ImportBatchStatus.COMMITTED
        batch_state.committed_at = datetime.now(timezone.utc)

        # Log to history
        hist_item = ImportHistoryItem(
            batch_id=batch_state.batch_id,
            file_name=batch_state.file_name,
            document_type=batch_state.document_type,
            status=ImportBatchStatus.COMMITTED,
            total_rows=len(batch_state.parsed_rows),
            committed_count=committed_count,
            total_inflow=sum((r.normalized.amount for r in batch_state.parsed_rows if r.normalized and r.normalized.direction == TransactionDirection.INFLOW), Decimal("0.00")),
            total_outflow=sum((r.normalized.amount for r in batch_state.parsed_rows if r.normalized and r.normalized.direction == TransactionDirection.OUTFLOW), Decimal("0.00")),
            created_at=batch_state.created_at,
            committed_at=batch_state.committed_at
        )
        if request.organization_id not in cls._HISTORY:
            cls._HISTORY[request.organization_id] = []
        cls._HISTORY[request.organization_id].insert(0, hist_item)

        return BatchCommitResponse(
            batch_id=batch_state.batch_id,
            status=ImportBatchStatus.COMMITTED,
            document_type=batch_state.document_type,
            target_ledger=target_ledger,
            committed_count=committed_count,
            skipped_count=skipped_count,
            updated_cash_balance=updated_cash_balance,
            updated_dscr=updated_dscr,
            message=message
        )

    @classmethod
    def get_batch_preview(cls, batch_id: str) -> ImportPreviewResponse:
        """Retrieves the current state and preview of a batch."""
        batch_state = cls._get_batch(batch_id)
        return cls._build_preview_response(batch_state)

    @classmethod
    def get_history(cls, org_id: str = "demo-org-agro-01") -> List[ImportHistoryItem]:
        """Returns import history for an organization."""
        return cls._HISTORY.get(org_id, [])

    # --- Internal Helpers ---

    @classmethod
    def _get_batch(cls, batch_id: str) -> ImportBatchState:
        batch = cls._BATCHES.get(batch_id)
        if not batch:
            raise ImportEngineError(f"Import partiyasi topilmadi: {batch_id}", code="BATCH_NOT_FOUND")
        return batch

    @classmethod
    def _process_rows_for_batch(cls, batch: ImportBatchState) -> None:
        """Parses, validates, classifies, and checks duplicates for all rows in a batch."""
        parsed_rows: List[ParsedRowSchema] = []
        normalized_list: List[NormalizedRowData] = []

        for idx, raw_row in enumerate(batch.raw_data.rows, start=1):
            row_id = f"{batch.batch_id}-row-{idx}"
            norm_data, val_status, msgs = TransactionValidator.validate_row(
                row_dict=raw_row,
                mappings=batch.mappings,
                document_type=batch.document_type,
                row_index=idx
            )

            classification = None
            if norm_data:
                classification = Classifier.classify(norm_data, batch.document_type)

            parsed_rows.append(
                ParsedRowSchema(
                    row_id=row_id,
                    row_index=idx,
                    raw_data=raw_row,
                    normalized=norm_data,
                    validation_status=val_status,
                    validation_messages=msgs,
                    classification=classification
                )
            )
            if norm_data:
                normalized_list.append(norm_data)

        # Check duplicates
        dup_results = DuplicateDetector.check_intra_batch_duplicates(batch.org_id, normalized_list)
        norm_idx = 0
        for r in parsed_rows:
            if r.normalized:
                fp, is_dup = dup_results[norm_idx]
                r.fingerprint = fp
                r.is_duplicate = is_dup
                if is_dup and r.validation_status == RowValidationStatus.VALID:
                    r.validation_status = RowValidationStatus.DUPLICATE
                    r.validation_messages.append("Takroriy tranzaksiya (avval ro'yxatga olingan yoki fayl ichida takrorlangan).")
                norm_idx += 1

        batch.parsed_rows = parsed_rows
        batch.status = ImportBatchStatus.VALIDATED

    @classmethod
    def _build_preview_response(cls, batch: ImportBatchState) -> ImportPreviewResponse:
        total_rows = len(batch.parsed_rows)
        valid_rows = sum(1 for r in batch.parsed_rows if r.validation_status == RowValidationStatus.VALID)
        warning_rows = sum(1 for r in batch.parsed_rows if r.validation_status == RowValidationStatus.WARNING)
        error_rows = sum(1 for r in batch.parsed_rows if r.validation_status == RowValidationStatus.ERROR)
        duplicate_rows = sum(1 for r in batch.parsed_rows if r.validation_status == RowValidationStatus.DUPLICATE)

        total_inflow = sum(
            (r.normalized.amount for r in batch.parsed_rows if r.normalized and r.normalized.direction == TransactionDirection.INFLOW),
            Decimal("0.00")
        )
        total_outflow = sum(
            (r.normalized.amount for r in batch.parsed_rows if r.normalized and r.normalized.direction == TransactionDirection.OUTFLOW),
            Decimal("0.00")
        )
        net_flow = total_inflow - total_outflow

        if batch.document_type == DocumentTypeEnum.E_FAKTURA:
            accounting_notice = (
                "DIQQAT: Soliq E-Faktura ma'lumotlari faqat debitorlik/kreditorlik majburiyatlari reestriga "
                "(Invoice Obligation Ledger) yoziladi. Ular bankdagi kassa qoldig'ini o'zgartirmaydi."
            )
        else:
            accounting_notice = (
                "MA'LUMOT: Bank aylanmasi ko'chirmasi to'g'ridan-to'g'ri Kassa va Real Pul Oqimlari reestriga "
                "(Cash Ledger) kiritiladi va joriy moliyaviy hisobotlar hamda DSCR ko'rsatkichini yangilaydi."
            )

        return ImportPreviewResponse(
            batch_id=batch.batch_id,
            file_name=batch.file_name,
            file_hash_sha256=batch.file_hash,
            document_type=batch.document_type,
            total_rows=total_rows,
            valid_rows=valid_rows,
            warning_rows=warning_rows,
            error_rows=error_rows,
            duplicate_rows=duplicate_rows,
            total_inflow=total_inflow,
            total_outflow=total_outflow,
            net_flow=net_flow,
            detected_mappings=batch.detected_mapping_items,
            rows=batch.parsed_rows[:100],  # Preview first 100 rows
            accounting_notice=accounting_notice
        )

    @classmethod
    def reset(cls) -> None:
        """Utility for test suite resets."""
        cls._BATCHES.clear()
        cls._HISTORY.clear()
        DuplicateDetector._FILE_HASH_REGISTRY.clear()
        DuplicateDetector._TRANSACTION_FINGERPRINTS.clear()
        ReconciliationEngine.reset()
