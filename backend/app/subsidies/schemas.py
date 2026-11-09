"""
AgroHisob CFO - Agricultural Subsidy Intelligence Schemas (Assignment 6, Module B)
Pydantic contracts for subsidy programs, PQ-47 water-saving calculator,
PF-82 cotton & wheat interest compensation, eligibility matching, and financial impact.
"""

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SubsidyEligibilityStatusEnum(str, Enum):
    POTENTIALLY_ELIGIBLE = "POTENTIALLY_ELIGIBLE"                             # Dastlabki mezonlarga mos
    NOT_ELIGIBLE_UNDER_VERIFIED_RULE = "NOT_ELIGIBLE_UNDER_VERIFIED_RULE"     # Qoidaga asosan to'g'ri kelmaydi
    MORE_INFORMATION_REQUIRED = "MORE_INFORMATION_REQUIRED"                   # Qo'shimcha ma'lumot talab etiladi
    RULE_NOT_VERIFIED = "RULE_NOT_VERIFIED"                                   # Huquqiy qoida verifikatsiya qilinmagan
    OUTSIDE_EFFECTIVE_PERIOD = "OUTSIDE_EFFECTIVE_PERIOD"                     # Amal qilish muddatidan tashqarida


class SubsidyProgram(BaseModel):
    id: str
    program_code: str                     # e.g. "PQ47-DRIP-COTTON", "PQ47-DRIP-ORCHARD", "PF82-COTTON-INTEREST"
    program_name_uz: str
    managing_authority_uz: str
    legal_source_code: str                # e.g. "PQ-47", "PF-82"
    legal_source_url: str
    legal_clause: str
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool = True
    verification_status: str = "VERIFIED_ACTIVE"
    supported_crops: List[str] = Field(default_factory=list)
    supported_technologies: List[str] = Field(default_factory=list)
    eligible_regions: List[str] = Field(default_factory=list)  # Empty means all regions eligible
    base_rate_uzs_per_ha: Optional[Decimal] = None
    rate_description_uz: str
    interest_compensation_pct_points: Optional[Decimal] = None
    required_documents_uz: List[str] = Field(default_factory=list)


class PQ47CalculationRequest(BaseModel):
    crop_type: str = Field(default="Paxta", description="Ekin turi: Paxta, Sabzavot, Bog'dorchilik, Uzum, G'alla")
    area_hectares: float = Field(default=25.0, gt=0)
    technology_type: str = Field(default="DRIP_IRRIGATION", description="DRIP_IRRIGATION, SPRINKLER, PULSAR")
    region: str = Field(default="Andijon viloyati")
    district: str = Field(default="Asaka tumani")
    installation_cost_uzs: Decimal = Field(default=Decimal("250000000.00"), gt=0)
    financed_via_bank_loan: bool = False
    loan_principal_uzs: Optional[Decimal] = None
    annual_interest_rate_pct: Optional[Decimal] = None
    assessment_date: Optional[date] = None


class PQ47CalculationResult(BaseModel):
    program_code: str = "PQ47-WATER-SAVING"
    crop_type: str
    area_hectares: float
    technology_type: str
    region: str
    is_eligible: bool
    base_rate_per_ha_uzs: Decimal
    regional_coefficient: float
    effective_rate_per_ha_uzs: Decimal
    estimated_total_subsidy_uzs: Decimal
    phase_1_initial_disbursement_uzs: Decimal    # 50%
    phase_2_conditional_disbursement_uzs: Decimal  # 50%
    interest_compensation_annual_uzs: Optional[Decimal] = None
    interest_compensation_pct_points: Optional[Decimal] = None
    legal_source: str = "O'zbekiston Respublikasi Prezidentining 2026-yil 5-fevraldagi PQ-47-son qarori 3-bandi"
    effective_date: date = date(2026, 2, 5)
    statutory_status: str = "INDIKATIV_MODELLASHTIRISH"
    calculation_breakdown_uz: str
    methodology_uz: str
    statutory_disclaimer_uz: str


class PF82CalculationRequest(BaseModel):
    crop_type: str = Field(default="Paxta", description="Paxta yoki G'alla")
    harvest_year: int = Field(default=2026, ge=2024, le=2030)
    loan_principal_uzs: Decimal = Field(default=Decimal("150000000.00"), gt=0)
    contractual_interest_rate_pct: Decimal = Field(default=Decimal("14.00"), ge=0, le=50)
    outstanding_balance_uzs: Decimal = Field(default=Decimal("120000000.00"), ge=0)
    days_on_time_repaid: int = Field(default=365, ge=1, le=730)
    has_overdue_debt: bool = False
    repaid_by_year_end: bool = Field(default=False, description="Hosil yili 31-dekabriga qadar to'liq qaytarilgan bo'lsa 5.0%, aks holda shartnomaviy muddatda 2.5%")
    assessment_date: Optional[date] = None


class PF82CalculationResult(BaseModel):
    program_code: str = "PF82-COTTON-WHEAT"
    crop_type: str
    is_eligible: bool
    compensation_pct_points: Decimal
    net_farmer_interest_rate_pct: Decimal
    indicative_interest_compensation_uzs: Decimal
    calculation_basis_uzs: Decimal
    days_compensated: int
    legal_source: str = "O'zbekiston Respublikasi Prezidentining 2026-yil 8-maydagi PF-82-son Farmoni 1-bandi"
    effective_date: date = date(2026, 5, 8)
    statutory_status: str = "INDIKATIV_MODELLASHTIRISH"
    explanation_uz: str
    disclaimer_uz: str


class SubsidyMatchRequest(BaseModel):
    organization_id: str = "scenario-small-farmer"
    region: str = "Andijon viloyati"
    district: str = "Asaka tumani"
    crop_types: List[str] = Field(default_factory=lambda: ["Paxta", "Sabzavot"])
    land_hectares: float = 65.0
    has_drip_irrigation: bool = True
    has_bank_debt: bool = True
    assessment_date: Optional[date] = None


class SubsidyMatchItem(BaseModel):
    program: SubsidyProgram
    eligibility_status: SubsidyEligibilityStatusEnum
    eligibility_label_uz: str
    indicative_support_amount_uzs: Optional[Decimal] = None
    match_reasons_uz: List[str]
    missing_conditions_uz: List[str]


class SubsidyFinancialImpactResponse(BaseModel):
    organization_id: str
    organization_name: str
    assessment_date: str
    matched_programs: List[SubsidyMatchItem]
    total_potential_subsidy_uzs: Decimal
    immediate_cash_inflow_potential_uzs: Decimal    # 50% Initial
    conditional_future_inflow_uzs: Decimal          # 50% Conditional
    impact_on_cash_flow_uz: str
    impact_on_dscr_uz: str
    statutory_disclaimer_uz: str
