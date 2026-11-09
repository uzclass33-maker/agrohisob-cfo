import { 
  SyntheticScenarioMeta, 
  FinancialSummaryResponse, 
  StressTestRequest, 
  StressTestResponse, 
  CreditReadinessScorecard 
} from './types';
import { supabase } from './supabaseClient';

export const SYNTHETIC_DEMO_SCENARIO_IDS = new Set<string>([
  'scenario-small-farmer',
  'scenario-exporter',
  'scenario-cluster',
  'demo-org-farmer',
  'demo-org-fruit',
  'demo-org-cluster',
  'demo-org-agro-01',
]);

export function isSyntheticDemoScenario(orgId?: string | null): boolean {
  if (!orgId) return false;
  const clean = orgId.trim().toLowerCase();
  return SYNTHETIC_DEMO_SCENARIO_IDS.has(clean) || clean.startsWith('scenario-') || clean.startsWith('demo-');
}

// Clear any obsolete ad-hoc localStorage tokens on module evaluation
if (typeof window !== 'undefined') {
  try {
    const legacy = localStorage.getItem('agrohisob_demo_token');
    if (legacy && (legacy.startsWith('test-token-') || legacy === 'test-token-demo')) {
      localStorage.removeItem('agrohisob_demo_token');
    }
  } catch {}
}

/**
 * Custom error class for API requests providing HTTP status and detailed backend feedback.
 */
export class ApiError extends Error {
  status: number;
  detail: string;
  isAuthError: boolean;
  isForbidden: boolean;
  isSessionExpired: boolean;
  isNetworkError: boolean;

  constructor(message: string, status: number = 500, detail?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail || message;
    this.isAuthError = status === 401;
    this.isForbidden = status === 403;
    const lower = (detail || message || '').toLowerCase();
    this.isSessionExpired = status === 401 && (lower.includes('muddati') || lower.includes('expired') || lower.includes('qayta tizimga'));
    this.isNetworkError = status === 0 || status >= 502;
  }
}

/**
 * Resolves the backend base URL with strict environment preference and robust production fallback.
 * Guarantees that production client environments never silently call localhost.
 */
export function getApiBaseUrl(): string {
  // In browser on local machine, strictly connect to local backend
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://127.0.0.1:8000';
    }
  }

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

export interface DemoSessionResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    full_name: string;
    role: string;
    organizations: string[];
  };
}

/**
 * Creates an authentic, cryptographically-signed Demo CFO session from the backend.
 * Stored safely in localStorage to enable seamless exploration of protected demo features.
 */
export async function loginAsDemoSession(): Promise<DemoSessionResponse> {
  const baseUrl = getApiBaseUrl();
  let res: Response | null = null;
  try {
    res = await fetch(`${baseUrl}/api/v1/demo/session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
  } catch {
    res = null;
  }

  if (!res || !res.ok) {
    try {
      res = await fetch(`${baseUrl}/api/demo/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
    } catch {
      res = null;
    }
  }

  if (!res || !res.ok) {
    throw new Error("Demo sessiya yaratishda xatolik yuz berdi.");
  }

  const data: DemoSessionResponse = await res.json();
  if (typeof window !== 'undefined') {
    localStorage.setItem('agrohisob_demo_access_token', data.access_token);
    localStorage.setItem('agrohisob_demo_user', JSON.stringify(data.user));
    window.dispatchEvent(new Event('agrohisob_auth_change'));
  }
  return data;
}

export function getStoredDemoUser(): { id: string; email: string; full_name: string; role: string; organizations: string[] } | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem('agrohisob_demo_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function logoutDemoSession(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('agrohisob_demo_access_token');
    localStorage.removeItem('agrohisob_demo_user');
    window.dispatchEvent(new Event('agrohisob_auth_change'));
  }
}

/**
 * Resolves authentication token for API calls.
 * 1. Checks active Supabase session. If session is near expiry, proactively refreshes it.
 * 2. Checks active cryptographically-signed Demo Profile session in localStorage.
 * 3. For public synthetic demo scenarios without a valid session, cleanly returns null so requests travel
 *    as clean anonymous queries to approved server-side allowlisted scenarios.
 */
export async function getAuthToken(orgId?: string): Promise<string | null> {
  const isDemo = isSyntheticDemoScenario(orgId);

  // 1. Check Supabase session first
  try {
    const sessionRes = await supabase.auth.getSession();
    const session = sessionRes?.data?.session;
    if (session?.access_token) {
      const nowSec = Math.floor(Date.now() / 1000);
      const expiresAt = session.expires_at || 0;
      // Proactively refresh if session expires within 30 seconds
      if (expiresAt > 0 && expiresAt - nowSec < 30) {
        try {
          const refreshRes = await supabase.auth.refreshSession();
          if (refreshRes?.data?.session?.access_token) {
            return refreshRes.data.session.access_token;
          }
        } catch {
          // If proactive refresh fails, fall through to return current token or null
        }
      }
      return session.access_token;
    }
  } catch {
    // Supabase auth client not configured or session expired
  }

  // 2. Check for active Demo Profile session token in localStorage
  if (typeof window !== 'undefined') {
    try {
      const demoToken = localStorage.getItem('agrohisob_demo_access_token');
      if (demoToken) {
        return demoToken;
      }
    } catch {}
  }

  // 3. For synthetic benchmark scenarios without session, return null for clean anonymous read
  if (isDemo) {
    return null;
  }

  return null;
}

/**
 * Constructs a safe login redirect URL that preserves the user's intended target destination.
 */
export function buildLoginRedirectUrl(currentPath?: string): string {
  if (typeof window === 'undefined') return '/login';
  const target = currentPath || `${window.location.pathname}${window.location.search}`;
  return `/login?redirect=${encodeURIComponent(target)}`;
}

/**
 * Universal authenticated fetch wrapper for AgroHisob CFO APIs.
 * Supports automatic session refresh, single-retry on 401, and clean anonymous fallback for synthetic demo scenarios.
 */
export async function authFetch(
  endpoint: string,
  options: RequestInit = {},
  orgId?: string,
  retryCount: number = 0
): Promise<Response> {
  const baseUrl = getApiBaseUrl();
  const fullUrl = endpoint.startsWith('http://') || endpoint.startsWith('https://')
    ? endpoint
    : `${baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;

  const headers = new Headers(options.headers || {});
  const isDemo = isSyntheticDemoScenario(orgId);

  // Attach token if not already explicitly set
  if (!headers.has('Authorization')) {
    const token = await getAuthToken(orgId);
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  let res: Response;
  try {
    res = await fetch(fullUrl, {
      ...options,
      headers,
    });
  } catch (netErr: any) {
    throw new ApiError(
      "Server bilan aloqa o'rnatilmadi: Tarmoq xatosi yoki server kutish holatida.",
      0,
      netErr?.message
    );
  }

  // Handle 401 Unauthorized with single retry
  if (res.status === 401 && retryCount < 1) {
    // Case 1: If requesting an approved synthetic demo scenario, retry cleanly WITHOUT Authorization header
    if (isDemo && headers.has('Authorization')) {
      const demoHeaders = new Headers(options.headers || {});
      demoHeaders.delete('Authorization');
      return authFetch(endpoint, { ...options, headers: demoHeaders }, orgId, retryCount + 1);
    }

    // Case 2: Protected endpoint - attempt session refresh via Supabase
    try {
      const refreshRes = await supabase.auth.refreshSession();
      const newToken = refreshRes?.data?.session?.access_token;
      if (newToken) {
        const retryHeaders = new Headers(options.headers || {});
        retryHeaders.set('Authorization', `Bearer ${newToken}`);
        return authFetch(endpoint, { ...options, headers: retryHeaders }, orgId, retryCount + 1);
      }
    } catch {
      // Refresh unsuccessful
    }

    // Clean up any stale credentials if refresh fails
    if (typeof window !== 'undefined') {
      try {
        localStorage.removeItem('agrohisob_demo_token');
      } catch {}
    }
  }

  return res;
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
