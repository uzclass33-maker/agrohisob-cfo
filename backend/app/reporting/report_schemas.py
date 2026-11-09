"""
AgroHisob CFO - Report Data Schemas (Assignment 5)
Provides canonical, authoritative Pydantic models for Credit Profile,
Document Checklist, Financial Readiness Assessment, and Complete Credit Dossier.
"""

from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LoanPurposeEnum(str, Enum):
    WORKING_CAPITAL = "WORKING_CAPITAL"             # Aylanma mablag'larni to'ldirish
    AGRICULTURAL_INPUTS = "AGRICULTURAL_INPUTS"     # Urug'lik, o'g'it va yoqilg'i sotib olish
    MACHINERY_EQUIPMENT = "MACHINERY_EQUIPMENT"     # Qishloq xo'jaligi texnikasi va agregatlar
    DRIP_IRRIGATION = "DRIP_IRRIGATION"             # Tomchilatib sug'orish tizimi (PQ-47)
    COLD_STORAGE = "COLD_STORAGE"                   # Muzlatkichli omborxona qurish
    BUSINESS_EXPANSION = "BUSINESS_EXPANSION"       # Ekin maydonlari va faoliyatni kengaytirish
    OTHER = "OTHER"                                 # Boshqa agrar maqsadlar


class ChecklistItemStatus(str, Enum):
    AVAILABLE = "AVAILABLE"                         # Mavjud
    MISSING = "MISSING"                             # Yetishmaydi
    NEEDS_REVIEW = "NEEDS_REVIEW"                   # Qayta ko'rib chiqish talab etiladi
    NOT_APPLICABLE = "NOT_APPLICABLE"               # Qo'llanilmaydi


class ReadinessStatusEnum(str, Enum):
    READY_FOR_REVIEW = "READY_FOR_REVIEW"                   # Tahlil uchun tayyor (Inson tekshiruviga)
    ADDITIONAL_INFO_REQUIRED = "ADDITIONAL_INFO_REQUIRED"   # Qo'shimcha ma'lumot talab etiladi
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"                 # Ma'lumotlar yetarli emas


class CreditProfile(BaseModel):
    """Credit application configuration profile filled by applicant."""
    organization_id: str = "scenario-small-farmer"
    organization_name: str = "Andijon Baraka Fermer Xo'jaligi"
    organization_type: str = "FERMER_XOJALIGI"
    business_activity: str = "Paxtachilik va sabzavotchilik agrobiznesi"
    region: str = "Andijon viloyati"
    district: str = "Asaka tumani"
    inn: Optional[str] = "304819205"
    operating_years: int = Field(default=8, ge=0)
    reporting_currency: str = "UZS"
    land_hectares: float = Field(default=65.0, gt=0)
    main_crop_types: List[str] = Field(default_factory=lambda: ["Paxta", "Sabzavot"])
    harvest_months: List[int] = Field(default_factory=lambda: [6, 7, 9, 10, 11])
    sales_months: List[int] = Field(default_factory=lambda: [6, 7, 8, 9, 10, 11, 12])
    customer_segments: str = "Mahalliy bozor, agrosanoat klasteri va davlat buyurtmasi"
    
    # Financing Request
    requested_loan_amount_uzs: Decimal = Field(default=Decimal("150000000.00"), gt=0)
    loan_purpose: LoanPurposeEnum = LoanPurposeEnum.WORKING_CAPITAL
    proposed_term_months: int = Field(default=24, ge=1, le=120)
    proposed_annual_interest_rate_pct: Decimal = Field(default=Decimal("14.00"), ge=0, le=50)
    repayment_structure: str = Field(default="ANNUITY", description="ANNUITY or EQUAL_PRINCIPAL")
    grace_period_months: int = Field(default=3, ge=0, le=24)
    expected_disbursement_date: str = "2026-03-01"


class ChecklistItem(BaseModel):
    id: str
    category: str  # COMPANY_INFO, FINANCIAL_INFO, BUSINESS_INFO, AGRICULTURAL_INFO, FINANCING_INFO
    category_title_uz: str
    title_uz: str
    status: ChecklistItemStatus
    rationale_uz: str
    is_critical: bool = True


class DocumentReadinessChecklist(BaseModel):
    checklist_title_uz: str = "Kreditga Tayyorgarlik Hujjatlar Nazorat Ro'yxati"
    items: List[ChecklistItem]
    total_items: int
    available_count: int
    missing_count: int
    needs_review_count: int
    completeness_percentage: float
    disclaimer_uz: str = (
        "Mazkur ro'yxat dastlabki ma'lumotlar to'liqligini baholovchi indikativ vosita bo'lib, "
        "O'zbekiston tijorat banklarining yakuniy rasmiy talabnomasini o'rnini bosmaydi."
    )


class FinancialReadinessAssessment(BaseModel):
    overall_status: ReadinessStatusEnum
    status_label_uz: str
    readiness_score: int = Field(..., ge=0, le=100)
    data_completeness_pct: float
    cash_flow_stability_uz: str
    dscr_capacity_uz: str
    forecast_confidence_uz: str
    key_strengths_uz: List[str]
    identified_risks_uz: List[str]
    critical_limitations_uz: List[str]
    audit_disclaimer_uz: str


class CreditDossierData(BaseModel):
    """Canonical ReportData contract shared across UI preview, PDF and Excel generators."""
    dossier_id: str
    organization_id: str
    organization_name: str
    generation_timestamp: str
    calculation_version: str = "5.0.0"
    reporting_period: str = "2026"
    credit_profile: CreditProfile
    checklist: DocumentReadinessChecklist
    readiness_assessment: FinancialReadinessAssessment
    historical_summary: Dict[str, Any]
    forecast_summary: Dict[str, Any]
    debt_dscr_summary: Dict[str, Any]
    risks_scenarios_summary: Dict[str, Any]
    data_sources_and_assumptions: Dict[str, Any]
    collateral_readiness_summary: Optional[Dict[str, Any]] = None
    subsidy_opportunities_summary: Optional[Dict[str, Any]] = None
    regulatory_disclaimer_uz: str


class GeneratedReportRecord(BaseModel):
    report_id: str
    dossier_id: str
    organization_id: str
    report_title: str
    created_at: str
    status: str = "COMPLETED"  # DRAFT, VALIDATING, READY, GENERATING, COMPLETED, FAILED
    pdf_path: Optional[str] = None
    xlsx_path: Optional[str] = None
    pdf_url: Optional[str] = None
    xlsx_url: Optional[str] = None
    file_hash: Optional[str] = None
    file_size_bytes_pdf: Optional[int] = None
    file_size_bytes_xlsx: Optional[int] = None
    calculation_version: str = "5.0.0"
