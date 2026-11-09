"""
AgroHisob CFO - Collateral Intelligence Schemas (Assignment 6, Module A)
Pydantic contracts for land lease profile, VMQ-613 legal screening,
indicative DCF valuation, sensitivity analysis, and document checklist.
"""

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class VMQ613ScreeningStatusEnum(str, Enum):
    PRELIMINARY_CONDITIONS_MET = "PRELIMINARY_CONDITIONS_MET"             # Dastlabki shartlar bajarilgan
    ADDITIONAL_VERIFICATION_REQUIRED = "ADDITIONAL_VERIFICATION_REQUIRED" # Qo'shimcha tekshiruv talab etiladi
    APPARENT_RESTRICTION_IDENTIFIED = "APPARENT_RESTRICTION_IDENTIFIED"   # Qonuniy cheklov yoki taqiq aniqlangan
    INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION"                 # Ma'lumotlar yetarli emas


class ChecklistItemStatusEnum(str, Enum):
    AVAILABLE = "AVAILABLE"
    MISSING = "MISSING"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class LandLeaseProfile(BaseModel):
    """Agricultural land lease right proposed as credit collateral."""
    organization_id: str = "scenario-small-farmer"
    organization_name: str = "Andijon Baraka Fermer Xo'jaligi"
    land_reference: str = "17:03:04:02:01:0429"  # Cadastral or field identifier
    region: str = "Andijon viloyati"
    district: str = "Asaka tumani"
    area_hectares: float = Field(default=65.0, gt=0)
    land_category: str = "Sug'oriladigan qishloq xo'jaligi yeri"
    
    # Dates
    lease_start_date: date = date(2021, 3, 1)
    lease_expiration_date: date = date(2051, 3, 1)  # 30-year lease
    proposed_loan_maturity_date: date = date(2028, 3, 1)  # 2-year loan
    proposed_loan_amount_uzs: Decimal = Field(default=Decimal("150000000.00"), gt=0)
    
    # Legal Status
    is_registered_in_cadastre: bool = True
    registration_number: Optional[str] = "REG-AND-2021-0842"
    has_legal_restrictions: bool = False  # e.g. arrest, pledge, dispute
    is_disputed: bool = False
    is_terminated: bool = False
    is_secondary_lease: bool = False  # sub-lease
    has_sublease_authority_permission: bool = False
    
    # Agricultural & Valuation Attributes
    soil_bonitet_score: int = Field(default=68, ge=10, le=100)
    main_crop_type: str = "Paxta va sabzavot"
    normative_annual_net_benefit_per_ha_uzs: Decimal = Field(default=Decimal("8500000.00"), ge=0)
    discount_rate_pct: Decimal = Field(default=Decimal("16.00"), ge=1, le=50)
    target_ltv_pct: Decimal = Field(default=Decimal("65.00"), ge=10, le=90)
    has_independent_appraisal: bool = False
    independent_appraisal_value_uzs: Optional[Decimal] = None


class VMQ613RuleCheckItem(BaseModel):
    rule_id: str
    rule_name_uz: str
    statutory_basis: str
    status: str
    status_label_uz: str
    explanation_uz: str
    action_required_uz: Optional[str] = None


class VMQ613ScreeningResult(BaseModel):
    """Detailed explainable legal screening result under VMQ-613."""
    overall_status: VMQ613ScreeningStatusEnum
    status_label_uz: str
    screening_date: str
    
    # Lease duration verification (5-year post-maturity buffer rule)
    lease_duration_valid: bool
    remaining_lease_days_after_maturity: int
    remaining_lease_years_after_maturity: float
    required_buffer_years: int = 5
    is_5_year_buffer_satisfied: bool
    
    # Legal status checks
    registration_valid: bool
    restrictions_clear: bool
    dispute_clear: bool
    secondary_lease_compliant: bool
    
    # Explainable findings
    key_findings_uz: List[str] = Field(default_factory=list)
    missing_evidence_uz: List[str] = Field(default_factory=list)
    human_verification_requirements_uz: List[str] = Field(default_factory=list)
    
    # Harmonized convenient fields
    is_eligible: bool = False
    overall_legal_status_uz: str = ""
    post_maturity_buffer_years: float = 0.0
    remaining_lease_years: float = 0.0
    defects: List[str] = Field(default_factory=list)
    remediation_steps: List[str] = Field(default_factory=list)
    rule_checks: List[VMQ613RuleCheckItem] = Field(default_factory=list)
    statutory_disclaimer_uz: str = ""

    # Legal provenance
    legal_source_code: str = "VMQ-613"
    legal_source_url: str = "https://lex.uz/uz/docs/-7750301"
    applied_rule_clauses: List[str] = Field(default_factory=lambda: ["5-band", "8-band", "12-band", "14-band", "15-band"])


class IndicativeValuationRequest(BaseModel):
    area_hectares: float = Field(..., gt=0)
    soil_bonitet_score: int = Field(default=65, ge=10, le=100)
    remaining_lease_years: int = Field(default=25, ge=1, le=50)
    normative_annual_net_benefit_per_ha_uzs: Decimal = Field(default=Decimal("8500000.00"), gt=0)
    discount_rate_pct: Decimal = Field(default=Decimal("16.00"), ge=1, le=50)
    annual_benefit_growth_pct: Decimal = Field(default=Decimal("2.00"), ge=-20, le=30)
    target_ltv_pct: Decimal = Field(default=Decimal("65.00"), ge=10, le=90)


class DCFCashFlowPeriod(BaseModel):
    year: int
    nominal_cash_flow_uzs: Decimal
    discount_factor: float
    discounted_cash_flow_uzs: Decimal
    cumulative_pv_uzs: Decimal


class IndicativeValuationResult(BaseModel):
    """
    Transparent, non-certified indicative valuation of agricultural land lease right.
    Calculates present value of attributable net economic benefit over the lease horizon.
    """
    indicative_present_value_uzs: Decimal
    annual_attributable_net_benefit_uzs: Decimal
    adjusted_benefit_per_ha_uzs: Decimal
    bonitet_adjustment_factor: float
    discount_rate_pct: Decimal
    analysis_horizon_years: int
    annuity_factor: float
    target_ltv_pct: Decimal
    indicative_secured_amount_uzs: Decimal
    methodology_uz: str
    statutory_disclaimer_uz: str

    # Harmonized aliases
    indicative_market_value_uzs: Optional[Decimal] = None
    max_pledge_value_uzs: Optional[Decimal] = None
    valuation_horizon_years: Optional[int] = None
    adjusted_annual_net_benefit_per_ha_uzs: Optional[Decimal] = None
    cash_flow_schedule: List[DCFCashFlowPeriod] = Field(default_factory=list)


class ValuationSensitivityCase(BaseModel):
    scenario_name_uz: str
    discount_rate_pct: Decimal
    benefit_growth_pct: Decimal
    annual_attributable_benefit_uzs: Decimal
    indicative_present_value_uzs: Decimal
    indicative_secured_amount_uzs: Decimal
    variance_from_base_pct: float

    # Harmonized aliases
    indicative_valuation_uzs: Optional[Decimal] = None
    max_pledge_value_uzs: Optional[Decimal] = None
    scenario_label_uz: Optional[str] = None
    description_uz: Optional[str] = None
    variance_pct: Optional[float] = None


class CollateralSensitivityAnalysis(BaseModel):
    base_case: ValuationSensitivityCase
    optimistic_case: ValuationSensitivityCase
    pessimistic_case: ValuationSensitivityCase
    analysis_summary_uz: str

    # Harmonized aliases
    base_scenario: Optional[ValuationSensitivityCase] = None
    optimistic_scenario: Optional[ValuationSensitivityCase] = None
    pessimistic_scenario: Optional[ValuationSensitivityCase] = None
    volatility_range_uzs: Optional[Decimal] = None
    key_risk_drivers_uz: List[str] = Field(default_factory=list)


class CollateralChecklistItem(BaseModel):
    id: str
    title_uz: str
    category_uz: str
    status: ChecklistItemStatusEnum
    is_statutory: bool  # True if mandated by VMQ-613
    legal_source: str
    rationale_uz: str

    # Harmonized aliases
    code: Optional[str] = None
    document_name_uz: Optional[str] = None
    issuing_body_uz: Optional[str] = None
    status_label_uz: Optional[str] = None
    is_mandatory: Optional[bool] = None
    statutory_reference: Optional[str] = None
    description_uz: Optional[str] = None


class CollateralDocumentChecklist(BaseModel):
    items: List[CollateralChecklistItem]
    total_count: int
    available_count: int
    missing_count: int
    needs_verification_count: int
    completeness_pct: float
    checklist_disclaimer_uz: str

    # Harmonized aliases
    total_documents: Optional[int] = None
    readiness_percentage: Optional[float] = None
    readiness_verdict_uz: Optional[str] = None


class CollateralPreparationSummary(BaseModel):
    summary_id: str
    organization_id: str
    organization_name: str
    generation_date: str
    profile: LandLeaseProfile
    screening: VMQ613ScreeningResult
    valuation: IndicativeValuationResult
    sensitivity: CollateralSensitivityAnalysis
    checklist: CollateralDocumentChecklist
    regulatory_disclaimer_uz: str
