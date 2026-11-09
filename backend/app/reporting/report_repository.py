"""
AgroHisob CFO - Report Repository (Assignment 5)
Provides persistence and metadata retrieval for generated Credit Dossier reports (PDF and XLSX).
Stores artifacts in backend/storage/reports/ with filesystem synchronization.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import uuid

from app.reporting.report_schemas import GeneratedReportRecord

STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "reports"
METADATA_FILE = STORAGE_DIR / "reports_index.json"

# In-memory registry cached from disk
_report_cache: Dict[str, GeneratedReportRecord] = {}
_initialized: bool = False


def _ensure_storage_dir():
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _load_metadata():
    global _initialized, _report_cache
    _ensure_storage_dir()
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                _report_cache = {
                    item["report_id"]: GeneratedReportRecord(**item)
                    for item in data
                }
        except Exception:
            _report_cache = {}
    _initialized = True


def _save_metadata():
    _ensure_storage_dir()
    data = [record.model_dump() for record in _report_cache.values()]
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class ReportRepository:
    """Manages report file storage and metadata registry."""

    @classmethod
    def get_storage_dir(cls) -> Path:
        _ensure_storage_dir()
        return STORAGE_DIR

    @classmethod
    def save_report_record(cls, record: GeneratedReportRecord) -> GeneratedReportRecord:
        if not _initialized:
            _load_metadata()
        _report_cache[record.report_id] = record
        _save_metadata()
        return record

    @classmethod
    def get_report_record(cls, report_id: str) -> Optional[GeneratedReportRecord]:
        if not _initialized:
            _load_metadata()
        return _report_cache.get(report_id)

    @classmethod
    def list_reports(cls, organization_id: Optional[str] = None) -> List[GeneratedReportRecord]:
        if not _initialized:
            _load_metadata()
        records = list(_report_cache.values())
        if organization_id:
            records = [r for r in records if r.organization_id == organization_id]
        # Sort descending by created_at
        records.sort(key=lambda x: x.created_at, reverse=True)
        return records

    @classmethod
    def delete_report(cls, report_id: str) -> bool:
        if not _initialized:
            _load_metadata()
        record = _report_cache.pop(report_id, None)
        if record:
            if record.pdf_path and os.path.exists(record.pdf_path):
                try:
                    os.remove(record.pdf_path)
                except OSError:
                    pass
            if record.xlsx_path and os.path.exists(record.xlsx_path):
                try:
                    os.remove(record.xlsx_path)
                except OSError:
                    pass
            _save_metadata()
            return True
        return False
