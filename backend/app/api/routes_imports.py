"""
AgroHisob CFO - Smart Data Import API Endpoints
Provides endpoints for uploading, previewing, mapping, validating, and committing
Soliq E-Faktura and Bank Statement financial data.
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.import_engine.exceptions import (
    ImportEngineError,
    FileValidationError,
    FileSizeLimitExceededError,
    UnsupportedFormatError,
    CorruptedFileError,
    DuplicateFileError,
    UnmappedColumnError,
    LedgerSeparationViolationError,
)
from app.import_engine.schemas import (
    BatchCommitRequest,
    BatchCommitResponse,
    DocumentTypeEnum,
    ImportHistoryItem,
    ImportPreviewResponse,
    ParsedRowSchema,
    RowOverride,
)
from app.import_engine.import_service import ImportService


router = APIRouter(prefix="/imports", tags=["Smart Financial Data Import"])


class CustomMappingRequest(BaseModel):
    mappings: Dict[str, str]  # target_field -> source_header


@router.post(
    "/upload",
    response_model=ImportPreviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload financial document (.csv / .xlsx)",
    description="Validates file format, parses tabular rows, autodetects column mappings, and generates preview."
)
async def upload_financial_document(
    file: UploadFile = File(...),
    document_type: DocumentTypeEnum = Form(...),
    organization_id: str = Form("demo-org-agro-01"),
):
    try:
        content = await file.read()
        preview = ImportService.upload_and_stage(
            file_name=file.filename or "unknown.csv",
            content=content,
            document_type=document_type,
            org_id=organization_id,
        )
        return preview

    except UnsupportedFormatError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except FileSizeLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=e.message)
    except DuplicateFileError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except (FileValidationError, CorruptedFileError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except ImportEngineError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Faylni yuklashda tizimli xatolik: {str(e)}")


@router.get(
    "/{batch_id}/preview",
    response_model=ImportPreviewResponse,
    summary="Get import batch preview",
    description="Retrieves parsed rows, detected mappings, validation summary, and financial totals for an uploaded batch."
)
def get_batch_preview(batch_id: str):
    try:
        return ImportService.get_batch_preview(batch_id)
    except ImportEngineError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post(
    "/{batch_id}/mapping",
    response_model=ImportPreviewResponse,
    summary="Update column mapping profile",
    description="Applies manual or custom column mapping adjustments and re-validates all rows."
)
def update_batch_mapping(batch_id: str, request: CustomMappingRequest):
    try:
        return ImportService.apply_custom_mapping(batch_id, request.mappings)
    except UnmappedColumnError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except ImportEngineError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.patch(
    "/{batch_id}/rows/{row_id}",
    response_model=ParsedRowSchema,
    summary="Override row values or classification",
    description="Permits manual user adjustment of category, amount, counterparty, or direction before final commit."
)
def override_batch_row(batch_id: str, row_id: str, override: RowOverride):
    try:
        return ImportService.override_row(batch_id, row_id, override)
    except ImportEngineError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post(
    "/{batch_id}/commit",
    response_model=BatchCommitResponse,
    summary="Commit validated batch into ledger",
    description="Posts records into the designated ledger (Bank -> Cash Ledger; E-Faktura -> Invoice Obligation Ledger) and updates financial metrics."
)
def commit_batch(batch_id: str, request: Optional[BatchCommitRequest] = None):
    try:
        req = request or BatchCommitRequest(batch_id=batch_id)
        # Ensure batch_id consistency
        req.batch_id = batch_id
        return ImportService.commit_batch(req)
    except LedgerSeparationViolationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except ImportEngineError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get(
    "/history/list",
    response_model=List[ImportHistoryItem],
    summary="List import history",
    description="Retrieves chronological audit log of all imported batches for an organization."
)
def get_import_history(organization_id: str = "demo-org-agro-01"):
    return ImportService.get_history(organization_id)
