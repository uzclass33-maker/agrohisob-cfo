"""
AgroHisob CFO - Smart Import Engine Data Schemas
Pydantic v2 schemas defining import structures, column mappings, validation, and commit pipelines.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DocumentTypeEnum(str, Enum):
    """Supported business financial document families in Uzbekistan."""
    E_FAKTURA = "E_FAKTURA"          # Soliq.uz Elektron Hisobvaraq-Faktura (Invoice / Commercial Obligations)
    BANK_STATEMENT = "BANK_STATEMENT"  # Bank hisobvaraq aylanmasi / ko'chirma (Actual Cash Movements)


class ImportBatchStatus(str, Enum):
    """State of an import batch lifecycle."""
    UPLOADED = "UPLOADED"
    PARSED = "PARSED"
    MAPPED = "MAPPED"
    VALIDATED = "VALIDATED"
    COMMITTED = "COMMITTED"
    REJECTED = "REJECTED"


class RowValidationStatus(str, Enum):
    """Integrity and validity status of an individual parsed row."""
    VALID = "VALID"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DUPLICATE = "DUPLICATE"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class TransactionDirection(str, Enum):
    """Financial movement direction."""
    INFLOW = "INFLOW"    # Kirim / Kredit / Pul tushumi
    OUTFLOW = "OUTFLOW"  # Chiqim / Debet / Pul to'lovi


class AgroFinancialCategory(str, Enum):
    """Standardized agronomic financial chart of categories."""
    CROP_SALES_GRAIN = "CROP_SALES_GRAIN"              # G'alla va don ekinlari sotuvi
    CROP_SALES_COTTON = "CROP_SALES_COTTON"            # Paxta xomashyosi sotuvi
    CROP_SALES_HORTICULTURE = "CROP_SALES_HORTICULTURE"# Meva, sabzavot, poliz ekinlari sotuvi
    FERTILIZER_CHEMICALS = "FERTILIZER_CHEMICALS"      # Mineral o'g'itlar va pestitsidlar
    FUEL_LUBRICANTS = "FUEL_LUBRICANTS"                # Yoqilg'i va moylash materiallari (GSM)
    SEEDS_SEEDLINGS = "SEEDS_SEEDLINGS"                # Urug'lik va ko'chatlar
    MACHINERY_SERVICES = "MACHINERY_SERVICES"          # Texnika xizmati, traktor va ehtiyot qismlar
    LABOR_PAYROLL = "LABOR_PAYROLL"                    # Ish haqi va mavsumiy ishchilar to'lovlari
    IRRIGATION_WATER = "IRRIGATION_WATER"              # Sug'orish suvi, nasos va melioratsiya
    LAND_LEASE = "LAND_LEASE"                          # Yer ijarasi va kadastr to'lovlari
    INSURANCE_AGRO = "INSURANCE_AGRO"                  # Hosil va agromulk sug'urtasi
    TAXES_DUTIES = "TAXES_DUTIES"                      # Yagona yer solig'i va majburiy to'lovlar
    DEBT_SERVICE = "DEBT_SERVICE"                      # Bank kredit foiz va asosiy qarz to'lovlari
    SUBSIDY_GRANTS = "SUBSIDY_GRANTS"                  # Davlat agrar subsidiyalari va grantlar
    OTHER_OPERATING_EXPENSES = "OTHER_OPERATING_EXPENSES" # Boshqa operatsion xarajatlar
    OTHER_OPERATING_INCOME = "OTHER_OPERATING_INCOME"     # Boshqa operatsion daromadlar
    UNCATEGORIZED_EXPENSE = "UNCATEGORIZED_EXPENSE"       # Noaniq xarajat (tekshirish talab)
    UNCATEGORIZED_INCOME = "UNCATEGORIZED_INCOME"         # Noaniq daromad (tekshirish talab)


class ClassificationResult(BaseModel):
    """Result produced by the classification engine for a single transaction."""
    category: AgroFinancialCategory
    category_name_uz: str
    confidence: float = Field(ge=0.0, le=1.0)
    rule_source: str  # e.g., "MXIK_DICTIONARY", "KEYWORD_HEURISTIC", "COUNTERPARTY_RULE", "DEFAULT_FALLBACK"
    applied_rule: Optional[str] = None


class NormalizedRowData(BaseModel):
    """Clean, type-safe representation of a single financial record."""
    transaction_date: date
    amount: Decimal = Field(gt=0, decimal_places=2)
    direction: TransactionDirection
    counterparty_name: str
    counterparty_inn: Optional[str] = None
    document_number: Optional[str] = None
    purpose: Optional[str] = None
    mxik_code: Optional[str] = None
    vat_amount: Optional[Decimal] = Field(default=Decimal("0.00"), decimal_places=2)
    vat_rate: Optional[Decimal] = Field(default=Decimal("0.00"), decimal_places=2)
    bank_account: Optional[str] = None


class ParsedRowSchema(BaseModel):
    """Wrapper holding raw row data, normalized data, validation outcome, and classification."""
    row_id: str
    row_index: int
    raw_data: Dict[str, Any]
    normalized: Optional[NormalizedRowData] = None
    validation_status: RowValidationStatus = RowValidationStatus.VALID
    validation_messages: List[str] = Field(default_factory=list)
    classification: Optional[ClassificationResult] = None
    fingerprint: Optional[str] = None
    is_duplicate: bool = False


class ColumnMappingItem(BaseModel):
    """Mapping descriptor between source header and system target field."""
    source_header: str
    target_field: str
    confidence: float = Field(ge=0.0, le=1.0)
    sample_values: List[str] = Field(default_factory=list)


class MappingProfileSchema(BaseModel):
    """Mapping request or auto-detected mappings for a batch."""
    document_type: DocumentTypeEnum
    mappings: Dict[str, str]  # target_field -> source_header


class RowOverride(BaseModel):
    """Manual adjustment provided by user for a specific row before committing."""
    row_id: str
    category: Optional[AgroFinancialCategory] = None
    direction: Optional[TransactionDirection] = None
    amount: Optional[Decimal] = None
    counterparty_name: Optional[str] = None
    purpose: Optional[str] = None


class ImportPreviewResponse(BaseModel):
    """Complete summary and paginated row preview presented to user before confirmation."""
    batch_id: str
    file_name: str
    file_hash_sha256: str
    document_type: DocumentTypeEnum
    total_rows: int
    valid_rows: int
    warning_rows: int
    error_rows: int
    duplicate_rows: int
    total_inflow: Decimal
    total_outflow: Decimal
    net_flow: Decimal
    detected_mappings: List[ColumnMappingItem]
    rows: List[ParsedRowSchema]
    accounting_notice: str


class BatchCommitRequest(BaseModel):
    """Request to finalize import and post data to the respective ledger."""
    batch_id: str
    organization_id: str = "demo-org-agro-01"
    overrides: List[RowOverride] = Field(default_factory=list)
    ignore_duplicates: bool = False


class BatchCommitResponse(BaseModel):
    """Result of committing an import batch."""
    batch_id: str
    status: ImportBatchStatus
    document_type: DocumentTypeEnum
    target_ledger: str  # "CASH_TRANSACTION_LEDGER" or "INVOICE_OBLIGATION_LEDGER"
    committed_count: int
    skipped_count: int
    updated_cash_balance: Optional[Decimal] = None
    updated_dscr: Optional[Decimal] = None
    message: str


class ImportHistoryItem(BaseModel):
    """Historical audit entry for an import run."""
    batch_id: str
    file_name: str
    document_type: DocumentTypeEnum
    status: ImportBatchStatus
    total_rows: int
    committed_count: int
    total_inflow: Decimal
    total_outflow: Decimal
    created_at: datetime
    committed_at: Optional[datetime] = None
