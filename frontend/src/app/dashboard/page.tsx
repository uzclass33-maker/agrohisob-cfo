'use client';

import React, { useEffect, useState, useTransition, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { 
  fetchScenarios,
  fetchDashboardOverview,
  fetchDashboardCashFlow,
  fetchDashboardForecast,
  fetchDashboardDebt,
  fetchDashboardRisks,
  simulateDashboardScenario,
  fetchAIInsights,
  explainInsightAPI
} from '@/lib/api';
import { 
  SyntheticScenarioMeta,
  DashboardOverviewResponse,
  DashboardCashFlowResponse,
  DashboardForecastResponse,
  DashboardDebtResponse,
  DashboardRisksResponse,
  AIInsightsResponse,
  ScenarioComparisonResponse,
  FinancialInsight,
  DashboardRiskItem
} from '@/lib/types';
import { formatUZS, formatCompactUZS } from '@/lib/formatters';
import CashFlowChart from '@/components/CashFlowChart';
import { 
  Building2, Wheat, Truck, CheckCircle2, AlertTriangle, 
  ArrowUpRight, ArrowDownRight, RefreshCw, Sliders, ShieldCheck, 
  DollarSign, Calendar, AlertOctagon, TrendingUp, TrendingDown, Info,
  BrainCircuit, Sparkles, ShieldAlert, Cpu, BarChart3, Layers, 
  FileText, ArrowRight, Gauge, Activity, Database
} from 'lucide-react';

type TabType = 'overview' | 'cashflow' | 'forecast' | 'debt' | 'risks' | 'scenarios' | 'ai_cfo';

function DashboardContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  // Active Organization & Tab State
  const [scenarios, setScenarios] = useState<SyntheticScenarioMeta[]>([]);
  const [selectedOrgId, setSelectedOrgId] = useState<string>(
    searchParams.get('scenario') || 'scenario-small-farmer'
  );
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  // Backend Data States
  const [overview, setOverview] = useState<DashboardOverviewResponse | null>(null);
  const [cashflow, setCashflow] = useState<DashboardCashFlowResponse | null>(null);
  const [forecast, setForecast] = useState<DashboardForecastResponse | null>(null);
  const [debt, setDebt] = useState<DashboardDebtResponse | null>(null);
  const [risks, setRisks] = useState<DashboardRisksResponse | null>(null);
  const [aiInsights, setAiInsights] = useState<AIInsightsResponse | null>(null);

  // Scenario Simulation State
  const [scenarioPreset, setScenarioPreset] = useState<'BASE' | 'OPTIMISTIC' | 'PESSIMISTIC' | 'CUSTOM'>('BASE');
  const [revenueChange, setRevenueChange] = useState<number>(0);
  const [costChange, setCostChange] = useState<number>(0);
  const [delayMonths, setDelayMonths] = useState<number>(0);
  const [interestDelta, setInterestDelta] = useState<number>(0);
  const [simulationResult, setSimulationResult] = useState<ScenarioComparisonResponse | null>(null);
  const [simulating, setSimulating] = useState<boolean>(false);

  // Status & Loading
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [llmRequested, setLlmRequested] = useState<boolean>(false);
  const [llmLoading, setLlmLoading] = useState<boolean>(false);

  // Cashflow category filter
  const [cfFilter, setCfFilter] = useState<'ALL' | 'INFLOWS' | 'OUTFLOWS'>('ALL');

  // Load scenarios metadata
  useEffect(() => {
    async function loadScenarios() {
      try {
        const list = await fetchScenarios();
        setScenarios(list);
      } catch (e) {
        console.error("Scenarios load error:", e);
      }
    }
    loadScenarios();
  }, []);

  // Sync with searchParams
  useEffect(() => {
    const fromParam = searchParams.get('scenario');
    if (fromParam && fromParam !== selectedOrgId) {
      setSelectedOrgId(fromParam);
    }
  }, [searchParams]);

  // Main Data Fetcher
  const loadDashboardData = async (orgId: string) => {
    try {
      setLoading(true);
      setError(null);

      const [ovRes, cfRes, fcRes, dbRes, rkRes, aiRes] = await Promise.all([
        fetchDashboardOverview(orgId),
        fetchDashboardCashFlow(orgId),
        fetchDashboardForecast(orgId),
        fetchDashboardDebt(orgId),
        fetchDashboardRisks(orgId),
        fetchAIInsights(orgId, false)
      ]);

      setOverview(ovRes);
      setCashflow(cfRes);
      setForecast(fcRes);
      setDebt(dbRes);
      setRisks(rkRes);
      setAiInsights(aiRes);

      // Trigger initial base scenario comparison
      const simRes = await simulateDashboardScenario({
        organization_id: orgId,
        scenario_type: 'BASE',
        revenue_change_pct: 0,
        cost_change_pct: 0,
        collection_delay_months: 0,
        interest_rate_delta_pct: 0
      });
      setSimulationResult(simRes);
      setScenarioPreset('BASE');
      setRevenueChange(0);
      setCostChange(0);
      setDelayMonths(0);
      setInterestDelta(0);

    } catch (err: any) {
      console.error("Dashboard data load error:", err);
      setError(err.message || "Boshqaruv paneli ma'lumotlarini yuklashda xatolik yuz berdi.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedOrgId) {
      loadDashboardData(selectedOrgId);
    }
  }, [selectedOrgId]);

  // Run Backend Scenario Recalculation
  const handleRunSimulation = async (
    type: 'BASE' | 'OPTIMISTIC' | 'PESSIMISTIC' | 'CUSTOM',
    rev: number,
    cost: number,
    delay: number,
    rate: number
  ) => {
    try {
      setSimulating(true);
      const res = await simulateDashboardScenario({
        organization_id: selectedOrgId,
        scenario_type: type,
        revenue_change_pct: rev,
        cost_change_pct: cost,
        collection_delay_months: delay,
        interest_rate_delta_pct: rate
      });
      setSimulationResult(res);
    } catch (e: any) {
      console.error("Simulation error:", e);
    } finally {
      setSimulating(false);
    }
  };

  const handleApplyPreset = (preset: 'BASE' | 'OPTIMISTIC' | 'PESSIMISTIC') => {
    setScenarioPreset(preset);
    if (preset === 'BASE') {
      setRevenueChange(0);
      setCostChange(0);
      setDelayMonths(0);
      setInterestDelta(0);
      handleRunSimulation('BASE', 0, 0, 0, 0);
    } else if (preset === 'OPTIMISTIC') {
      setRevenueChange(20);
      setCostChange(-10);
      setDelayMonths(0);
      setInterestDelta(0);
      handleRunSimulation('OPTIMISTIC', 20, -10, 0, 0);
    } else if (preset === 'PESSIMISTIC') {
      setRevenueChange(-20);
      setCostChange(15);
      setDelayMonths(1);
      setInterestDelta(2);
      handleRunSimulation('PESSIMISTIC', -20, 15, 1, 2);
    }
  };

  const handleOrgChange = (id: string) => {
    setSelectedOrgId(id);
    router.push(`/dashboard?scenario=${id}`);
  };

  // LLM Explanation Request with Privacy Check
  const handleToggleLLM = async () => {
    if (!llmRequested) {
      try {
        setLlmLoading(true);
        const res = await fetchAIInsights(selectedOrgId, true);
        setAiInsights(res);
        setLlmRequested(true);
      } catch (e: any) {
        console.error("LLM Insight error:", e);
      } finally {
        setLlmLoading(false);
      }
    } else {
      setLlmRequested(false);
      // Revert to deterministic rule engine
      if (selectedOrgId) {
        const res = await fetchAIInsights(selectedOrgId, false);
        setAiInsights(res);
      }
    }
  };

  const getDscrBadge = (rating: string, dscr: number | null) => {
    if (dscr === null) {
      return (
        <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-slate-100 text-slate-700 border border-slate-200">
          Qarz mavjud emas
        </span>
      );
    }
    if (dscr >= 1.5) {
      return (
        <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
          {dscr.toFixed(2)}x — Mustahkam (DSCR &ge; 1.50)
        </span>
      );
    }
    if (dscr >= 1.2) {
      return (
        <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-sky-100 text-sky-800 border border-sky-200">
          {dscr.toFixed(2)}x — Mo'tadil (1.20 - 1.50)
        </span>
      );
    }
    if (dscr >= 1.0) {
      return (
        <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200">
          {dscr.toFixed(2)}x — Cheklangan (1.00 - 1.20)
        </span>
      );
    }
    return (
      <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-rose-100 text-rose-800 border border-rose-200">
        {dscr.toFixed(2)}x — Kritik Xavfli (DSCR &lt; 1.00)
      </span>
    );
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-rose-100 text-rose-800 border border-rose-200">KRITIK</span>;
      case 'HIGH':
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-orange-100 text-orange-800 border border-orange-200">YUQORI</span>;
      case 'MEDIUM':
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200">O'RTA</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-blue-100 text-blue-800 border border-blue-200">MA'LUMOT</span>;
    }
  };

  return (
    <div className="py-8 bg-slate-50 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        
        {/* Top Control Bar: Organization Switcher & Meta */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-emerald-50 text-emerald-700 rounded-xl border border-emerald-100">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Korxona:</span>
                {overview && (
                  <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${
                    overview.data_source === 'BANK_STATEMENT_IMPORT' 
                      ? 'bg-purple-50 text-purple-700 border-purple-200' 
                      : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  }`}>
                    {overview.data_source === 'BANK_STATEMENT_IMPORT' ? 'Bank Ko\'chirmasi (Haqiqiy)' : 'Sintetik Benchmark'}
                  </span>
                )}
              </div>
              <h2 className="text-lg font-bold text-slate-900">
                {overview ? overview.organization_name : "Yuklanmoqda..."}
              </h2>
            </div>
          </div>

          {/* Org Selector Buttons */}
          <div className="flex items-center space-x-1.5 p-1 bg-slate-100 rounded-xl">
            <button
              onClick={() => handleOrgChange('scenario-small-farmer')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                selectedOrgId.includes('farmer')
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Fermer (65 ga)
            </button>
            <button
              onClick={() => handleOrgChange('scenario-exporter')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                selectedOrgId.includes('exporter')
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Eksportyor (120 ga)
            </button>
            <button
              onClick={() => handleOrgChange('scenario-cluster')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                selectedOrgId.includes('cluster')
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Klaster (2 500 ga)
            </button>
          </div>

          {/* Quick Refresh */}
          <div className="flex items-center space-x-3 text-xs text-slate-500">
            <span>Valyuta: <strong>UZS</strong></span>
            <span>Davr: <strong>2026</strong></span>
            <button
              onClick={() => loadDashboardData(selectedOrgId)}
              disabled={loading}
              className="p-2 text-slate-600 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors border border-slate-200"
              title="Qayta hisoblash"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-emerald-600' : ''}`} />
            </button>
          </div>
        </div>

        {/* 7-Module Navigation Tabs */}
        <div className="bg-white rounded-xl border border-slate-200 p-1.5 shadow-sm overflow-x-auto">
          <div className="flex items-center space-x-1 min-w-[760px]">
            {[
              { id: 'overview', label: '1. Ijroiya Xulosa', icon: Activity },
              { id: 'cashflow', label: '2. Kassa Oqimlari', icon: DollarSign },
              { id: 'forecast', label: '3. 12 Oylik Prognoz', icon: Calendar },
              { id: 'debt', label: '4. Qarz & DSCR', icon: Gauge },
              { id: 'risks', label: '5. Xavflar Monitori', icon: ShieldAlert, badge: risks?.critical_count },
              { id: 'scenarios', label: '6. Ssenariylar Simulyatsiyasi', icon: Sliders },
              { id: 'ai_cfo', label: '7. AI-CFO Xulosalari', icon: BrainCircuit, highlight: true },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabType)}
                  className={`flex items-center space-x-2 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                    isActive
                      ? tab.highlight 
                        ? 'bg-purple-600 text-white shadow-sm' 
                        : 'bg-emerald-600 text-white shadow-sm'
                      : tab.highlight
                        ? 'text-purple-700 hover:bg-purple-50'
                        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                  {tab.badge !== undefined && tab.badge > 0 && (
                    <span className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold ${
                      isActive ? 'bg-white text-rose-600' : 'bg-rose-100 text-rose-700'
                    }`}>
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl flex items-center space-x-3 text-sm">
            <AlertOctagon className="w-5 h-5 flex-shrink-0 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        {/* Loading Overlay State */}
        {loading && (
          <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <RefreshCw className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
            <p className="text-sm font-semibold text-slate-700">
              Moliyaviy hisob-kitoblar aniq hisoblanmoqda (Financial Engine v4.0.0)...
            </p>
          </div>
        )}

        {/* =========================================================================
            MODULE 1: EXECUTIVE FINANCIAL OVERVIEW
        ========================================================================== */}
        {!loading && activeTab === 'overview' && overview && (
          <div className="space-y-6">
            {/* Top KPI Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Card 1: Total Inflow */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
                <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
                  <span>Yalpi Pul Tushumlari</span>
                  <ArrowUpRight className="w-4 h-4 text-emerald-500" />
                </div>
                <div className="text-2xl font-bold text-slate-900">
                  {formatCompactUZS(overview.kpis.total_inflows)}
                </div>
                <div className="text-xs text-slate-500 flex items-center justify-between border-t border-slate-100 pt-2">
                  <span>Aniq summa:</span>
                  <span className="font-semibold text-emerald-700">{formatUZS(overview.kpis.total_inflows)}</span>
                </div>
              </div>

              {/* Card 2: Total Outflow */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
                <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
                  <span>Jami Pul Chiqimlari</span>
                  <ArrowDownRight className="w-4 h-4 text-rose-500" />
                </div>
                <div className="text-2xl font-bold text-slate-900">
                  {formatCompactUZS(overview.kpis.total_outflows)}
                </div>
                <div className="text-xs text-slate-500 flex items-center justify-between border-t border-slate-100 pt-2">
                  <span>Shu jumladan kredit:</span>
                  <span className="font-semibold text-rose-700">{formatCompactUZS(overview.kpis.debt_service)}</span>
                </div>
              </div>

              {/* Card 3: Net Cash Flow */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
                <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
                  <span>Sof Pul Oqimi (Net Cash)</span>
                  {overview.kpis.net_cash_flow >= 0 ? (
                    <TrendingUp className="w-4 h-4 text-emerald-500" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-rose-500" />
                  )}
                </div>
                <div className={`text-2xl font-bold ${overview.kpis.net_cash_flow >= 0 ? 'text-emerald-700' : 'text-rose-700'}`}>
                  {formatCompactUZS(overview.kpis.net_cash_flow)}
                </div>
                <div className="text-xs text-slate-500 flex items-center justify-between border-t border-slate-100 pt-2">
                  <span>Yakuniy qoldiq:</span>
                  <span className="font-bold text-slate-900">{formatCompactUZS(overview.kpis.closing_balance)}</span>
                </div>
              </div>

              {/* Card 4: DSCR Ratio */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
                <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
                  <span>DSCR Qoplash Nisbati</span>
                  <Gauge className="w-4 h-4 text-sky-500" />
                </div>
                <div className="text-2xl font-bold text-slate-900">
                  {overview.kpis.dscr !== null ? `${overview.kpis.dscr.toFixed(2)}x` : "Qarzsiz"}
                </div>
                <div className="text-xs border-t border-slate-100 pt-2">
                  {getDscrBadge(overview.kpis.dscr_rating, overview.kpis.dscr)}
                </div>
              </div>
            </div>

            {/* Secondary KPIs Row */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-3">
                <div className="p-3 bg-amber-50 text-amber-600 rounded-xl">
                  <Calendar className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-xs text-slate-500 font-semibold">Eng Past Kassa Nuqtasi</div>
                  <div className="text-base font-bold text-slate-900">
                    {formatUZS(overview.kpis.projected_min_balance)}
                  </div>
                  <div className="text-xs text-amber-700 font-medium">
                    Eng og'ir oy: <strong>{overview.kpis.min_balance_month}</strong>
                  </div>
                </div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-3">
                <div className="p-3 bg-rose-50 text-rose-600 rounded-xl">
                  <AlertOctagon className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-xs text-slate-500 font-semibold">Taqchillik Oylari</div>
                  <div className="text-base font-bold text-slate-900">
                    {overview.kpis.months_in_deficit} oy
                  </div>
                  <div className="text-xs text-slate-500">
                    {overview.kpis.months_in_deficit > 0 ? "Kassa uzilishi xavfi mavjud" : "Kassa uzilishi aniqlanmadi"}
                  </div>
                </div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-3">
                <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-xs text-slate-500 font-semibold">Hisoblash Dvigateli</div>
                  <div className="text-base font-bold text-slate-900">
                    Deterministik v{overview.calculation_version}
                  </div>
                  <div className="text-xs text-emerald-700 font-medium">
                    100% matematik bog'liqlik tasdiqlangan
                  </div>
                </div>
              </div>
            </div>

            {/* Visual Cash Flow Chart */}
            {cashflow && (
              <CashFlowChart 
                data={cashflow.monthly_data.map(m => ({
                  month_number: m.month_number,
                  month_name: m.month_name,
                  opening_balance: m.opening_balance,
                  total_inflows: m.total_inflows,
                  total_outflows: m.total_outflows,
                  net_cash_flow: m.net_cash_flow,
                  closing_balance: m.closing_balance,
                  debt_service: 0,
                  dscr: null,
                  is_deficit: m.is_deficit,
                  inflows_breakdown: {},
                  outflows_breakdown: {}
                }))}
                title="12 Oylik Kassa Oqimlari va Yakuniy Balans Dinamikasi (2026)"
              />
            )}
          </div>
        )}

        {/* =========================================================================
            MODULE 2: CASH-FLOW INTELLIGENCE
        ========================================================================== */}
        {!loading && activeTab === 'cashflow' && cashflow && (
          <div className="space-y-6">
            {/* Category Distribution Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Inflows Breakdown */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div className="flex items-center space-x-2">
                    <ArrowUpRight className="w-5 h-5 text-emerald-600" />
                    <h3 className="font-bold text-slate-900 text-sm">Tushumlar Toifasi Taqsimoti</h3>
                  </div>
                  <span className="text-xs font-bold text-emerald-700">
                    {formatUZS(cashflow.total_inflows)}
                  </span>
                </div>
                <div className="space-y-2.5">
                  {Object.entries(cashflow.inflow_by_category).map(([cat, amount]) => {
                    const pct = cashflow.total_inflows > 0 ? (amount / cashflow.total_inflows) * 100 : 0;
                    return (
                      <div key={cat} className="space-y-1">
                        <div className="flex justify-between text-xs font-medium">
                          <span className="text-slate-700">{cat}</span>
                          <span className="text-slate-900 font-bold">{formatUZS(amount)} ({pct.toFixed(1)}%)</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2">
                          <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${pct}%` }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Outflows Breakdown */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div className="flex items-center space-x-2">
                    <ArrowDownRight className="w-5 h-5 text-rose-600" />
                    <h3 className="font-bold text-slate-900 text-sm">Chiqimlar Toifasi Taqsimoti</h3>
                  </div>
                  <span className="text-xs font-bold text-rose-700">
                    {formatUZS(cashflow.total_outflows)}
                  </span>
                </div>
                <div className="space-y-2.5">
                  {Object.entries(cashflow.outflow_by_category).map(([cat, amount]) => {
                    const pct = cashflow.total_outflows > 0 ? (amount / cashflow.total_outflows) * 100 : 0;
                    return (
                      <div key={cat} className="space-y-1">
                        <div className="flex justify-between text-xs font-medium">
                          <span className="text-slate-700">{cat}</span>
                          <span className="text-slate-900 font-bold">{formatUZS(amount)} ({pct.toFixed(1)}%)</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2">
                          <div className="bg-rose-500 h-2 rounded-full" style={{ width: `${pct}%` }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Monthly Roll-Forward Detailed Table */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-4 border-b border-slate-100 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Oylik Kassa Oqimlari Tafsiloti (Roll-Forward Reconciliation)</h3>
                  <p className="text-xs text-slate-500">Boshlang'ich qoldiq + Tushumlar - Chiqimlar = Yakuniy qoldiq</p>
                </div>
                <span className="px-2.5 py-1 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold">
                  100% Rekonsilyatsiya Qilingan
                </span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider border-b border-slate-200">
                    <tr>
                      <th className="py-3 px-4">Oy</th>
                      <th className="py-3 px-4 text-right">Boshlang'ich Qoldiq</th>
                      <th className="py-3 px-4 text-right text-emerald-700">Yalpi Tushum</th>
                      <th className="py-3 px-4 text-right text-rose-700">Jami Chiqim</th>
                      <th className="py-3 px-4 text-right">Sof Kassa Oqimi</th>
                      <th className="py-3 px-4 text-right font-bold">Yakuniy Qoldiq</th>
                      <th className="py-3 px-4 text-center">Holat</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {cashflow.monthly_data.map((m) => (
                      <tr key={m.month_number} className={`hover:bg-slate-50/80 ${m.is_deficit ? 'bg-rose-50/40' : ''}`}>
                        <td className="py-3 px-4 font-bold text-slate-900">
                          {m.month_name}
                        </td>
                        <td className="py-3 px-4 text-right text-slate-600">
                          {formatUZS(m.opening_balance)}
                        </td>
                        <td className="py-3 px-4 text-right text-emerald-700 font-semibold">
                          +{formatUZS(m.total_inflows)}
                        </td>
                        <td className="py-3 px-4 text-right text-rose-700 font-semibold">
                          -{formatUZS(m.total_outflows)}
                        </td>
                        <td className={`py-3 px-4 text-right font-bold ${m.net_cash_flow >= 0 ? 'text-emerald-700' : 'text-rose-700'}`}>
                          {m.net_cash_flow >= 0 ? '+' : ''}{formatUZS(m.net_cash_flow)}
                        </td>
                        <td className={`py-3 px-4 text-right font-bold ${m.closing_balance < 0 ? 'text-rose-700' : 'text-slate-900'}`}>
                          {formatUZS(m.closing_balance)}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {m.is_deficit ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
                              Taqchillik
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                              Ijobiy
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            MODULE 3: TWELVE-MONTH SEASONAL FORECASTING DASHBOARD
        ========================================================================== */}
        {!loading && activeTab === 'forecast' && forecast && (
          <div className="space-y-6">
            {/* Forecast Assumptions & Seasonal Summary Card */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left 2 Cols: Assumptions Panel */}
              <div className="lg:col-span-2 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div className="flex items-center space-x-2">
                    <Wheat className="w-5 h-5 text-amber-600" />
                    <h3 className="text-sm font-bold text-slate-900">Agrar Prognoz Farazlari & Hosil Parametrlari</h3>
                  </div>
                  <span className="text-xs text-slate-500 font-medium">Model v{forecast.model_version}</span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                  <div className="p-3 bg-slate-50 rounded-xl">
                    <span className="text-slate-500 block">Asosiy ekin turi:</span>
                    <strong className="text-slate-900 text-sm block mt-1">{forecast.assumptions.crop_type}</strong>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-xl">
                    <span className="text-slate-500 block">Ekin maydoni:</span>
                    <strong className="text-slate-900 text-sm block mt-1">{forecast.assumptions.land_hectares} gektar</strong>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-xl">
                    <span className="text-slate-500 block">Tuproq boniteti:</span>
                    <strong className="text-slate-900 text-sm block mt-1">{forecast.assumptions.soil_bonitet} ball</strong>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-xl">
                    <span className="text-slate-500 block">Tomchilatib sug'orish:</span>
                    <strong className="text-slate-900 text-sm block mt-1">
                      {forecast.assumptions.has_drip_irrigation ? "Mavjud (PQ-47)" : "Yo'q"}
                    </strong>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-xl">
                    <span className="text-slate-500 block">Tushum kechikishi:</span>
                    <strong className="text-slate-900 text-sm block mt-1">{forecast.assumptions.collection_timing_days} kun</strong>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-xl">
                    <span className="text-slate-500 block">Xarajatlar inflyatsiyasi:</span>
                    <strong className="text-slate-900 text-sm block mt-1">+{forecast.assumptions.input_inflation_rate_pct}%</strong>
                  </div>
                </div>

                <div className="p-3 bg-blue-50 border border-blue-100 rounded-xl text-xs text-blue-800 space-y-1">
                  <div className="font-bold flex items-center space-x-1.5">
                    <Info className="w-4 h-4 text-blue-600" />
                    <span>Mavsumiylik qoidasi (Agrar Tsikl):</span>
                  </div>
                  <p>
                    Bahor oylarida (Mart-May) urug'lik, o'g'it va yoqilg'i uchun kassa chiqimlari 60-70% ni tashkil etadi. Asosiy hosil tushumi esa yoz oxiri va kuzda (Iyun-Noyabr) shakllanadi.
                  </p>
                </div>
              </div>

              {/* Right Col: Seasonality KPI summary */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-3">
                    Prognoz Metrikalari
                  </h3>
                  <div className="space-y-3 mt-4 text-xs">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-600">Boshlang'ich kassa:</span>
                      <span className="font-bold text-slate-900">{formatUZS(forecast.initial_cash_balance)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-600">Eng past kassa nuqtasi:</span>
                      <span className="font-bold text-rose-700">{formatUZS(forecast.lowest_cash_point)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-600">Eng og'ir oy:</span>
                      <span className="font-bold text-amber-700">{forecast.lowest_cash_month}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-600">Kassa taqchilligi oylari:</span>
                      <span className="font-bold text-rose-700">{forecast.months_in_deficit} oy</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-600">Kutilayotgan DSCR:</span>
                      <span className="font-bold text-emerald-700">
                        {forecast.annual_dscr ? `${forecast.annual_dscr.toFixed(2)}x` : "Qarzsiz"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100 text-[11px] text-slate-500 text-center">
                  Prognoz generatsiya sanasi: <strong>{new Date(forecast.forecast_generation_date).toLocaleDateString()}</strong>
                </div>
              </div>
            </div>

            {/* Monthly Forecast Forecast Grid */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-4 border-b border-slate-100">
                <h3 className="text-sm font-bold text-slate-900">12 Oylik Prognoz Jadvali va CFADS Qoplash</h3>
                <p className="text-xs text-slate-500">Oylik prognoz qilingan operatsion oqim, kredit xizmati va yakuniy kassa balansi</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider border-b border-slate-200">
                    <tr>
                      <th className="py-3 px-4">Oy</th>
                      <th className="py-3 px-4 text-right">Boshlang'ich</th>
                      <th className="py-3 px-4 text-right text-emerald-700">Tushum</th>
                      <th className="py-3 px-4 text-right text-slate-700">Opex</th>
                      <th className="py-3 px-4 text-right text-rose-700">Kredit Xizmati</th>
                      <th className="py-3 px-4 text-right font-bold">CFADS</th>
                      <th className="py-3 px-4 text-right font-bold">Yakuniy Kassa</th>
                      <th className="py-3 px-4 text-center">DSCR</th>
                      <th className="py-3 px-4 text-center">Ogohlantirish</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {forecast.monthly_forecast.map((m) => (
                      <tr key={m.month_number} className={`hover:bg-slate-50/80 ${m.is_deficit ? 'bg-rose-50/50' : m.is_below_buffer ? 'bg-amber-50/30' : ''}`}>
                        <td className="py-3 px-4 font-bold text-slate-900">{m.month_name}</td>
                        <td className="py-3 px-4 text-right text-slate-600">{formatUZS(m.opening_balance)}</td>
                        <td className="py-3 px-4 text-right text-emerald-700 font-semibold">{formatUZS(m.projected_inflows)}</td>
                        <td className="py-3 px-4 text-right text-slate-700">{formatUZS(m.projected_operating_outflows)}</td>
                        <td className="py-3 px-4 text-right text-rose-700">{formatUZS(m.debt_service)}</td>
                        <td className={`py-3 px-4 text-right font-bold ${m.cfads >= 0 ? 'text-emerald-700' : 'text-rose-700'}`}>
                          {formatUZS(m.cfads)}
                        </td>
                        <td className={`py-3 px-4 text-right font-bold ${m.closing_balance < 0 ? 'text-rose-700' : 'text-slate-900'}`}>
                          {formatUZS(m.closing_balance)}
                        </td>
                        <td className="py-3 px-4 text-center font-bold">
                          {m.monthly_dscr !== null ? `${m.monthly_dscr.toFixed(2)}x` : "—"}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {m.is_deficit ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
                              Kassa Taqchilligi
                            </span>
                          ) : m.is_below_buffer ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                              Past Bufer
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                              Normal
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            MODULE 4: DEBT & DSCR ANALYTICS
        ========================================================================== */}
        {!loading && activeTab === 'debt' && debt && (
          <div className="space-y-6">
            {/* Top Debt Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
                <span className="text-xs text-slate-500 font-semibold">Jami Asosiy Qarz</span>
                <div className="text-2xl font-bold text-slate-900">{formatCompactUZS(debt.total_principal)}</div>
                <div className="text-xs text-slate-500 pt-1 border-t border-slate-100">
                  Aniq: {formatUZS(debt.total_principal)}
                </div>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
                <span className="text-xs text-slate-500 font-semibold">Yillik Foiz To'lovi</span>
                <div className="text-2xl font-bold text-amber-700">{formatCompactUZS(debt.total_interest)}</div>
                <div className="text-xs text-slate-500 pt-1 border-t border-slate-100">
                  Hisoblangan foiz yuki
                </div>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
                <span className="text-xs text-slate-500 font-semibold">Jami Yillik Qarz Xizmati</span>
                <div className="text-2xl font-bold text-rose-700">{formatCompactUZS(debt.total_debt_service)}</div>
                <div className="text-xs text-slate-500 pt-1 border-t border-slate-100">
                  Asosiy qarz + Foiz
                </div>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
                <span className="text-xs text-slate-500 font-semibold">Yillik DSCR Qoplash</span>
                <div className="text-2xl font-bold text-slate-900">
                  {debt.annual_dscr !== null ? `${debt.annual_dscr.toFixed(2)}x` : "Qarzsiz"}
                </div>
                <div className="text-xs pt-1 border-t border-slate-100">
                  {getDscrBadge(debt.dscr_risk_tier, debt.annual_dscr)}
                </div>
              </div>
            </div>

            {/* DSCR Formula & Risk Benchmark Box */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center space-x-2">
                  <Gauge className="w-5 h-5 text-sky-600" />
                  <h3 className="text-sm font-bold text-slate-900">DSCR Hisoblash Metodologiyasi va Bank Standartlari</h3>
                </div>
                <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-100 text-slate-700">
                  CFADS / (Asosiy Qarz + Foiz)
                </span>
              </div>

              <p className="text-xs text-slate-700 leading-relaxed">
                <strong>Izoh:</strong> {debt.dscr_interpretation_uz}
              </p>

              {/* Benchmark Bands Table */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs pt-2">
                <div className="p-3 rounded-xl border border-rose-200 bg-rose-50/60">
                  <span className="font-bold text-rose-800 block">DSCR &lt; 1.00x</span>
                  <span className="text-rose-700 mt-1 block">Kritik Xavfli: Operatsion tushum kreditni to'lashga yetarli emas.</span>
                </div>
                <div className="p-3 rounded-xl border border-amber-200 bg-amber-50/60">
                  <span className="font-bold text-amber-800 block">1.00x &le; DSCR &lt; 1.20x</span>
                  <span className="text-amber-700 mt-1 block">Cheklangan Qoplash: To'lov chegarasida, bufer yetarli emas.</span>
                </div>
                <div className="p-3 rounded-xl border border-sky-200 bg-sky-50/60">
                  <span className="font-bold text-sky-800 block">1.20x &le; DSCR &lt; 1.50x</span>
                  <span className="text-sky-700 mt-1 block">Mo'tadil Qoplash: O'zbekiston banklari minimal talabiga mos.</span>
                </div>
                <div className="p-3 rounded-xl border border-emerald-200 bg-emerald-50/60">
                  <span className="font-bold text-emerald-800 block">DSCR &ge; 1.50x</span>
                  <span className="text-emerald-700 mt-1 block">Mustahkam & Ishonchli: Yuqori to'lov qobiliyati va zaxira mavjud.</span>
                </div>
              </div>
            </div>

            {/* Active Loans Table */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-4 border-b border-slate-100 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Mavjud Kredit Shartnomalari va Garov Ta'minoti</h3>
                  <p className="text-xs text-slate-500">Banklar, stavkalar va oylik to'lov majburiyatlari</p>
                </div>
                <span className="text-xs text-slate-500">
                  Keyingi to'lov: <strong>{debt.next_payment_date}</strong> ({formatUZS(debt.next_payment_amount)})
                </span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider border-b border-slate-200">
                    <tr>
                      <th className="py-3 px-4">Kreditor Bank</th>
                      <th className="py-3 px-4">Kredit Turi</th>
                      <th className="py-3 px-4">Shartnoma #</th>
                      <th className="py-3 px-4 text-right">Asosiy Qarz</th>
                      <th className="py-3 px-4 text-center">Stavka (%)</th>
                      <th className="py-3 px-4 text-right">Oylik To'lov</th>
                      <th className="py-3 px-4">Muddat</th>
                      <th className="py-3 px-4">Garov Ta'minoti</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {debt.loan_schedules.map((loan, idx) => (
                      <tr key={idx} className="hover:bg-slate-50">
                        <td className="py-3 px-4 font-bold text-slate-900">{loan.lender_name}</td>
                        <td className="py-3 px-4 text-slate-600">{loan.loan_type}</td>
                        <td className="py-3 px-4 font-mono text-slate-500">{loan.contract_number}</td>
                        <td className="py-3 px-4 text-right font-semibold text-slate-900">{formatUZS(loan.principal_amount)}</td>
                        <td className="py-3 px-4 text-center font-bold text-emerald-700">{loan.annual_interest_rate}%</td>
                        <td className="py-3 px-4 text-right font-bold text-rose-700">{formatUZS(loan.monthly_payment)}</td>
                        <td className="py-3 px-4 text-slate-600">{loan.start_date} &rarr; {loan.maturity_date}</td>
                        <td className="py-3 px-4 text-slate-500 italic max-w-xs truncate">{loan.collateral}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            MODULE 5: FINANCIAL RISK MONITORING
        ========================================================================== */}
        {!loading && activeTab === 'risks' && risks && (
          <div className="space-y-6">
            {/* Risk Count Summary Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-xl border border-rose-200 shadow-sm flex items-center justify-between">
                <div>
                  <span className="text-xs text-rose-600 font-bold">Kritik Xavflar</span>
                  <div className="text-2xl font-extrabold text-rose-700">{risks.critical_count} ta</div>
                </div>
                <AlertOctagon className="w-8 h-8 text-rose-500" />
              </div>

              <div className="bg-white p-4 rounded-xl border border-orange-200 shadow-sm flex items-center justify-between">
                <div>
                  <span className="text-xs text-orange-600 font-bold">Yuqori Xavflar</span>
                  <div className="text-2xl font-extrabold text-orange-700">{risks.high_count} ta</div>
                </div>
                <AlertTriangle className="w-8 h-8 text-orange-500" />
              </div>

              <div className="bg-white p-4 rounded-xl border border-amber-200 shadow-sm flex items-center justify-between">
                <div>
                  <span className="text-xs text-amber-600 font-bold">O'rta Xavflar</span>
                  <div className="text-2xl font-extrabold text-amber-700">{risks.medium_count} ta</div>
                </div>
                <Info className="w-8 h-8 text-amber-500" />
              </div>

              <div className="bg-white p-4 rounded-xl border border-blue-200 shadow-sm flex items-center justify-between">
                <div>
                  <span className="text-xs text-blue-600 font-bold">Jami Xavflar</span>
                  <div className="text-2xl font-extrabold text-slate-800">{risks.risks_count} ta</div>
                </div>
                <ShieldCheck className="w-8 h-8 text-blue-500" />
              </div>
            </div>

            {/* Deep-Dive Explainable Risk Cards */}
            <div className="space-y-4">
              {risks.risks.map((risk) => (
                <div 
                  key={risk.id} 
                  className={`bg-white p-5 rounded-2xl border shadow-sm space-y-3 ${
                    risk.severity === 'CRITICAL' ? 'border-rose-300 bg-rose-50/20' :
                    risk.severity === 'HIGH' ? 'border-orange-300 bg-orange-50/20' :
                    'border-slate-200'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                    <div className="flex items-center space-x-2">
                      {risk.severity === 'CRITICAL' ? (
                        <AlertOctagon className="w-5 h-5 text-rose-600" />
                      ) : risk.severity === 'HIGH' ? (
                        <AlertTriangle className="w-5 h-5 text-orange-600" />
                      ) : (
                        <Info className="w-5 h-5 text-amber-600" />
                      )}
                      <h4 className="text-sm font-bold text-slate-900">{risk.title}</h4>
                      {getSeverityBadge(risk.severity)}
                    </div>
                    <div className="text-xs font-semibold text-slate-500">
                      Ta'sir davri: <strong className="text-slate-900">{risk.affected_period}</strong>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    <div className="space-y-1.5">
                      <div className="flex items-center justify-between text-slate-500">
                        <span>Trigger Qoidasi:</span>
                        <code className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-800">{risk.trigger_rule}</code>
                      </div>
                      <div className="flex items-center justify-between text-slate-500">
                        <span>Ko'rsatkich qiymati:</span>
                        <span className="font-bold text-slate-900">{risk.metric_value}</span>
                      </div>
                      <p className="text-slate-700 leading-relaxed pt-1">
                        {risk.explanation_uz}
                      </p>
                    </div>

                    <div className="p-3 bg-emerald-50/80 border border-emerald-200 rounded-xl space-y-1">
                      <span className="text-emerald-800 font-bold flex items-center space-x-1">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span>Tavsiya etilayotgan Boshqaruv Chorasi:</span>
                      </span>
                      <p className="text-emerald-900 leading-relaxed">
                        {risk.business_response_uz}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* =========================================================================
            MODULE 6: INTERACTIVE SCENARIO ANALYSIS SIMULATION
        ========================================================================== */}
        {!loading && activeTab === 'scenarios' && (
          <div className="space-y-6">
            {/* Header & Controls Panel */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
                <div>
                  <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                    <Sliders className="w-5 h-5 text-emerald-600" />
                    <span>Interaktiv Ssenariylar va Sezgirlik Tahlili</span>
                  </h3>
                  <p className="text-xs text-slate-500">
                    Barcha o'zgarishlar to'liq backend Financial Engine orqali qayta hisoblanadi (klient-tomon hisoblashlari yo'q).
                  </p>
                </div>

                {/* Preset Buttons */}
                <div className="flex items-center space-x-1.5 p-1 bg-slate-100 rounded-xl text-xs">
                  <button
                    onClick={() => handleApplyPreset('BASE')}
                    className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                      scenarioPreset === 'BASE' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600'
                    }`}
                  >
                    Baza (0%)
                  </button>
                  <button
                    onClick={() => handleApplyPreset('OPTIMISTIC')}
                    className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                      scenarioPreset === 'OPTIMISTIC' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-600'
                    }`}
                  >
                    Optimistik (+20%/-10%)
                  </button>
                  <button
                    onClick={() => handleApplyPreset('PESSIMISTIC')}
                    className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                      scenarioPreset === 'PESSIMISTIC' ? 'bg-rose-600 text-white shadow-sm' : 'text-slate-600'
                    }`}
                  >
                    Pessimistik (-20%/+15%)
                  </button>
                </div>
              </div>

              {/* Sliders Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Slider 1: Revenue Change */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-700">Tushum O'zgarishi:</span>
                    <span className={revenueChange >= 0 ? 'text-emerald-700 font-bold' : 'text-rose-700 font-bold'}>
                      {revenueChange >= 0 ? `+${revenueChange}%` : `${revenueChange}%`}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="-30"
                    max="30"
                    step="5"
                    value={revenueChange}
                    onChange={(e) => {
                      const val = Number(e.target.value);
                      setRevenueChange(val);
                      setScenarioPreset('CUSTOM');
                      handleRunSimulation('CUSTOM', val, costChange, delayMonths, interestDelta);
                    }}
                    className="w-full accent-emerald-600 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400">
                    <span>-30%</span>
                    <span>0%</span>
                    <span>+30%</span>
                  </div>
                </div>

                {/* Slider 2: Cost Change */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-700">Xarajatlar O'zgarishi:</span>
                    <span className={costChange <= 0 ? 'text-emerald-700 font-bold' : 'text-rose-700 font-bold'}>
                      {costChange >= 0 ? `+${costChange}%` : `${costChange}%`}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="-20"
                    max="30"
                    step="5"
                    value={costChange}
                    onChange={(e) => {
                      const val = Number(e.target.value);
                      setCostChange(val);
                      setScenarioPreset('CUSTOM');
                      handleRunSimulation('CUSTOM', revenueChange, val, delayMonths, interestDelta);
                    }}
                    className="w-full accent-rose-600 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400">
                    <span>-20%</span>
                    <span>0%</span>
                    <span>+30%</span>
                  </div>
                </div>

                {/* Slider 3: Collection Delay */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-700">To'lov Kechikishi:</span>
                    <span className="text-amber-700 font-bold">{delayMonths} oy</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="3"
                    step="1"
                    value={delayMonths}
                    onChange={(e) => {
                      const val = Number(e.target.value);
                      setDelayMonths(val);
                      setScenarioPreset('CUSTOM');
                      handleRunSimulation('CUSTOM', revenueChange, costChange, val, interestDelta);
                    }}
                    className="w-full accent-amber-600 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400">
                    <span>0 oy</span>
                    <span>1 oy</span>
                    <span>3 oy</span>
                  </div>
                </div>

                {/* Slider 4: Interest Rate Delta */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-700">Kredit Foizi O'zgarishi:</span>
                    <span className="text-sky-700 font-bold">+{interestDelta}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="5"
                    step="0.5"
                    value={interestDelta}
                    onChange={(e) => {
                      const val = Number(e.target.value);
                      setInterestDelta(val);
                      setScenarioPreset('CUSTOM');
                      handleRunSimulation('CUSTOM', revenueChange, costChange, delayMonths, val);
                    }}
                    className="w-full accent-sky-600 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400">
                    <span>0%</span>
                    <span>+2.5%</span>
                    <span>+5%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Comparison Results Card */}
            {simulationResult && (
              <div className="space-y-6">
                {/* Variance Metrics */}
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                  <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
                    <span className="text-xs text-slate-500 font-semibold">Sof Pul Oqimi Farqi</span>
                    <div className={`text-xl font-bold ${simulationResult.variance_net_cash_flow >= 0 ? 'text-emerald-700' : 'text-rose-700'}`}>
                      {simulationResult.variance_net_cash_flow >= 0 ? '+' : ''}
                      {formatCompactUZS(simulationResult.variance_net_cash_flow)}
                    </div>
                    <div className="text-[11px] text-slate-500">
                      Baza: {formatCompactUZS(simulationResult.baseline.net_annual_cash_flow)} &rarr; Stressed: {formatCompactUZS(simulationResult.stressed.net_annual_cash_flow)}
                    </div>
                  </div>

                  <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
                    <span className="text-xs text-slate-500 font-semibold">Yakuniy Kassa Farqi</span>
                    <div className={`text-xl font-bold ${simulationResult.variance_closing_balance >= 0 ? 'text-emerald-700' : 'text-rose-700'}`}>
                      {simulationResult.variance_closing_balance >= 0 ? '+' : ''}
                      {formatCompactUZS(simulationResult.variance_closing_balance)}
                    </div>
                    <div className="text-[11px] text-slate-500">
                      Baza: {formatCompactUZS(simulationResult.baseline.final_closing_balance)} &rarr; Stressed: {formatCompactUZS(simulationResult.stressed.final_closing_balance)}
                    </div>
                  </div>

                  <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
                    <span className="text-xs text-slate-500 font-semibold">DSCR Farqi</span>
                    <div className={`text-xl font-bold ${(simulationResult.variance_dscr || 0) >= 0 ? 'text-emerald-700' : 'text-rose-700'}`}>
                      {simulationResult.variance_dscr !== null ? `${simulationResult.variance_dscr >= 0 ? '+' : ''}${simulationResult.variance_dscr.toFixed(2)}x` : '—'}
                    </div>
                    <div className="text-[11px] text-slate-500">
                      Stressed DSCR: <strong>{simulationResult.stressed.annual_dscr ? `${simulationResult.stressed.annual_dscr.toFixed(2)}x` : 'Qarzsiz'}</strong>
                    </div>
                  </div>

                  <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
                    <span className="text-xs text-slate-500 font-semibold">To'lov Qobiliyati Xulosasi</span>
                    <div className="text-base font-bold text-slate-900 truncate">
                      {simulationResult.solvency_impact}
                    </div>
                    <div className="text-[11px] text-slate-500">
                      Taqchillik: <strong>{simulationResult.stressed.months_in_deficit} oy</strong>
                    </div>
                  </div>
                </div>

                {/* Stressed Cash Flow Chart */}
                <CashFlowChart
                  data={simulationResult.stressed.monthly_forecast.map(m => ({
                    month_number: m.month_number,
                    month_name: m.month_name,
                    opening_balance: m.opening_balance,
                    total_inflows: m.projected_inflows,
                    total_outflows: m.total_outflows,
                    net_cash_flow: m.net_cash_flow,
                    closing_balance: m.closing_balance,
                    debt_service: m.debt_service,
                    dscr: m.monthly_dscr,
                    is_deficit: m.is_deficit,
                    inflows_breakdown: {},
                    outflows_breakdown: {}
                  }))}
                  title={`Simulyatsiya Qilingan Pul Oqimi Dinamikasi (${simulationResult.scenario_type} Ssenariysi)`}
                />
              </div>
            )}
          </div>
        )}

        {/* =========================================================================
            MODULE 7: AI-CFO FINANCIAL INSIGHTS & EXPLANATION ENGINE
        ========================================================================== */}
        {!loading && activeTab === 'ai_cfo' && aiInsights && (
          <div className="space-y-6">
            {/* Executive Health Summary Card */}
            <div className="bg-gradient-to-r from-purple-900 via-indigo-900 to-slate-900 text-white p-6 rounded-2xl shadow-xl space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-purple-800/80 pb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2.5 bg-purple-500/20 rounded-xl border border-purple-400/30">
                    <BrainCircuit className="w-6 h-6 text-purple-300" />
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-purple-300 uppercase tracking-wider">
                      AI-CFO Moliyaviy Salomatlik Tahlili
                    </span>
                    <h3 className="text-lg font-bold text-white">
                      Strategik Intellekt & Boshqaruv Xulosasi
                    </h3>
                  </div>
                </div>

                {/* LLM Toggle Button */}
                <button
                  onClick={handleToggleLLM}
                  disabled={llmLoading}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition-all border ${
                    aiInsights.is_llm_used
                      ? 'bg-purple-500 text-white border-purple-400 shadow-lg'
                      : 'bg-white/10 text-purple-200 border-white/20 hover:bg-white/20'
                  }`}
                >
                  <Sparkles className={`w-4 h-4 ${llmLoading ? 'animate-spin' : ''}`} />
                  <span>{aiInsights.is_llm_used ? "LLM Tushuntirishi Faol" : "LLM Izohini Yoqish (Maxfiy)"}</span>
                </button>
              </div>

              {/* Health Summary Text */}
              <p className="text-sm text-purple-100 leading-relaxed">
                {aiInsights.financial_health_summary_uz}
              </p>

              {/* Key Findings Bullets */}
              <div className="space-y-2 pt-2">
                <span className="text-xs font-bold uppercase tracking-wider text-purple-300">
                  Asosiy Strategik Xulosalar:
                </span>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                  {aiInsights.key_findings_uz.map((finding, idx) => (
                    <div key={idx} className="flex items-start space-x-2 bg-white/5 p-2.5 rounded-lg border border-white/10">
                      <span className="text-purple-400 font-bold">•</span>
                      <span className="text-purple-100">{finding}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Privacy Notice */}
              <div className="flex items-center justify-between text-[11px] text-purple-300 border-t border-purple-800/80 pt-3">
                <span className="flex items-center space-x-1.5">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Dvigatel: <strong>{aiInsights.generation_method}</strong> (Faktik tekshirilgan)</span>
                </span>
                <span className="italic">{aiInsights.disclaimer_uz}</span>
              </div>
            </div>

            {/* Deep-Dive Insight Cards */}
            <div className="space-y-4">
              <h4 className="text-sm font-bold text-slate-900">
                Isbotlangan Tahliliy Dalillar va Tavsiyalar ({aiInsights.insights.length} ta xulosa)
              </h4>

              {aiInsights.insights.map((insight) => (
                <div 
                  key={insight.insight_id}
                  className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                    <div className="flex items-center space-x-2.5">
                      {getSeverityBadge(insight.severity)}
                      <h5 className="font-bold text-slate-900 text-sm">{insight.headline_uz}</h5>
                    </div>
                    <span className="text-xs px-2 py-0.5 rounded font-mono bg-slate-100 text-slate-700">
                      {insight.insight_type}
                    </span>
                  </div>

                  {/* Core Message */}
                  <p className="text-xs text-slate-800 leading-relaxed">
                    {insight.core_message_uz}
                  </p>

                  {/* Evidence Bullets & Verifiable Data Table */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    <div className="space-y-2">
                      <span className="font-bold text-slate-700 block">Isbotlangan Raqamli Faktlar:</span>
                      <ul className="space-y-1 list-disc list-inside text-slate-600">
                        {insight.evidence_bullets_uz.map((bullet, bIdx) => (
                          <li key={bIdx}>{bullet}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl space-y-1.5">
                      <span className="font-bold text-emerald-900 flex items-center space-x-1.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span>Boshqaruv Tavsiyasi (CFO Tavsiyasi):</span>
                      </span>
                      <p className="text-emerald-950 leading-relaxed text-xs">
                        {insight.recommended_action_uz}
                      </p>
                    </div>
                  </div>

                  {/* Supporting Metrics Badges */}
                  <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 text-[11px] text-slate-500">
                    <span className="font-semibold">Hisoblangan parametrlar:</span>
                    {Object.entries(insight.supporting_metrics).map(([k, v]) => (
                      <span key={k} className="px-2 py-0.5 rounded bg-slate-100 text-slate-800 font-mono">
                        {k}: {String(v)}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="flex items-center space-x-2 text-slate-600 text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
          <span>Yuklanmoqda...</span>
        </div>
      </div>
    }>
      <DashboardContent />
    </Suspense>
  );
}
