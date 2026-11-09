"""
AgroHisob CFO - Credit Dossier & Bank Reporting Router (Assignment 5)
Provides versioned REST endpoints for credit profile validation, document readiness checklist,
live canonical dossier preview, synchronous/background report generation, and secure downloads.
"""

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request, Response, status
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from app.reporting.credit_profile import (
    get_default_credit_profile,
    validate_credit_profile,
)
from app.reporting.dossier_builder import DossierBuilder
from app.reporting.excel_generator import ExcelModelGenerator
from app.reporting.pdf_generator import PDFReportGenerator
from app.reporting.readiness_assessment import build_document_readiness_checklist
from app.reporting.report_repository import ReportRepository
from app.reporting.report_schemas import (
    CreditDossierData,
    CreditProfile,
    DocumentReadinessChecklist,
    GeneratedReportRecord,
)

router = APIRouter(prefix="/reports", tags=["Credit Dossier & Bank Reporting"])


class ProfileValidationResponse(BaseModel):
    is_valid: bool
    errors: List[str]
    credit_profile: CreditProfile


class GenerateReportRequest(BaseModel):
    organization_id: Optional[str] = "scenario-small-farmer"
    fiscal_year: int = 2026
    credit_profile: Optional[CreditProfile] = None


def _resolve_profile_and_org(
    org_id_query: Optional[str],
    body_data: Optional[Dict[str, Any]]
) -> tuple[str, CreditProfile, int]:
    """Resolves organization_id, CreditProfile, and fiscal_year from various request shapes."""
    body_data = body_data or {}
    fiscal_year = int(body_data.get("fiscal_year", 2026))

    # Case 1: Wrapped inside credit_profile key
    if "credit_profile" in body_data and isinstance(body_data["credit_profile"], dict):
        profile = CreditProfile(**body_data["credit_profile"])
        org_id = profile.organization_id or org_id_query or "scenario-small-farmer"
        return org_id, profile, fiscal_year

    # Case 2: Raw CreditProfile passed at root (contains requested_loan_amount_uzs)
    if "requested_loan_amount_uzs" in body_data:
        profile = CreditProfile(**body_data)
        org_id = profile.organization_id or org_id_query or "scenario-small-farmer"
        return org_id, profile, fiscal_year

    # Case 3: Only organization_id passed
    org_id = body_data.get("organization_id") or org_id_query or "scenario-small-farmer"
    profile = get_default_credit_profile(org_id)
    return org_id, profile, fiscal_year


@router.post("/credit/profile", response_model=ProfileValidationResponse)
def validate_credit_profile_endpoint(profile: CreditProfile):
    """
    Validates a credit application profile and ensures logical bounds.
    """
    is_valid, errors = validate_credit_profile(profile)
    return ProfileValidationResponse(
        is_valid=is_valid,
        errors=errors,
        credit_profile=profile
    )


@router.post("/credit/validate", response_model=DocumentReadinessChecklist)
def validate_document_readiness_endpoint(
    request_data: Optional[Dict[str, Any]] = None,
    organization_id: Optional[str] = Query(None)
):
    """
    Returns the comprehensive 5-domain document readiness checklist and completeness score.
    """
    org_id, _, _ = _resolve_profile_and_org(organization_id, request_data)
    from app.import_engine.reconciliation import ReconciliationEngine
    ledger_data = ReconciliationEngine.get_ledgers(org_id)
    is_imported = ledger_data["cash_transaction_count"] > 0
    return build_document_readiness_checklist(org_id, is_imported=is_imported)


@router.post("/credit/preview", response_model=CreditDossierData)
def preview_credit_dossier_endpoint(
    request_data: Optional[Dict[str, Any]] = None,
    organization_id: Optional[str] = Query(None)
):
    """
    Constructs and returns canonical CreditDossierData for live UI preview.
    Ensures 100% financial consistency across UI, PDF, and Excel representations.
    """
    org_id, profile, fiscal_year = _resolve_profile_and_org(organization_id, request_data)
    dossier = DossierBuilder.build_dossier(
        organization_id=org_id,
        custom_profile=profile,
        fiscal_year=fiscal_year
    )
    return dossier


@router.post("/credit/generate", response_model=GeneratedReportRecord)
def generate_credit_dossier_files_endpoint(
    request_data: Optional[Dict[str, Any]] = None,
    organization_id: Optional[str] = Query(None)
):
    """
    Builds canonical CreditDossierData and generates both PDF and Excel model files on disk.
    Registers the report in repository with SHA-256 hash and download endpoints.
    """
    org_id, profile, fiscal_year = _resolve_profile_and_org(organization_id, request_data)
    dossier = DossierBuilder.build_dossier(
        organization_id=org_id,
        custom_profile=profile,
        fiscal_year=fiscal_year
    )

    report_id = f"rep-{uuid.uuid4().hex[:12]}"
    storage_dir = ReportRepository.get_storage_dir()

    pdf_filename = f"{report_id}_{org_id}_dossier.pdf"
    xlsx_filename = f"{report_id}_{org_id}_model.xlsx"
    pdf_path = storage_dir / pdf_filename
    xlsx_path = storage_dir / xlsx_filename

    # 1. Generate PDF
    pdf_bytes = PDFReportGenerator.generate_dossier_pdf(dossier, output_path=str(pdf_path))
    pdf_size = len(pdf_bytes)

    # 2. Generate Excel
    xlsx_bytes = ExcelModelGenerator.generate_dossier_xlsx(dossier, output_path=str(xlsx_path))
    xlsx_size = len(xlsx_bytes)

    # 3. Compute combined SHA-256 hash of PDF
    pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

    now_iso = datetime.now(timezone.utc).isoformat()
    record = GeneratedReportRecord(
        report_id=report_id,
        dossier_id=dossier.dossier_id,
        organization_id=org_id,
        report_title=f"{profile.organization_name} — Kreditga Tayyorgarlik Dosyesi va Moliyaviy Modeli",
        created_at=now_iso,
        status="COMPLETED",
        pdf_path=str(pdf_path),
        xlsx_path=str(xlsx_path),
        pdf_url=f"/api/v1/reports/{report_id}/download/pdf",
        xlsx_url=f"/api/v1/reports/{report_id}/download/xlsx",
        file_hash=pdf_hash,
        file_size_bytes_pdf=pdf_size,
        file_size_bytes_xlsx=xlsx_size,
        calculation_version="5.0.0"
    )

    ReportRepository.save_report_record(record)
    return record


@router.get("/history", response_model=List[GeneratedReportRecord])
def list_report_history_endpoint(
    organization_id: Optional[str] = Query(None)
):
    """
    Retrieves previous generated reports for an organization or all organizations.
    """
    return ReportRepository.list_reports(organization_id=organization_id)


@router.get("/{report_id}", response_model=GeneratedReportRecord)
def get_report_metadata_endpoint(report_id: str):
    """
    Returns metadata for a specific generated report.
    """
    record = ReportRepository.get_report_record(report_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hisobot topilmadi: {report_id}"
        )
    return record


@router.get("/{report_id}/download/pdf")
def download_pdf_report_endpoint(report_id: str):
    """
    Downloads the high-grade PDF credit dossier.
    """
    record = ReportRepository.get_report_record(report_id)
    if not record or not record.pdf_path or not os.path.exists(record.pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PDF hisobot fayli topilmadi: {report_id}"
        )

    safe_title = record.organization_id.replace(" ", "_")
    filename = f"AgroHisob_Dossier_{safe_title}_{report_id[:8]}.pdf"
    return FileResponse(
        path=record.pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/{report_id}/download/xlsx")
def download_xlsx_model_endpoint(report_id: str):
    """
    Downloads the structured 8-sheet Excel financial model workbook.
    """
    record = ReportRepository.get_report_record(report_id)
    if not record or not record.xlsx_path or not os.path.exists(record.xlsx_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Excel moliyaviy model fayli topilmadi: {report_id}"
        )

    safe_title = record.organization_id.replace(" ", "_")
    filename = f"AgroHisob_Financial_Model_{safe_title}_{report_id[:8]}.xlsx"
    return FileResponse(
        path=record.xlsx_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
