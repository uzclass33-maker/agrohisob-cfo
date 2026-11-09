export interface SyntheticScenarioMeta {
  id: string;
  key: string;
  name: string;
  category: 'small_farmer' | 'exporter' | 'cluster';
  category_label: string;
  region: string;
  district: string;
  hectares: number;
  main_crop: string;
  initial_cash_uzs: number;
  annual_revenue_estimate_uzs: number;
  debt_load_uzs: number;
  description: string;
  key_dynamics: string;
  is_synthetic: boolean;
}

export interface MonthlyFinancialData {
  month_number: number;
  month_name: string;
  opening_balance: number;
  total_inflows: number;
  total_outflows: number;
  net_cash_flow: number;
  closing_balance: number;
  debt_service: number;
  dscr: number | null;
  is_deficit: boolean;
  inflows_breakdown: Record<string, number>;
  outflows_breakdown: Record<string, number>;
}

export interface FinancialSummaryResponse {
  organization_id?: string;
  organization_name: string;
  fiscal_year: number;
  initial_opening_balance: number;
  final_closing_balance: number;
  total_annual_inflows: number;
  total_annual_outflows: number;
  net_annual_cash_flow: number;
  total_debt_service: number;
  annual_dscr: number;
  dscr_rating: 'EXCELLENT' | 'HEALTHY' | 'WATCHLIST' | 'CRITICAL';
  months_in_deficit: number;
  lowest_cash_point: number;
  lowest_cash_month: string;
  is_mathematically_reconciled: boolean;
  reconciliation_message: string;
  monthly_data: MonthlyFinancialData[];
  category_summary: Record<string, number>;
}

export interface StressTestRequest {
  scenario_id: string;
  yield_shock_pct: number;
  price_shock_pct: number;
  cost_shock_pct: number;
  interest_rate_override?: number;
}

export interface StressTestResponse {
  scenario_id: string;
  scenario_name: string;
  baseline_annual_inflow: number;
  baseline_annual_outflow: number;
  baseline_dscr: number;
  stressed_annual_inflow: number;
  stressed_annual_outflow: number;
  stressed_dscr: number;
  dscr_change_pct: number;
  deficit_months_baseline: number;
  deficit_months_stressed: number;
  minimum_cash_baseline: number;
  minimum_cash_stressed: number;
  solvency_status: string;
  stressed_monthly_data: MonthlyFinancialData[];
}

export interface CreditReadinessScorecard {
  scenario_id: string;
  organization_name: string;
  legal_type: string;
  region: string;
  land_hectares: number;
  soil_bonitet_score: number;
  credit_score: number;
  rating_tier: string;
  dscr: number;
  dscr_assessment: string;
  max_additional_borrowing_capacity_uzs: number;
  recommended_loan_product: string;
  vmq613_leasehold_estimated_value_uzs: number;
  vmq613_collateral_discount_factor: number;
  vmq613_bankable_collateral_uzs: number;
  key_strengths: string[];
  identified_risks: string[];
  credit_committee_readiness_notes: string;
  disclaimer: string;
}

// -------------------------------------------------------------------------
// ASSIGNMENT 2 TYPES: Calculation Engine, Amortization, DSCR, Scenarios, Risk
// -------------------------------------------------------------------------
export interface RepaymentScheduleItem {
  period_number: number;
  payment_date: string;
  opening_principal: number;
  principal_paid: number;
  interest_paid: number;
  total_payment: number;
  remaining_principal: number;
}

export interface LoanScheduleResponse {
  principal: number;
  annual_interest_rate_pct: number;
  term_months: number;
  repayment_type: 'ANNUITY' | 'EQUAL_PRINCIPAL';
  payment_frequency: 'MONTHLY' | 'QUARTERLY';
  grace_period_months: number;
  total_interest_cost: number;
  total_payment_sum: number;
  effective_periodic_rate_pct: number;
  schedule: RepaymentScheduleItem[];
  calculation_version: string;
  disclaimer: string;
}

export interface DSCRCalculationResponse {
  operating_cash_inflows: number;
  operating_cash_outflows: number;
  cfads: number;
  total_debt_service: number;
  dscr: number | null;
  has_debt: boolean;
  status_tier: string;
  status_label_uz: string;
  interpretation_uz: string;
  is_acceptable: boolean;
  calculation_version: string;
}

export interface LiquidityAlert {
  warning_type: 'NEGATIVE_CASH' | 'LOW_BUFFER' | 'DEBT_SERVICE_PRESSURE' | 'SEASONAL_GAP';
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  affected_month: string;
  month_number: number;
  relevant_figures: Record<string, number>;
  rule_triggered: string;
  explanation_uz: string;
  suggested_action_uz: string;
}

export interface ScenarioComparisonItem {
  scenario_type: 'BASE' | 'OPTIMISTIC' | 'PESSIMISTIC' | 'CUSTOM';
  revenue_change_pct: number;
  cost_change_pct: number;
  closing_balance: number;
  net_cash_flow: number;
  annual_dscr: number | null;
  solvency_status: string;
}

// -------------------------------------------------------------------------
// ASSIGNMENT 4 TYPES: AI-CFO Financial Dashboard, Intelligence & Analytics
// -------------------------------------------------------------------------
export interface DashboardOverviewKPIs {
  total_inflows: number;
  total_outflows: number;
  net_cash_flow: number;
  closing_balance: number;
  operating_cash_flow: number;
  debt_service: number;
  dscr: number | null;
  dscr_rating: string;
  projected_min_balance: number;
  min_balance_month: string;
  months_in_deficit: number;
}

export interface DashboardOverviewResponse {
  organization_id: string;
  organization_name: string;
  organization_type: string;
  reporting_period: string;
  base_currency: string;
  data_source: 'SYNTHETIC_BENCHMARK' | 'BANK_STATEMENT_IMPORT' | string;
  is_synthetic: boolean;
  last_data_update: string;
  kpis: DashboardOverviewKPIs;
  calculation_version: string;
}

export interface DashboardCashFlowItem {
  month_number: number;
  month_name: string;
  opening_balance: number;
  total_inflows: number;
  total_outflows: number;
  net_cash_flow: number;
  closing_balance: number;
  is_deficit: boolean;
  categories: Record<string, number>;
}

export interface DashboardCashFlowResponse {
  organization_id: string;
  reporting_period: string;
  currency: string;
  total_inflows: number;
  total_outflows: number;
  net_cash_flow: number;
  initial_opening_balance: number;
  final_closing_balance: number;
  monthly_data: DashboardCashFlowItem[];
  inflow_by_category: Record<string, number>;
  outflow_by_category: Record<string, number>;
  reconciled_with_engine: boolean;
}

export interface MonthlyForecastItem {
  month_number: number;
  month_name: string;
  opening_balance: number;
  projected_inflows: number;
  projected_operating_outflows: number;
  debt_service: number;
  total_outflows: number;
  net_cash_flow: number;
  closing_balance: number;
  cfads: number;
  monthly_dscr: number | null;
  is_deficit: boolean;
  is_below_buffer: boolean;
  alerts: LiquidityAlert[];
}

export interface DashboardForecastResponse {
  organization_id: string;
  fiscal_year: number;
  model_version: string;
  forecast_generation_date: string;
  historical_months_count: number;
  forecast_months_count: number;
  initial_cash_balance: number;
  final_closing_balance: number;
  lowest_cash_point: number;
  lowest_cash_month: string;
  months_in_deficit: number;
  annual_dscr: number | null;
  dscr_rating: string;
  monthly_forecast: MonthlyForecastItem[];
  assumptions: Record<string, any>;
  liquidity_warnings_count: number;
}

export interface LoanScheduleSummaryItem {
  lender_name: string;
  loan_type: string;
  contract_number: string;
  principal_amount: number;
  annual_interest_rate: number;
  monthly_payment: number;
  start_date: string;
  maturity_date: string;
  collateral: string;
}

export interface DashboardDebtResponse {
  organization_id: string;
  total_principal: number;
  total_interest: number;
  total_debt_service: number;
  annual_dscr: number | null;
  dscr_risk_tier: string;
  dscr_interpretation_uz: string;
  next_payment_date: string;
  next_payment_amount: number;
  loan_schedules: LoanScheduleSummaryItem[];
}

export interface DashboardRiskItem {
  id: string;
  title: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  affected_period: string;
  metric_value: string;
  trigger_rule: string;
  explanation_uz: string;
  business_response_uz: string;
}

export interface DashboardRisksResponse {
  organization_id: string;
  risks_count: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  risks: DashboardRiskItem[];
}

export interface FinancialInsight {
  insight_id: string;
  insight_type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  headline_uz: string;
  core_message_uz: string;
  evidence_bullets_uz: string[];
  recommended_action_uz: string;
  supporting_metrics: Record<string, any>;
  is_verified_fact: boolean;
  generation_method: string;
}

export interface AIInsightsResponse {
  organization_id: string;
  financial_health_summary_uz: string;
  key_findings_uz: string[];
  insights: FinancialInsight[];
  generation_method: string;
  model_version: string;
  is_llm_used: boolean;
  disclaimer_uz: string;
}

export interface ScenarioSimulationInput {
  organization_id: string;
  scenario_type: 'BASE' | 'OPTIMISTIC' | 'PESSIMISTIC' | 'CUSTOM';
  revenue_change_pct: number;
  cost_change_pct: number;
  collection_delay_months: number;
  interest_rate_delta_pct: number;
}

export interface ScenarioComparisonResponse {
  scenario_type: 'BASE' | 'OPTIMISTIC' | 'PESSIMISTIC' | 'CUSTOM';
  adjustments_applied: {
    revenue_change_pct: number;
    cost_change_pct: number;
    collection_delay_months: number;
    interest_rate_delta_pct: number;
  };
  baseline: {
    total_annual_inflows: number;
    total_annual_outflows: number;
    net_annual_cash_flow: number;
    final_closing_balance: number;
    lowest_cash_point: number;
    annual_dscr: number | null;
    months_in_deficit: number;
    monthly_forecast: MonthlyForecastItem[];
  };
  stressed: {
    total_annual_inflows: number;
    total_annual_outflows: number;
    net_annual_cash_flow: number;
    final_closing_balance: number;
    lowest_cash_point: number;
    annual_dscr: number | null;
    months_in_deficit: number;
    monthly_forecast: MonthlyForecastItem[];
  };
  variance_net_cash_flow: number;
  variance_closing_balance: number;
  variance_dscr: number | null;
  solvency_impact: string;
}
