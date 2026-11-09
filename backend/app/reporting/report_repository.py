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
    
    # 1. First attempt to load from durable database model
    loaded_from_db = False
    try:
        from app.db.database import SessionLocal
        from app.models.core import ReportFileRecordModel
        session = SessionLocal()
        try:
            db_records = session.query(ReportFileRecordModel).all()
            if db_records:
                _report_cache = {
                    r.report_id: GeneratedReportRecord(
                        report_id=r.report_id,
                        dossier_id=r.dossier_id or "",
                        organization_id=r.organization_id,
                        report_title=r.report_title,
                        created_at=r.created_at.isoformat() if r.created_at else "",
                        status=r.status or "COMPLETED",
                        pdf_path=r.pdf_path or "",
                        xlsx_path=r.xlsx_path or "",
                        pdf_url=r.pdf_url or "",
                        xlsx_url=r.xlsx_url or "",
                        file_hash=r.file_hash or "",
                        file_size_bytes_pdf=r.file_size_bytes_pdf or 0,
                        file_size_bytes_xlsx=r.file_size_bytes_xlsx or 0,
                        calculation_version=r.calculation_version or "5.0.0"
                    )
                    for r in db_records
                }
                loaded_from_db = True
        finally:
            session.close()
    except Exception:
        loaded_from_db = False

    # 2. If DB was empty or failed, load from JSON disk cache and sync to DB
    if not loaded_from_db and METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                _report_cache = {
                    item["report_id"]: GeneratedReportRecord(**item)
                    for item in data
                }
            # Sync loaded records into DB
            for item in _report_cache.values():
                _sync_to_db(item)
        except Exception:
            _report_cache = {}
    _initialized = True


def _sync_to_db(record: GeneratedReportRecord):
    """Synchronizes report record with durable database model."""
    try:
        from app.db.database import SessionLocal
        from app.models.core import ReportFileRecordModel
        session = SessionLocal()
        try:
            db_rec = session.query(ReportFileRecordModel).filter(
                ReportFileRecordModel.report_id == record.report_id
            ).first()
            if not db_rec:
                db_rec = ReportFileRecordModel(
                    report_id=record.report_id,
                    dossier_id=record.dossier_id,
                    organization_id=record.organization_id,
                    report_title=record.report_title,
                    status=record.status,
                    pdf_path=record.pdf_path,
                    xlsx_path=record.xlsx_path,
                    pdf_url=record.pdf_url,
                    xlsx_url=record.xlsx_url,
                    file_hash=record.file_hash,
                    file_size_bytes_pdf=record.file_size_bytes_pdf,
                    file_size_bytes_xlsx=record.file_size_bytes_xlsx,
                    calculation_version=record.calculation_version,
                )
                session.add(db_rec)
            else:
                db_rec.report_title = record.report_title
                db_rec.status = record.status
                db_rec.pdf_path = record.pdf_path
                db_rec.xlsx_path = record.xlsx_path
                db_rec.file_hash = record.file_hash
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
    except Exception:
        pass


def _delete_from_db(report_id: str):
    """Deletes report record from durable database model."""
    try:
        from app.db.database import SessionLocal
        from app.models.core import ReportFileRecordModel
        session = SessionLocal()
        try:
            db_rec = session.query(ReportFileRecordModel).filter(
                ReportFileRecordModel.report_id == report_id
            ).first()
            if db_rec:
                session.delete(db_rec)
                session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
    except Exception:
        pass


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
        _sync_to_db(record)
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
            _delete_from_db(report_id)
            return True
        return False
