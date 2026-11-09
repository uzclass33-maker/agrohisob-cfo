from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import date, datetime

class OrganizationBase(BaseModel):
    name: str
    inn: str = Field(..., min_length=9, max_length=9, description="9-digit Uzbekistan Tax ID (STIR)")
    legal_type: str
    region: str
    district: str
    land_hectares: float = Field(..., gt=0)
    cadastre_number: Optional[str] = None
    soil_bonitet_score: int = Field(default=65, ge=1, le=100)
    main_crop_type: str
    has_drip_irrigation: bool = False
    has_cold_storage: bool = False
    cold_storage_capacity_tons: float = 0.0

class OrganizationResponse(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime

class DebtItemSchema(BaseModel):
    lender_name: str
    loan_type: str
    contract_number: str
    principal_amount: float
    outstanding_balance: float
    annual_interest_rate: float
    monthly_payment_total: float
    start_date: str
    maturity_date: str
    collateral_description: Optional[str] = None

class TransactionSchema(BaseModel):
    transaction_date: str
    direction: str = Field(..., pattern="^(INFLOW|OUTFLOW)$")
    amount: float = Field(..., gt=0)
    category: str
    counterparty_name: str
    counterparty_inn: Optional[str] = None
    mxik_code: Optional[str] = None
    document_number: Optional[str] = None
    description: Optional[str] = None

class MonthlyFinancialData(BaseModel):
    month_number: int = Field(..., ge=1, le=12)
    month_name: str
    opening_balance: float
    total_inflows: float
    total_outflows: float
    net_cash_flow: float
    closing_balance: float
    debt_service: float
    dscr: Optional[float] = None
    is_deficit: bool = False
    inflows_breakdown: Dict[str, float] = Field(default_factory=dict)
    outflows_breakdown: Dict[str, float] = Field(default_factory=dict)

class FinancialCalculationRequest(BaseModel):
    scenario_id: Optional[str] = None
    initial_opening_balance: float = Field(..., ge=0)
    monthly_transactions: Optional[List[TransactionSchema]] = None
    monthly_overrides: Optional[List[Dict[str, Any]]] = None

class FinancialSummaryResponse(BaseModel):
    organization_id: Optional[str] = None
    organization_name: str
    fiscal_year: int
    initial_opening_balance: float
    final_closing_balance: float
    total_annual_inflows: float
    total_annual_outflows: float
    net_annual_cash_flow: float
    total_debt_service: float
    annual_dscr: Optional[float] = None
    dscr_rating: str  # EXCELLENT, HEALTHY, WATCHLIST, CRITICAL, NO_DEBT
    months_in_deficit: int
    lowest_cash_point: float
    lowest_cash_month: str
    is_mathematically_reconciled: bool
    reconciliation_message: str
    monthly_data: List[MonthlyFinancialData]
    category_summary: Dict[str, float]

class StressTestRequest(BaseModel):
    scenario_id: str
    yield_shock_pct: float = Field(default=0.0, ge=-50.0, le=50.0, description="Yield shock percentage e.g. -20% or +10%")
    price_shock_pct: float = Field(default=0.0, ge=-50.0, le=50.0, description="Price shock percentage e.g. -15% or +15%")
    cost_shock_pct: float = Field(default=0.0, ge=-50.0, le=50.0, description="Operating cost shock percentage e.g. +10%")
    interest_rate_override: Optional[float] = Field(default=None, ge=0.0, le=50.0, description="Annual loan interest rate override")

class StressTestResponse(BaseModel):
    scenario_id: str
    scenario_name: str
    baseline_annual_inflow: float
    baseline_annual_outflow: float
    baseline_dscr: float
    stressed_annual_inflow: float
    stressed_annual_outflow: float
    stressed_dscr: float
    dscr_change_pct: float
    deficit_months_baseline: int
    deficit_months_stressed: int
    minimum_cash_baseline: float
    minimum_cash_stressed: float
    solvency_status: str
    stressed_monthly_data: List[MonthlyFinancialData]

class CreditReadinessScorecard(BaseModel):
    scenario_id: str
    organization_name: str
    legal_type: str
    region: str
    land_hectares: float
    soil_bonitet_score: int
    credit_score: int = Field(..., ge=0, le=100)
    rating_tier: str  # Tier 1 (AAA-A), Tier 2 (BBB-B), Tier 3 (CCC-C), Tier 4 (D)
    dscr: float
    dscr_assessment: str
    max_additional_borrowing_capacity_uzs: float
    recommended_loan_product: str
    vmq613_leasehold_estimated_value_uzs: float
    vmq613_collateral_discount_factor: float
    vmq613_bankable_collateral_uzs: float
    key_strengths: List[str]
    identified_risks: List[str]
    credit_committee_readiness_notes: str
    disclaimer: str

class SyntheticScenarioMeta(BaseModel):
    id: str
    key: str
    name: str
    category: str  # small_farmer, exporter, cluster
    category_label: str
    region: str
    district: str
    hectares: float
    main_crop: str
    initial_cash_uzs: float
    annual_revenue_estimate_uzs: float
    debt_load_uzs: float
    description: str
    key_dynamics: str
    is_synthetic: bool = True
