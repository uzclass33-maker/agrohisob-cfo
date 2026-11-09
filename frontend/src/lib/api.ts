import { 
  SyntheticScenarioMeta, 
  FinancialSummaryResponse, 
  StressTestRequest, 
  StressTestResponse, 
  CreditReadinessScorecard 
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000';

export async function fetchScenarios(): Promise<SyntheticScenarioMeta[]> {
  const res = await fetch(`${API_BASE}/api/scenarios`, { cache: 'no-store' });
  if (!res.ok) {
    throw new Error(`Failed to fetch scenarios: ${res.statusText}`);
  }
  return res.json();
}

export async function calculateFinancials(
  scenarioId: string, 
  initialBalance: number = 0
): Promise<FinancialSummaryResponse> {
  const res = await fetch(`${API_BASE}/api/financials/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      scenario_id: scenarioId,
      initial_opening_balance: initialBalance
    }),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Financial calculation failed: ${res.statusText}`);
  }
  return res.json();
}

export async function runStressTest(params: StressTestRequest): Promise<StressTestResponse> {
  const res = await fetch(`${API_BASE}/api/financials/stress-test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Stress test execution failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchCreditReadiness(scenarioId: string): Promise<CreditReadinessScorecard> {
  const res = await fetch(`${API_BASE}/api/reports/credit-readiness/${scenarioId}`, { cache: 'no-store' });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch credit report: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchLoanSchedule(params: {
  principal: number;
  annual_interest_rate_pct: number;
  start_date: string;
  term_months: number;
  repayment_type?: 'ANNUITY' | 'EQUAL_PRINCIPAL';
  grace_period_months?: number;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/finance/loans/schedule`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...params,
      repayment_type: params.repayment_type || 'ANNUITY',
      grace_period_months: params.grace_period_months || 0
    }),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to calculate loan schedule: ${res.statusText}`);
  }
  return res.json();
}

export async function calculateDSCRAPI(params: {
  operating_cash_inflows: number;
  operating_cash_outflows: number;
  debt_service_principal: number;
  debt_service_interest: number;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/finance/dscr/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to calculate DSCR: ${res.statusText}`);
  }
  return res.json();
}

export async function uploadImportFile(
  file: File,
  documentType: 'E_FAKTURA' | 'BANK_STATEMENT',
  organizationId: string = 'demo-org-agro-01'
): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('document_type', documentType);
  formData.append('organization_id', organizationId);

  const res = await fetch(`${API_BASE}/api/v1/imports/upload`, {
    method: 'POST',
    body: formData,
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchBatchPreview(batchId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/imports/${batchId}/preview`, { cache: 'no-store' });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch preview: ${res.statusText}`);
  }
  return res.json();
}

export async function updateBatchMapping(batchId: string, mappings: Record<string, string>): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/imports/${batchId}/mapping`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mappings }),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Mapping update failed: ${res.statusText}`);
  }
  return res.json();
}

export async function overrideBatchRow(batchId: string, rowId: string, override: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/imports/${batchId}/rows/${rowId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(override),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Row override failed: ${res.statusText}`);
  }
  return res.json();
}

export async function commitImportBatch(batchId: string, organizationId: string = 'demo-org-agro-01'): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/imports/${batchId}/commit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ batch_id: batchId, organization_id: organizationId }),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Commit failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchImportHistory(organizationId: string = 'demo-org-agro-01'): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/imports/history/list?organization_id=${encodeURIComponent(organizationId)}`, {
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch history: ${res.statusText}`);
  }
  return res.json();
}

// -------------------------------------------------------------------------
// ASSIGNMENT 4 API CLIENT FUNCTIONS: AI-CFO Financial Dashboard
// -------------------------------------------------------------------------
export async function fetchDashboardOverview(organizationId: string, period: string = '2026'): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/dashboard/overview?organization_id=${encodeURIComponent(organizationId)}&reporting_period=${encodeURIComponent(period)}`, {
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch overview: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchDashboardCashFlow(organizationId: string, period: string = '2026'): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/dashboard/cashflow?organization_id=${encodeURIComponent(organizationId)}&reporting_period=${encodeURIComponent(period)}`, {
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch cashflow: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchDashboardForecast(organizationId: string, fiscalYear: number = 2026): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/dashboard/forecast?organization_id=${encodeURIComponent(organizationId)}&fiscal_year=${fiscalYear}`, {
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch forecast: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchDashboardDebt(organizationId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/dashboard/debt?organization_id=${encodeURIComponent(organizationId)}`, {
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch debt analytics: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchDashboardRisks(organizationId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/dashboard/risks?organization_id=${encodeURIComponent(organizationId)}`, {
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch risk monitor: ${res.statusText}`);
  }
  return res.json();
}

export async function simulateDashboardScenario(params: {
  organization_id: string;
  scenario_type?: string;
  revenue_change_pct: number;
  cost_change_pct: number;
  collection_delay_months: number;
  interest_rate_delta_pct: number;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/dashboard/scenarios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to simulate scenario: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchAIInsights(organizationId: string, requestLlm: boolean = false): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/insights?organization_id=${encodeURIComponent(organizationId)}&request_llm=${requestLlm}`, {
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch AI insights: ${res.statusText}`);
  }
  return res.json();
}

export async function explainInsightAPI(params: {
  organization_id: string;
  insight_id?: string;
  request_llm?: boolean;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/insights/explain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to explain insight: ${res.statusText}`);
  }
  return res.json();
}

// =========================================================================
// ASSIGNMENT 5: CREDIT DOSSIER & REPORTING CLIENT APIS
// =========================================================================

export async function validateCreditProfileAPI(profile: any): Promise<{
  is_valid: boolean;
  errors: string[];
  credit_profile: any;
}> {
  const res = await fetch(`${API_BASE}/api/v1/reports/credit/profile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Kredit profilini tekshirishda xatolik yuz berdi: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchDocumentReadinessChecklist(organizationId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/reports/credit/validate?organization_id=${encodeURIComponent(organizationId)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ organization_id: organizationId }),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Hujjatlar ro'yxatini yuklashda xatolik yuz berdi: ${res.statusText}`);
  }
  return res.json();
}

export async function previewCreditDossier(organizationId: string, customProfile?: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/reports/credit/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      organization_id: organizationId,
      fiscal_year: 2026,
      credit_profile: customProfile
    }),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Kredit dosye dastlabki ko'rinishini shakllantirishda xatolik: ${res.statusText}`);
  }
  return res.json();
}

export async function generateCreditDossier(organizationId: string, customProfile?: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/reports/credit/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      organization_id: organizationId,
      fiscal_year: 2026,
      credit_profile: customProfile
    }),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Hisobot fayllarini generatsiya qilishda xatolik yuz berdi: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchReportHistory(organizationId?: string): Promise<any[]> {
  const url = organizationId 
    ? `${API_BASE}/api/v1/reports/history?organization_id=${encodeURIComponent(organizationId)}`
    : `${API_BASE}/api/v1/reports/history`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Hisobotlar tarixini yuklashda xatolik: ${res.statusText}`);
  }
  return res.json();
}

export function getFullDownloadUrl(pathUrl: string): string {
  if (pathUrl.startsWith('http://') || pathUrl.startsWith('https://')) {
    return pathUrl;
  }
  return `${API_BASE}${pathUrl}`;
}


// ==========================================
// ASSIGNMENT 6: COLLATERAL, SUBSIDIES & REGULATORY API CLIENTS
// ==========================================

export async function fetchRegulatorySources(verifiedOnly: boolean = true): Promise<any[]> {
  const res = await fetch(`${API_BASE}/api/v1/regulatory/sources?verified_only=${verifiedOnly}`, { cache: 'no-store' });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Me'yoriy hujjatlarni yuklashda xatolik: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchRegulatorySource(code: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/regulatory/sources/${encodeURIComponent(code)}`, { cache: 'no-store' });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Me'yoriy hujjat ma'lumotlarini olishda xatolik: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchDefaultCollateralProfile(organizationId: string = 'scenario-small-farmer'): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/collateral/profile/default?organization_id=${encodeURIComponent(organizationId)}`, { cache: 'no-store' });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Standart garov profilini yuklashda xatolik: ${res.statusText}`);
  }
  return res.json();
}

export async function screenCollateralEligibility(profile: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/collateral/eligibility`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `VMQ-613 huquqiy tahlilida xatolik: ${res.statusText}`);
  }
  return res.json();
}

export async function calculateCollateralValuation(req: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/collateral/valuation/illustrative`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Indikativ baholashda xatolik: ${res.statusText}`);
  }
  return res.json();
}

export async function calculateCollateralScenarios(req: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/collateral/scenarios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Sezgirlik ssenariylarini hisoblashda xatolik: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchCollateralChecklist(profile: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/collateral/checklist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Hujjatlar cheklistini yuklashda xatolik: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchCollateralSummary(profile: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/collateral/summary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Garov xulosasini yuklashda xatolik: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchSubsidyPrograms(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/api/v1/subsidies/programs`, { cache: 'no-store' });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Subsidiya dasturlarini yuklashda xatolik: ${res.statusText}`);
  }
  return res.json();
}

export async function matchSubsidyPrograms(req: any): Promise<any[]> {
  const res = await fetch(`${API_BASE}/api/v1/subsidies/match`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Subsidiya mosligini tahlil qilishda xatolik: ${res.statusText}`);
  }
  return res.json();
}

export async function calculatePQ47(req: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/subsidies/calculate/pq47`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `PQ-47 hisob-kitobida xatolik: ${res.statusText}`);
  }
  return res.json();
}

export async function calculatePF82(req: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/subsidies/calculate/pf82`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `PF-82 hisob-kitobida xatolik: ${res.statusText}`);
  }
  return res.json();
}

export async function calculateSubsidyFinancialImpact(req: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/subsidies/financial-impact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    cache: 'no-store'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Subsidiya moliyaviy ta'sirini baholashda xatolik: ${res.statusText}`);
  }
  return res.json();
}
