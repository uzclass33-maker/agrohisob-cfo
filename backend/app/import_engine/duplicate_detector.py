"""
AgroHisob CFO - Duplicate Detector
Provides two-tier duplicate prevention: file-level SHA-256 cryptographic tracking and
transaction-level canonical fingerprinting to prevent accidental double-entry of accounting records.
"""

import hashlib
from decimal import Decimal
from typing import Dict, List, Optional, Set, Tuple
from app.import_engine.schemas import NormalizedRowData, RowValidationStatus
from app.import_engine.exceptions import DuplicateFileError


class DuplicateDetector:
    """Manages duplicate detection across files and individual transactions."""

    # In-memory registry of imported file hashes per organization (can also query DB)
    _FILE_HASH_REGISTRY: Dict[str, Set[str]] = {}
    _TRANSACTION_FINGERPRINTS: Dict[str, Set[str]] = {}

    @classmethod
    def register_file(cls, org_id: str, file_hash: str) -> None:
        """Stores file hash in registry."""
        if org_id not in cls._FILE_HASH_REGISTRY:
            cls._FILE_HASH_REGISTRY[org_id] = set()
        cls._FILE_HASH_REGISTRY[org_id].add(file_hash)

    @classmethod
    def is_file_duplicate(cls, org_id: str, file_hash: str) -> bool:
        """Checks if file hash already exists for this organization."""
        return org_id in cls._FILE_HASH_REGISTRY and file_hash in cls._FILE_HASH_REGISTRY[org_id]

    @classmethod
    def generate_row_fingerprint(cls, org_id: str, row: NormalizedRowData) -> str:
        """
        Creates canonical SHA-256 fingerprint for a financial transaction:
        Hash = SHA256(org_id + date + amount + direction + cp_identifier + doc_number)
        """
        cp_identifier = (row.counterparty_inn or row.counterparty_name).strip().lower()
        doc_num = (row.document_number or "").strip().lower()
        amount_str = f"{row.amount:.2f}"
        direction_str = row.direction.value

        raw_key = f"{org_id}|{row.transaction_date.isoformat()}|{amount_str}|{direction_str}|{cp_identifier}|{doc_num}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @classmethod
    def register_transaction_fingerprint(cls, org_id: str, fingerprint: str) -> None:
        """Saves committed transaction fingerprint."""
        if org_id not in cls._TRANSACTION_FINGERPRINTS:
            cls._TRANSACTION_FINGERPRINTS[org_id] = set()
        cls._TRANSACTION_FINGERPRINTS[org_id].add(fingerprint)

    @classmethod
    def check_intra_batch_duplicates(
        cls, 
        org_id: str, 
        rows: List[NormalizedRowData]
    ) -> List[Tuple[str, bool]]:
        """
        Checks for duplicate transactions within a single batch as well as historical records.
        Returns list of (fingerprint, is_duplicate).
        """
        results = []
        seen_in_batch = set()
        existing_history = cls._TRANSACTION_FINGERPRINTS.get(org_id, set())

        for row in rows:
            fp = cls.generate_row_fingerprint(org_id, row)
            is_dup = (fp in seen_in_batch) or (fp in existing_history)
            seen_in_batch.add(fp)
            results.append((fp, is_dup))

        return results

    @classmethod
    def clear_cache_for_org(cls, org_id: str) -> None:
        """Utility for test resets."""
        cls._FILE_HASH_REGISTRY.pop(org_id, None)
        cls._TRANSACTION_FINGERPRINTS.pop(org_id, None)
