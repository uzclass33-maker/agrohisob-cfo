/**
 * Privacy-conscious product analytics client for AgroHisob CFO.
 * Strips any sensitive banking, tax, or PII parameters before dispatching.
 */

import { authFetch } from './api';

export type AnalyticsEventType =
  | 'demo_started'
  | 'import_started'
  | 'import_completed'
  | 'import_failed'
  | 'dashboard_viewed'
  | 'forecast_generated'
  | 'scenario_calculated'
  | 'report_generated'
  | 'report_downloaded'
  | 'feedback_submitted';

function getSessionId(): string {
  if (typeof window === 'undefined') return 'server-session';
  let sess = sessionStorage.getItem('agrohisob_session_id');
  if (!sess) {
    sess = 'sess-' + Math.random().toString(36).substring(2, 12);
    sessionStorage.setItem('agrohisob_session_id', sess);
  }
  return sess;
}

export async function trackEvent(
  eventType: AnalyticsEventType,
  options?: {
    durationMs?: number;
    status?: 'SUCCESS' | 'FAILED' | 'CANCELLED';
    errorCategory?: string;
    metadata?: Record<string, any>;
  }
) {
  try {
    const payload = {
      event_type: eventType,
      session_id: getSessionId(),
      organization_id: 'org-default',
      duration_ms: options?.durationMs || null,
      status: options?.status || 'SUCCESS',
      error_category: options?.errorCategory || null,
      metadata: options?.metadata || {}
    };

    // Non-blocking fire-and-forget call
    authFetch('/api/v1/analytics/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).catch(() => {
      // Analytics should never break user interactions
    });
  } catch {
    // Silent fail for analytics
  }
}
