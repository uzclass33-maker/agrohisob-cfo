from datetime import date
from decimal import Decimal
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class CurrencyEnum(str, Enum):
    UZS = "UZS"
    USD = "USD"
    EUR = "EUR"

class TransactionDirection(str, Enum):
    INFLOW = "INFLOW"
    OUTFLOW = "OUTFLOW"

class RepaymentTypeEnum(str, Enum):
    ANNUITY = "ANNUITY"
    EQUAL_PRINCIPAL = "EQUAL_PRINCIPAL" # Differential payment

class PaymentFrequencyEnum(str, Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"

class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ScenarioTypeEnum(str, Enum):
    BASE = "BASE"
    OPTIMISTIC = "OPTIMISTIC"
    PESSIMISTIC = "PESSIMISTIC"
    CUSTOM = "CUSTOM"

# -------------------------------------------------------------------------
# 1. Historical Cash Flow Schemas
# -------------------------------------------------------------------------
class CashTransactionInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    transaction_id: Optional[str] = None
    transaction_date: date
    direction: TransactionDirection
    amount: Decimal = Field(..., gt=0, description="Amount in local currency")
    category: str = Field(..., description="CROP_SALES, SEEDS, FUEL, LABOR, DEBT_SERVICE, etc.")
    counterparty: Optional[str] = None
    currency: CurrencyEnum = CurrencyEnum.UZS
    is_reversal: bool = False
    description: Optional[str] = None

class CashFlowAnalysisRequest(BaseModel):
    organization_id: str
    reporting_period: str # e.g. "2024" or "2024-Q1"
    opening_balance: Decimal = Field(default=Decimal("0.00"), ge=0)
    transactions: List[CashTransactionInput]
    currency: CurrencyEnum = CurrencyEnum.UZS

class MonthlyCashFlowItem(BaseModel):
    month_number: int
    month_name: str
    opening_balance: Decimal
    total_inflows: Decimal
    total_outflows: Decimal
    net_cash_flow: Decimal
    closing_balance: Decimal
    is_deficit: bool
    categories: Dict[str, Decimal]

class CashFlowAnalysisResponse(BaseModel):
    organization_id: str
    reporting_period: str
    currency: CurrencyEnum
    initial_opening_balance: Decimal
    final_closing_balance: Decimal
    total_inflows: Decimal
    total_outflows: Decimal
    net_cash_flow: Decimal
    monthly_breakdown: List[MonthlyCashFlowItem]
    category_totals: Dict[str, Decimal]
    data_completeness: Dict[str, Any]
    calculation_version: str = "2.0.0"

# -------------------------------------------------------------------------
# 2. Loan Amortization Schemas
# -------------------------------------------------------------------------
class LoanScheduleRequest(BaseModel):
    principal: Decimal = Field(..., gt=0, description="Initial loan principal amount")
    annual_interest_rate_pct: Decimal = Field(..., ge=0, description="Nominal annual interest rate as percentage (e.g. 14.0 for 14%)")
    start_date: date
    term_months: int = Field(..., gt=0, le=360, description="Repayment term in months")
    payment_frequency: PaymentFrequencyEnum = PaymentFrequencyEnum.MONTHLY
    repayment_type: RepaymentTypeEnum = RepaymentTypeEnum.ANNUITY
    grace_period_months: int = Field(default=0, ge=0, description="Grace period during which only interest is paid")
    currency: CurrencyEnum = CurrencyEnum.UZS

class RepaymentScheduleItem(BaseModel):
    period_number: int
    payment_date: str
    opening_principal: Decimal
    principal_paid: Decimal
    interest_paid: Decimal
    total_payment: Decimal
    remaining_principal: Decimal

class LoanScheduleResponse(BaseModel):
    principal: Decimal
    annual_interest_rate_pct: Decimal
    term_months: int
    repayment_type: RepaymentTypeEnum
    payment_frequency: PaymentFrequencyEnum
    grace_period_months: int
    total_interest_cost: Decimal
    total_payment_sum: Decimal
    effective_periodic_rate_pct: Decimal
    schedule: List[RepaymentScheduleItem]
    calculation_version: str = "2.0.0"
    disclaimer: str = "Ushbu to'lov jadvali ko'rgazmali matematik hisob-kitob bo'lib, bankning rasmiy ofertasi hisoblanmaydi."

# -------------------------------------------------------------------------
# 3. DSCR Schemas
# -------------------------------------------------------------------------
class DSCRCalculationRequest(BaseModel):
    operating_cash_inflows: Decimal = Field(..., ge=0)
    operating_cash_outflows: Decimal = Field(..., ge=0, description="Outflows excluding debt principal & interest")
    debt_service_principal: Decimal = Field(..., ge=0)
    debt_service_interest: Decimal = Field(..., ge=0)

class DSCRThresholdBand(BaseModel):
    tier: str
    label_uz: str
    min_value: Optional[Decimal]
    max_value: Optional[Decimal]

class DSCRCalculationResponse(BaseModel):
    operating_cash_inflows: Decimal
    operating_cash_outflows: Decimal
    cfads: Decimal = Field(..., description="Cash Flow Available for Debt Service (Inflows - Non-debt Outflows)")
    total_debt_service: Decimal
    dscr: Optional[Decimal] = Field(None, description="CFADS / Total Debt Service. None if debt service is zero.")
    has_debt: bool
    status_tier: str
    status_label_uz: str
    interpretation_uz: str
    is_acceptable: bool
    thresholds_applied: List[DSCRThresholdBand]
    calculation_version: str = "2.0.0"

# -------------------------------------------------------------------------
# 4. Liquidity Warning Schemas
# -------------------------------------------------------------------------
class LiquidityAlert(BaseModel):
    warning_type: str # NEGATIVE_CASH, LOW_BUFFER, DEBT_SERVICE_PRESSURE, SEASONAL_GAP
    severity: AlertSeverity
    affected_month: str
    month_number: int
    relevant_figures: Dict[str, Decimal]
    rule_triggered: str
    explanation_uz: str
    suggested_action_uz: str

# -------------------------------------------------------------------------
# 5. Seasonal Forecasting Schemas
# -------------------------------------------------------------------------
class CropForecastAssumption(BaseModel):
    crop_name: str
    area_ha: Decimal = Field(..., gt=0)
    expected_yield_tons_per_ha: Decimal = Field(..., gt=0)
    selling_price_per_ton_uzs: Decimal = Field(..., gt=0)
    harvest_months: List[int] = Field(..., description="List of 1-based month numbers when crop is harvested/delivered")
    collection_delay_months: int = Field(default=0, ge=0, description="Delay between delivery and actual cash receipt")

class CostSeasonalityAssumption(BaseModel):
    # Normalized monthly weights or explicit amounts in UZS (12 elements)
    seeds_planting_by_month: List[Decimal] = Field(default_factory=lambda: [Decimal("0.00")] * 12)
    fertilizer_chemicals_by_month: List[Decimal] = Field(default_factory=lambda: [Decimal("0.00")] * 12)
    fuel_lubricants_by_month: List[Decimal] = Field(default_factory=lambda: [Decimal("0.00")] * 12)
    labor_salaries_by_month: List[Decimal] = Field(default_factory=lambda: [Decimal("0.00")] * 12)
    fixed_monthly_opex_uzs: Decimal = Field(default=Decimal("0.00"), ge=0)

class SeasonalForecastRequest(BaseModel):
    organization_id: str
    fiscal_year: int = 2026
    start_month: int = Field(default=1, ge=1, le=12)
    horizon_months: int = Field(default=12, ge=1, le=36)
    beginning_cash_balance: Decimal = Field(default=Decimal("0.00"), ge=0)
    min_liquidity_buffer_uzs: Decimal = Field(default=Decimal("10000000.00"), ge=0)
    crop_assumptions: List[CropForecastAssumption]
    cost_assumptions: CostSeasonalityAssumption
    existing_monthly_debt_service: List[Decimal] = Field(default_factory=lambda: [Decimal("0.00")] * 12)
    currency: CurrencyEnum = CurrencyEnum.UZS

class MonthlyForecastItem(BaseModel):
    month_number: int
    month_name: str
    opening_balance: Decimal
    projected_inflows: Decimal
    projected_operating_outflows: Decimal
    debt_service: Decimal
    total_outflows: Decimal
    net_cash_flow: Decimal
    closing_balance: Decimal
    cfads: Decimal
    monthly_dscr: Optional[Decimal]
    is_deficit: bool
    is_below_buffer: bool
    alerts: List[LiquidityAlert]

class SeasonalForecastResponse(BaseModel):
    organization_id: str
    fiscal_year: int
    currency: CurrencyEnum
    initial_cash_balance: Decimal
    final_closing_balance: Decimal
    total_annual_inflows: Decimal
    total_annual_outflows: Decimal
    total_debt_service: Decimal
    net_annual_cash_flow: Decimal
    annual_dscr: Optional[Decimal]
    dscr_rating: str
    months_in_deficit: int
    lowest_cash_point: Decimal
    lowest_cash_month: str
    monthly_forecast: List[MonthlyForecastItem]
    all_alerts: List[LiquidityAlert]
    calculation_version: str = "2.0.0"

# -------------------------------------------------------------------------
# 6. Scenario & Sensitivity Schemas
# -------------------------------------------------------------------------
class ScenarioAdjustments(BaseModel):
    revenue_change_pct: Decimal = Field(default=Decimal("0.00"), description="e.g. -20.0 for -20%")
    cost_change_pct: Decimal = Field(default=Decimal("0.00"), description="e.g. +15.0 for +15%")
    collection_delay_months: int = Field(default=0, ge=0)
    interest_rate_delta_pct: Decimal = Field(default=Decimal("0.00"), description="e.g. +2.0 for +2%")

class ScenarioAnalysisRequest(BaseModel):
    base_forecast_request: SeasonalForecastRequest
    scenario_type: ScenarioTypeEnum = ScenarioTypeEnum.CUSTOM
    adjustments: Optional[ScenarioAdjustments] = None

class ScenarioComparisonResponse(BaseModel):
    scenario_type: ScenarioTypeEnum
    adjustments_applied: ScenarioAdjustments
    baseline: SeasonalForecastResponse
    stressed: SeasonalForecastResponse
    variance_net_cash_flow: Decimal
    variance_closing_balance: Decimal
    variance_dscr: Optional[Decimal]
    solvency_impact: str
    risk_summary_uz: List[str]
    calculation_version: str = "2.0.0"

# -------------------------------------------------------------------------
# 7. AI-CFO Insights & Consolidated Dashboard Schemas (Assignment 4)
# -------------------------------------------------------------------------
class InsightTypeEnum(str, Enum):
    LIQUIDITY_DEFICIT = "LIQUIDITY_DEFICIT"
    SEASONAL_GAP = "SEASONAL_GAP"
    DEBT_SERVICE_PRESSURE = "DEBT_SERVICE_PRESSURE"
    COST_CONCENTRATION = "COST_CONCENTRATION"
    WORKING_CAPITAL_SURPLUS = "WORKING_CAPITAL_SURPLUS"
    REVENUE_TIMING_RISK = "REVENUE_TIMING_RISK"
    HEALTHY_CONDITIONS = "HEALTHY_CONDITIONS"

class FinancialInsight(BaseModel):
    insight_id: str
    organization_id: str
    period: str
    insight_type: InsightTypeEnum
    severity: AlertSeverity
    relevant_metric: str
    supporting_values: Dict[str, Any]
    calculation_version: str = "4.0.0"
    explanation_uz: str
    action_category: str
    suggested_action_uz: str
    generation_method: str = "DETERMINISTIC_RULE_ENGINE"  # or "LLM_ASSISTED"
    evidence_data: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str

class DashboardOverviewKPIs(BaseModel):
    total_inflows: Decimal
    total_outflows: Decimal
    net_cash_flow: Decimal
    closing_balance: Decimal
    operating_cash_flow: Decimal
    debt_service: Decimal
    dscr: Optional[Decimal] = None
    dscr_rating: str
    projected_min_balance: Decimal
    min_balance_month: str
    months_in_deficit: int

class DashboardOverviewResponse(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    reporting_period: str
    base_currency: str = "UZS"
    data_source: str
    is_synthetic: bool
    last_data_update: str
    kpis: DashboardOverviewKPIs
    calculation_version: str = "4.0.0"

class DashboardCashFlowResponse(BaseModel):
    organization_id: str
    reporting_period: str
    currency: str = "UZS"
    total_inflows: Decimal
    total_outflows: Decimal
    net_cash_flow: Decimal
    initial_opening_balance: Decimal
    final_closing_balance: Decimal
    monthly_data: List[MonthlyCashFlowItem]
    inflow_by_category: Dict[str, Decimal]
    outflow_by_category: Dict[str, Decimal]
    reconciled_with_engine: bool = True

class DashboardForecastResponse(BaseModel):
    organization_id: str
    fiscal_year: int
    model_version: str = "2.0.0"
    forecast_generation_date: str
    historical_months_count: int
    forecast_months_count: int
    initial_cash_balance: Decimal
    final_closing_balance: Decimal
    lowest_cash_point: Decimal
    lowest_cash_month: str
    months_in_deficit: int
    annual_dscr: Optional[Decimal]
    dscr_rating: str
    monthly_forecast: List[MonthlyForecastItem]
    assumptions: Dict[str, Any]
    liquidity_warnings_count: int

class DashboardDebtResponse(BaseModel):
    organization_id: str
    total_principal: Decimal
    total_interest: Decimal
    total_debt_service: Decimal
    annual_dscr: Optional[Decimal]
    dscr_risk_tier: str
    dscr_interpretation_uz: str
    next_payment_date: str
    next_payment_amount: Decimal
    loan_schedules: List[Dict[str, Any]]

class DashboardRisksResponse(BaseModel):
    organization_id: str
    risks_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    risks: List[Dict[str, Any]]

class AIInsightsResponse(BaseModel):
    organization_id: str
    financial_health_summary_uz: str
    key_findings_uz: List[str]
    insights: List[FinancialInsight]
    generation_method: str = "DETERMINISTIC_RULE_ENGINE"
    model_version: str = "4.0.0"
    is_llm_used: bool = False
    disclaimer_uz: str

