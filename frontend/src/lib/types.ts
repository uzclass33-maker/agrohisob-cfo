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

// =========================================================================
// ASSIGNMENT 5: CREDIT DOSSIER & REPORTING TYPES
// =========================================================================

export type LoanPurpose =
  | 'WORKING_CAPITAL'
  | 'AGRICULTURAL_INPUTS'
  | 'MACHINERY_EQUIPMENT'
  | 'DRIP_IRRIGATION'
  | 'COLD_STORAGE'
  | 'BUSINESS_EXPANSION'
  | 'OTHER';

export type ChecklistStatus = 'AVAILABLE' | 'MISSING' | 'NEEDS_REVIEW' | 'NOT_APPLICABLE';

export type ReadinessStatus = 'READY_FOR_REVIEW' | 'ADDITIONAL_INFO_REQUIRED' | 'INSUFFICIENT_DATA';

export interface CreditProfile {
  organization_id: string;
  organization_name: string;
  organization_type: string;
  business_activity: string;
  region: string;
  district: string;
  inn?: string;
  operating_years: number;
  reporting_currency: string;
  land_hectares: number;
  main_crop_types: string[];
  harvest_months: number[];
  sales_months: number[];
  customer_segments: string;
  requested_loan_amount_uzs: number;
  loan_purpose: LoanPurpose;
  proposed_term_months: number;
  proposed_annual_interest_rate_pct: number;
  repayment_structure: 'ANNUITY' | 'EQUAL_PRINCIPAL';
  grace_period_months: number;
  expected_disbursement_date: string;
}

export interface ChecklistItem {
  id: string;
  category: string;
  category_title_uz: string;
  title_uz: string;
  status: ChecklistStatus;
  rationale_uz: string;
  is_critical: boolean;
}

export interface DocumentReadinessChecklist {
  checklist_title_uz: string;
  items: ChecklistItem[];
  total_items: number;
  available_count: number;
  missing_count: number;
  needs_review_count: number;
  completeness_percentage: number;
  disclaimer_uz: string;
}

export interface FinancialReadinessAssessment {
  overall_status: ReadinessStatus;
  status_label_uz: string;
  readiness_score: number;
  data_completeness_pct: number;
  cash_flow_stability_uz: string;
  dscr_capacity_uz: string;
  forecast_confidence_uz: string;
  key_strengths_uz: string[];
  identified_risks_uz: string[];
  critical_limitations_uz: string[];
  audit_disclaimer_uz: string;
}

export interface HistoricalFinancialSummary {
  total_inflows: number;
  total_outflows: number;
  net_cash_flow: number;
  initial_opening_balance: number;
  final_closing_balance: number;
  monthly_data: Array<{
    month_number: number;
    month_name: string;
    opening_balance: number;
    inflows: number;
    outflows: number;
    net_cash_flow: number;
    closing_balance: number;
    is_deficit: boolean;
  }>;
  inflow_categories: Record<string, number>;
  outflow_categories: Record<string, number>;
}

export interface DebtDscrSummary {
  requested_principal: number;
  requested_term_months: number;
  annual_interest_rate_pct: number;
  repayment_structure: string;
  grace_period_months: number;
  total_interest_cost: number;
  total_payment_sum: number;
  first_year_new_loan_service: number;
  existing_annual_debt_service: number;
  combined_annual_debt_service: number;
  standalone_dscr: number | null;
  combined_dscr: number | null;
  dscr_formula: string;
  amortization_schedule: Array<{
    period: number;
    date: string;
    opening_principal: number;
    principal_paid: number;
    interest_paid: number;
    total_payment: number;
    remaining_principal: number;
  }>;
}

export interface CreditDossierData {
  dossier_id: string;
  organization_id: string;
  organization_name: string;
  generation_timestamp: string;
  calculation_version: string;
  reporting_period: string;
  credit_profile: CreditProfile;
  checklist: DocumentReadinessChecklist;
  readiness_assessment: FinancialReadinessAssessment;
  historical_summary: HistoricalFinancialSummary;
  forecast_summary: {
    fiscal_year: number;
    initial_cash_balance: number;
    final_closing_balance: number;
    total_annual_inflows: number;
    total_annual_outflows: number;
    net_annual_cash_flow: number;
    lowest_cash_point: number;
    lowest_cash_month: string;
    months_in_deficit: number;
    monthly_forecast: Array<{
      month_number: number;
      month_name: string;
      opening_balance: number;
      inflows: number;
      operating_outflows: number;
      debt_service: number;
      total_outflows: number;
      net_cash_flow: number;
      closing_balance: number;
      cfads: number;
      monthly_dscr: number | null;
      is_deficit: boolean;
    }>;
  };
  debt_dscr_summary: DebtDscrSummary;
  risks_scenarios_summary: {
    base: {
      inflows: number;
      outflows: number;
      closing_balance: number;
      dscr: number | null;
      deficits: number;
    };
    optimistic: {
      inflows: number;
      outflows: number;
      closing_balance: number;
      dscr: number | null;
      deficits: number;
      variance_closing: number;
    };
    pessimistic: {
      inflows: number;
      outflows: number;
      closing_balance: number;
      dscr: number | null;
      deficits: number;
      variance_closing: number;
      solvency_impact: string;
    };
  };
  data_sources_and_assumptions: Record<string, any>;
  collateral_readiness_summary?: {
    is_eligible: boolean;
    readiness_pct: number;
    indicative_valuation_uzs: number;
    max_pledge_value_uzs: number;
    remaining_years: number;
    legal_readiness_status: string;
    cadastral_reference: string;
  };
  subsidy_opportunities_summary?: {
    matched_count: number;
    total_potential_uzs: number;
    phase_1_immediate_uzs: number;
    phase_2_conditional_uzs: number;
    cash_flow_impact_uz: string;
    dscr_impact_uz: string;
  };
  regulatory_disclaimer_uz: string;
}

export interface GeneratedReportRecord {
  report_id: string;
  dossier_id: string;
  organization_id: string;
  report_title: string;
  created_at: string;
  status: string;
  pdf_path?: string;
  xlsx_path?: string;
  pdf_url?: string;
  xlsx_url?: string;
  file_hash?: string;
  file_size_bytes_pdf?: number;
  file_size_bytes_xlsx?: number;
  calculation_version: string;
}

// ==========================================
// ASSIGNMENT 6: COLLATERAL, SUBSIDIES & REGULATORY TYPES
// ==========================================

export interface RegulatorySourceRecord {
  id: string;
  document_code: string;
  document_title_uz: string;
  official_lex_url: string;
  issuing_authority_uz: string;
  effective_from: string;
  effective_to?: string | null;
  verification_status: string;
  last_verified_at: string;
  key_clauses_summary_uz: Record<string, string>;
  applicable_beneficiaries_uz: string[];
}

export interface LandLeaseProfile {
  organization_id: string;
  organization_name: string;
  land_reference: string;
  region: string;
  district: string;
  area_hectares: number;
  land_category: string;
  lease_start_date: string;
  lease_expiration_date: string;
  proposed_loan_maturity_date: string;
  proposed_loan_amount_uzs: number;
  is_registered_in_cadastre: boolean;
  registration_number?: string;
  has_legal_restrictions: boolean;
  restriction_details?: string;
  is_disputed: boolean;
  is_terminated: boolean;
  is_secondary_lease: boolean;
  has_sublease_authority_permission: boolean;
  soil_bonitet_score: number;
  main_crop_type: string;
  normative_annual_net_benefit_per_ha_uzs: number;
  discount_rate_pct: number;
  target_ltv_pct: number;
  has_independent_appraisal: boolean;
  independent_appraisal_value_uzs?: number | null;
}

export interface VMQ613RuleCheckItem {
  rule_id: string;
  rule_name_uz: string;
  statutory_basis: string;
  status: 'COMPLIANT' | 'NON_COMPLIANT' | 'WARNING' | 'CONDITIONAL_PASS';
  status_label_uz: string;
  explanation_uz: string;
  action_required_uz?: string;
}

export interface VMQ613ScreeningResult {
  is_eligible: boolean;
  overall_legal_status_uz: string;
  screening_date: string;
  lease_duration_years: number;
  remaining_lease_years: number;
  post_maturity_buffer_years: number;
  rule_checks: VMQ613RuleCheckItem[];
  defects: string[];
  remediation_steps: string[];
  statutory_disclaimer_uz: string;
}

export interface IndicativeValuationRequest {
  area_hectares: number;
  soil_bonitet_score: number;
  remaining_lease_years: number;
  normative_annual_net_benefit_per_ha_uzs: number;
  discount_rate_pct: number;
  annual_benefit_growth_pct: number;
  target_ltv_pct: number;
}

export interface DCFCashFlowPeriod {
  year: number;
  nominal_cash_flow_uzs: number;
  discount_factor: number;
  discounted_cash_flow_uzs: number;
  cumulative_pv_uzs: number;
}

export interface IndicativeValuationResult {
  methodology_applied: string;
  valuation_horizon_years: number;
  discount_rate_pct: number;
  soil_bonitet_score: number;
  bonitet_adjustment_factor: number;
  adjusted_annual_net_benefit_per_ha_uzs: number;
  total_adjusted_annual_net_benefit_uzs: number;
  cash_flow_schedule: DCFCashFlowPeriod[];
  indicative_market_value_uzs: number;
  target_ltv_pct: number;
  max_pledge_value_uzs: number;
  statutory_disclaimer_uz: string;
}

export interface CollateralScenarioResult {
  scenario_name: string;
  scenario_label_uz: string;
  discount_rate_pct: number;
  annual_net_benefit_per_ha_uzs: number;
  indicative_valuation_uzs: number;
  max_pledge_value_uzs: number;
  variance_pct: number;
  description_uz: string;
}

export interface CollateralSensitivityAnalysis {
  base_scenario: CollateralScenarioResult;
  optimistic_scenario: CollateralScenarioResult;
  pessimistic_scenario: CollateralScenarioResult;
  volatility_range_uzs: number;
  key_risk_drivers_uz: string[];
}

export interface CollateralChecklistItem {
  id: string;
  code: string;
  document_name_uz: string;
  issuing_body_uz: string;
  status: 'AVAILABLE' | 'MISSING' | 'NEEDS_VERIFICATION' | 'NOT_APPLICABLE';
  status_label_uz: string;
  is_mandatory: boolean;
  statutory_reference: string;
  description_uz: string;
}

export interface CollateralDocumentChecklist {
  checklist_id: string;
  total_documents: number;
  available_count: number;
  missing_count: number;
  needs_verification_count: number;
  readiness_percentage: number;
  items: CollateralChecklistItem[];
  readiness_verdict_uz: string;
}

export interface CollateralPreparationSummary {
  summary_id: string;
  organization_id: string;
  organization_name: string;
  generation_date: string;
  profile: LandLeaseProfile;
  screening: VMQ613ScreeningResult;
  valuation: IndicativeValuationResult;
  sensitivity: CollateralSensitivityAnalysis;
  checklist: CollateralDocumentChecklist;
  regulatory_disclaimer_uz: string;
}

export interface SubsidyProgram {
  id: string;
  program_code: string;
  program_name_uz: string;
  managing_authority_uz: string;
  legal_source_code: string;
  legal_source_url: string;
  legal_clause: string;
  effective_from: string;
  effective_to?: string | null;
  is_active: boolean;
  verification_status: string;
  supported_crops: string[];
  supported_technologies: string[];
  eligible_regions: string[];
  base_rate_uzs_per_ha?: number | null;
  rate_description_uz: string;
  interest_compensation_pct_points?: number | null;
  required_documents_uz: string[];
}

export interface PQ47CalculationRequest {
  crop_type: string;
  area_hectares: number;
  technology_type: string;
  region: string;
  district: string;
  installation_cost_uzs: number;
  financed_via_bank_loan: boolean;
  loan_principal_uzs?: number | null;
  annual_interest_rate_pct?: number | null;
  assessment_date?: string | null;
}

export interface PQ47CalculationResult {
  program_code: string;
  crop_type: string;
  area_hectares: number;
  technology_type: string;
  region: string;
  is_eligible: boolean;
  base_rate_per_ha_uzs: number;
  regional_coefficient: number;
  effective_rate_per_ha_uzs: number;
  estimated_total_subsidy_uzs: number;
  phase_1_initial_disbursement_uzs: number;
  phase_2_conditional_disbursement_uzs: number;
  interest_compensation_annual_uzs?: number | null;
  interest_compensation_pct_points?: number | null;
  calculation_breakdown_uz: string;
  methodology_uz: string;
  statutory_disclaimer_uz: string;
}

export interface PF82CalculationRequest {
  crop_type: string;
  harvest_year: number;
  loan_principal_uzs: number;
  contractual_interest_rate_pct: number;
  outstanding_balance_uzs: number;
  days_on_time_repaid: number;
  has_overdue_debt: boolean;
  assessment_date?: string | null;
}

export interface PF82CalculationResult {
  program_code: string;
  crop_type: string;
  is_eligible: boolean;
  compensation_pct_points: number;
  net_farmer_interest_rate_pct: number;
  indicative_interest_compensation_uzs: number;
  calculation_basis_uzs: number;
  days_compensated: number;
  explanation_uz: string;
  disclaimer_uz: string;
}

export interface SubsidyMatchRequest {
  organization_id: string;
  region: string;
  district: string;
  crop_types: string[];
  land_hectares: number;
  has_drip_irrigation: boolean;
  has_bank_debt: boolean;
  assessment_date?: string | null;
}

export interface SubsidyMatchItem {
  program: SubsidyProgram;
  eligibility_status:
    | 'POTENTIALLY_ELIGIBLE'
    | 'NOT_ELIGIBLE_UNDER_VERIFIED_RULE'
    | 'MORE_INFORMATION_REQUIRED'
    | 'RULE_NOT_VERIFIED'
    | 'OUTSIDE_EFFECTIVE_PERIOD';
  eligibility_label_uz: string;
  indicative_support_amount_uzs?: number | null;
  match_reasons_uz: string[];
  missing_conditions_uz: string[];
}

export interface SubsidyFinancialImpactResponse {
  organization_id: string;
  organization_name: string;
  assessment_date: string;
  matched_programs: SubsidyMatchItem[];
  total_potential_subsidy_uzs: number;
  immediate_cash_inflow_potential_uzs: number;
  conditional_future_inflow_uzs: number;
  impact_on_cash_flow_uz: string;
  impact_on_dscr_uz: string;
  statutory_disclaimer_uz: string;
}
