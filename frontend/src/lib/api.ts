import { 
  SyntheticScenarioMeta, 
  FinancialSummaryResponse, 
  StressTestRequest, 
  StressTestResponse, 
  CreditReadinessScorecard 
} from './types';
import { supabase } from './supabaseClient';

/**
 * Custom error class for API requests providing HTTP status and detailed backend feedback.
 */
export class ApiError extends Error {
  status: number;
  detail: string;
  isAuthError: boolean;
  isForbidden: boolean;

  constructor(message: string, status: number = 500, detail?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail || message;
    this.isAuthError = status === 401;
    this.isForbidden = status === 403;
  }
}

/**
 * Resolves the backend base URL with strict environment preference and robust production fallback.
 * Guarantees that production client environments never silently call localhost.
 */
export function getApiBaseUrl(): string {
  const envUrl = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL;
  if (envUrl && envUrl.trim() !== '') {
    return envUrl.trim().replace(/\/+$/, '');
  }

  // When executing in a remote browser environment (e.g. Vercel deployment),
  // fallback to the live production Render backend instead of localhost.
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return 'https://agrohisob-backend.onrender.com';
    }
  }

  return 'http://127.0.0.1:8000';
}

/**
 * Resolves authentication token for API calls.
 * Checks active Supabase session, evaluator demo token in localStorage,
 * or attaches synthetic demo token for open benchmark scenarios.
 */
export async function getAuthToken(orgId?: string): Promise<string | null> {
  // 1. Check Supabase session first
  try {
    const sessionRes = await supabase.auth.getSession();
    const token = sessionRes?.data?.session?.access_token;
    if (token) return token;
  } catch {
    // Supabase auth client not configured or session expired
  }

  // 2. Check localStorage for evaluator or demo session token
  if (typeof window !== 'undefined') {
    const storedToken = localStorage.getItem('agrohisob_demo_token');
    if (storedToken) return storedToken;
  }

  // 3. For synthetic benchmark scenarios, auto-attach demo token so public evaluators can explore smoothly
  if (!orgId || orgId.startsWith('scenario-') || orgId.startsWith('demo-')) {
    if (orgId === 'scenario-exporter') return 'test-token-cfo-org1';
    if (orgId === 'scenario-small-farmer') return 'test-token-cfo-org2';
    return 'test-token-demo';
  }

  return null;
}

/**
 * Universal authenticated fetch wrapper for AgroHisob CFO APIs.
 */
export async function authFetch(
  endpoint: string,
  options: RequestInit = {},
  orgId?: string
): Promise<Response> {
  const baseUrl = getApiBaseUrl();
  const fullUrl = endpoint.startsWith('http://') || endpoint.startsWith('https://')
    ? endpoint
    : `${baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;

  const headers = new Headers(options.headers || {});

  const token = await getAuthToken(orgId);
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  return fetch(fullUrl, {
    ...options,
    headers,
  });
}

async function handleApiResponse<T = any>(res: Response, fallbackMessage: string): Promise<T> {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const message = errorData.detail || `${fallbackMessage}: ${res.statusText}`;
    throw new ApiError(message, res.status, errorData.detail);
  }
  return res.json();
}

// -------------------------------------------------------------------------
// Scenarios & Financial Core APIs
// -------------------------------------------------------------------------

export async function fetchScenarios(): Promise<SyntheticScenarioMeta[]> {
  const res = await authFetch('/api/scenarios', { cache: 'no-store' });
  return handleApiResponse<SyntheticScenarioMeta[]>(res, 'Failed to fetch scenarios');
}

export async function calculateFinancials(
  scenarioId: string, 
  initialBalance: number = 0
): Promise<FinancialSummaryResponse> {
  const res = await authFetch('/api/financials/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      scenario_id: scenarioId,
      initial_opening_balance: initialBalance
    }),
    cache: 'no-store'
  }, scenarioId);
  return handleApiResponse<FinancialSummaryResponse>(res, 'Financial calculation failed');
}

export async function runStressTest(params: StressTestRequest): Promise<StressTestResponse> {
  const res = await authFetch('/api/financials/stress-test', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
    cache: 'no-store'
  }, params.scenario_id);
  return handleApiResponse<StressTestResponse>(res, 'Stress test execution failed');
}

export async function fetchCreditReadiness(scenarioId: string): Promise<CreditReadinessScorecard> {
  const res = await authFetch(`/api/reports/credit-readiness/${encodeURIComponent(scenarioId)}`, { cache: 'no-store' }, scenarioId);
  return handleApiResponse<CreditReadinessScorecard>(res, 'Failed to fetch credit report');
}

export async function fetchLoanSchedule(params: {
  principal: number;
  annual_interest_rate_pct: number;
  start_date: string;
  term_months: number;
  repayment_type?: 'ANNUITY' | 'EQUAL_PRINCIPAL';
  grace_period_months?: number;
}): Promise<any> {
  const res = await authFetch('/api/v1/finance/loans/schedule', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...params,
      repayment_type: params.repayment_type || 'ANNUITY',
      grace_period_months: params.grace_period_months || 0
    }),
    cache: 'no-store'
  });
  return handleApiResponse(res, 'Failed to calculate loan schedule');
}

export async function calculateDSCRAPI(params: {
  operating_cash_inflows: number;
  operating_cash_outflows: number;
  debt_service_principal: number;
  debt_service_interest: number;
}): Promise<any> {
  const res = await authFetch('/api/v1/finance/dscr/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
    cache: 'no-store'
  });
  return handleApiResponse(res, 'Failed to calculate DSCR');
}

// -------------------------------------------------------------------------
// Smart Financial Data Import APIs
// -------------------------------------------------------------------------

export async function uploadImportFile(
  file: File,
  documentType: 'E_FAKTURA' | 'BANK_STATEMENT',
  organizationId: string = 'demo-org-agro-01'
): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('document_type', documentType);
  formData.append('organization_id', organizationId);

  const res = await authFetch('/api/v1/imports/upload', {
    method: 'POST',
    body: formData,
    cache: 'no-store'
  }, organizationId);
  return handleApiResponse(res, 'Upload failed');
}

export async function fetchBatchPreview(batchId: string): Promise<any> {
  const res = await authFetch(`/api/v1/imports/${encodeURIComponent(batchId)}/preview`, { cache: 'no-store' });
  return handleApiResponse(res, 'Failed to fetch preview');
}

export async function updateBatchMapping(batchId: string, mappings: Record<string, string>): Promise<any> {
  const res = await authFetch(`/api/v1/imports/${encodeURIComponent(batchId)}/mapping`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mappings }),
    cache: 'no-store'
  });
  return handleApiResponse(res, 'Mapping update failed');
}

export async function overrideBatchRow(batchId: string, rowId: string, override: any): Promise<any> {
  const res = await authFetch(`/api/v1/imports/${encodeURIComponent(batchId)}/rows/${encodeURIComponent(rowId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(override),
    cache: 'no-store'
  });
  return handleApiResponse(res, 'Row override failed');
}

export async function commitImportBatch(batchId: string, organizationId: string = 'demo-org-agro-01'): Promise<any> {
  const res = await authFetch(`/api/v1/imports/${encodeURIComponent(batchId)}/commit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ batch_id: batchId, organization_id: organizationId }),
    cache: 'no-store'
  }, organizationId);
  return handleApiResponse(res, 'Commit failed');
}

export async function fetchImportHistory(organizationId: string = 'demo-org-agro-01'): Promise<any> {
  const res = await authFetch(
    `/api/v1/imports/history/list?organization_id=${encodeURIComponent(organizationId)}`,
    { cache: 'no-store' },
    organizationId
  );
  return handleApiResponse(res, 'Failed to fetch history');
}

// -------------------------------------------------------------------------
// AI-CFO Financial Dashboard Client APIs
// -------------------------------------------------------------------------

export async function fetchDashboardOverview(organizationId: string, period: string = '2026'): Promise<any> {
  const res = await authFetch(
    `/api/v1/dashboard/overview?organization_id=${encodeURIComponent(organizationId)}&reporting_period=${encodeURIComponent(period)}`,
    { cache: 'no-store' },
    organizationId
  );
  return handleApiResponse(res, 'Failed to fetch overview');
}

export async function fetchDashboardCashFlow(organizationId: string, period: string = '2026'): Promise<any> {
  const res = await authFetch(
    `/api/v1/dashboard/cashflow?organization_id=${encodeURIComponent(organizationId)}&reporting_period=${encodeURIComponent(period)}`,
    { cache: 'no-store' },
    organizationId
  );
  return handleApiResponse(res, 'Failed to fetch cashflow');
}

export async function fetchDashboardForecast(organizationId: string, fiscalYear: number = 2026): Promise<any> {
  const res = await authFetch(
    `/api/v1/dashboard/forecast?organization_id=${encodeURIComponent(organizationId)}&fiscal_year=${fiscalYear}`,
    { cache: 'no-store' },
    organizationId
  );
  return handleApiResponse(res, 'Failed to fetch forecast');
}

export async function fetchDashboardDebt(organizationId: string): Promise<any> {
  const res = await authFetch(
    `/api/v1/dashboard/debt?organization_id=${encodeURIComponent(organizationId)}`,
    { cache: 'no-store' },
    organizationId
  );
  return handleApiResponse(res, 'Failed to fetch debt analytics');
}

export async function fetchDashboardRisks(organizationId: string): Promise<any> {
  const res = await authFetch(
    `/api/v1/dashboard/risks?organization_id=${encodeURIComponent(organizationId)}`,
    { cache: 'no-store' },
    organizationId
  );
  return handleApiResponse(res, 'Failed to fetch risk monitor');
}

export async function simulateDashboardScenario(params: {
  organization_id: string;
  scenario_type?: string;
  revenue_change_pct: number;
  cost_change_pct: number;
  collection_delay_months: number;
  interest_rate_delta_pct: number;
}): Promise<any> {
  const res = await authFetch(
    '/api/v1/dashboard/scenarios',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
      cache: 'no-store'
    },
    params.organization_id
  );
  return handleApiResponse(res, 'Failed to simulate scenario');
}

export async function fetchAIInsights(organizationId: string, requestLlm: boolean = false): Promise<any> {
  const res = await authFetch(
    `/api/v1/insights?organization_id=${encodeURIComponent(organizationId)}&request_llm=${requestLlm}`,
    { cache: 'no-store' },
    organizationId
  );
  return handleApiResponse(res, 'Failed to fetch AI insights');
}

export async function explainInsightAPI(params: {
  organization_id: string;
  insight_id?: string;
  request_llm?: boolean;
}): Promise<any> {
  const res = await authFetch(
    '/api/v1/insights/explain',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
      cache: 'no-store'
    },
    params.organization_id
  );
  return handleApiResponse(res, 'Failed to explain insight');
}

// -------------------------------------------------------------------------
// Credit Dossier & Reporting Client APIs
// -------------------------------------------------------------------------

export async function validateCreditProfileAPI(profile: any): Promise<{
  is_valid: boolean;
  errors: string[];
  credit_profile: any;
}> {
  const res = await authFetch(
    '/api/v1/reports/credit/profile',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
      cache: 'no-store'
    },
    profile.organization_id
  );
  return handleApiResponse(res, 'Kredit profilini tekshirishda xatolik yuz berdi');
}

export async function fetchDocumentReadinessChecklist(organizationId: string): Promise<any> {
  const res = await authFetch(
    `/api/v1/reports/credit/validate?organization_id=${encodeURIComponent(organizationId)}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ organization_id: organizationId }),
      cache: 'no-store'
    },
    organizationId
  );
  return handleApiResponse(res, "Hujjatlar ro'yxatini yuklashda xatolik yuz berdi");
}

export async function previewCreditDossier(organizationId: string, customProfile?: any): Promise<any> {
  const res = await authFetch(
    '/api/v1/reports/credit/preview',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        organization_id: organizationId,
        fiscal_year: 2026,
        credit_profile: customProfile
      }),
      cache: 'no-store'
    },
    organizationId
  );
  return handleApiResponse(res, "Kredit dosye dastlabki ko'rinishini shakllantirishda xatolik");
}

export async function generateCreditDossier(organizationId: string, customProfile?: any): Promise<any> {
  const res = await authFetch(
    '/api/v1/reports/credit/generate',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        organization_id: organizationId,
        fiscal_year: 2026,
        credit_profile: customProfile
      }),
      cache: 'no-store'
    },
    organizationId
  );
  return handleApiResponse(res, 'Hisobot fayllarini generatsiya qilishda xatolik yuz berdi');
}

export async function fetchReportHistory(organizationId?: string): Promise<any[]> {
  const url = organizationId 
    ? `/api/v1/reports/history?organization_id=${encodeURIComponent(organizationId)}`
    : '/api/v1/reports/history';
  const res = await authFetch(url, { cache: 'no-store' }, organizationId);
  return handleApiResponse<any[]>(res, 'Hisobotlar tarixini yuklashda xatolik');
}

export function getFullDownloadUrl(pathUrl: string): string {
  if (pathUrl.startsWith('http://') || pathUrl.startsWith('https://')) {
    return pathUrl;
  }
  const base = getApiBaseUrl();
  return `${base}${pathUrl.startsWith('/') ? '' : '/'}${pathUrl}`;
}

// -------------------------------------------------------------------------
// Collateral, Subsidies & Regulatory Client APIs
// -------------------------------------------------------------------------

export async function fetchRegulatorySources(verifiedOnly: boolean = true): Promise<any[]> {
  const res = await authFetch(`/api/v1/regulatory/sources?verified_only=${verifiedOnly}`, { cache: 'no-store' });
  return handleApiResponse<any[]>(res, "Me'yoriy hujjatlarni yuklashda xatolik");
}

export async function fetchRegulatorySource(code: string): Promise<any> {
  const res = await authFetch(`/api/v1/regulatory/sources/${encodeURIComponent(code)}`, { cache: 'no-store' });
  return handleApiResponse(res, "Me'yoriy hujjat ma'lumotlarini olishda xatolik");
}

export async function fetchDefaultCollateralProfile(organizationId: string = 'scenario-small-farmer'): Promise<any> {
  const res = await authFetch(`/api/v1/collateral/profile/default?organization_id=${encodeURIComponent(organizationId)}`, { cache: 'no-store' }, organizationId);
  return handleApiResponse(res, 'Standart garov profilini yuklashda xatolik');
}

export async function screenCollateralEligibility(profile: any): Promise<any> {
  const res = await authFetch('/api/v1/collateral/eligibility', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
    cache: 'no-store'
  }, profile.organization_id);
  return handleApiResponse(res, 'VMQ-613 huquqiy tahlilida xatolik');
}

export async function calculateCollateralValuation(req: any): Promise<any> {
  const res = await authFetch('/api/v1/collateral/valuation/illustrative', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    cache: 'no-store'
  }, req.organization_id);
  return handleApiResponse(res, 'Indikativ baholashda xatolik');
}

export async function calculateCollateralScenarios(req: any): Promise<any> {
  const res = await authFetch('/api/v1/collateral/scenarios', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    cache: 'no-store'
  }, req.organization_id);
  return handleApiResponse(res, 'Sezgirlik ssenariylarini hisoblashda xatolik');
}

export async function fetchCollateralChecklist(profile: any): Promise<any> {
  const res = await authFetch('/api/v1/collateral/checklist', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
    cache: 'no-store'
  }, profile.organization_id);
  return handleApiResponse(res, 'Hujjatlar cheklistini yuklashda xatolik');
}

export async function fetchCollateralSummary(profile: any): Promise<any> {
  const res = await authFetch('/api/v1/collateral/summary', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
    cache: 'no-store'
  }, profile.organization_id);
  return handleApiResponse(res, 'Garov xulosasini yuklashda xatolik');
}

export async function fetchSubsidyPrograms(): Promise<any[]> {
  const res = await authFetch('/api/v1/subsidies/programs', { cache: 'no-store' });
  return handleApiResponse<any[]>(res, 'Subsidiya dasturlarini yuklashda xatolik');
}

export async function matchSubsidyPrograms(req: any): Promise<any[]> {
  const res = await authFetch('/api/v1/subsidies/match', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    cache: 'no-store'
  }, req.organization_id);
  return handleApiResponse<any[]>(res, 'Subsidiya mosligini tahlil qilishda xatolik');
}

export async function calculatePQ47(req: any): Promise<any> {
  const res = await authFetch('/api/v1/subsidies/calculate/pq47', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    cache: 'no-store'
  });
  return handleApiResponse(res, 'PQ-47 hisob-kitobida xatolik');
}

export async function calculatePF82(req: any): Promise<any> {
  const res = await authFetch('/api/v1/subsidies/calculate/pf82', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    cache: 'no-store'
  });
  return handleApiResponse(res, 'PF-82 hisob-kitobida xatolik');
}

export async function calculateSubsidyFinancialImpact(req: any): Promise<any> {
  const res = await authFetch('/api/v1/subsidies/financial-impact', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    cache: 'no-store'
  }, req.organization_id);
  return handleApiResponse(res, "Subsidiya moliyaviy ta'sirini baholashda xatolik");
}
