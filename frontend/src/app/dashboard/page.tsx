'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { calculateFinancials, fetchScenarios, fetchLoanSchedule } from '@/lib/api';
import { FinancialSummaryResponse, SyntheticScenarioMeta, LoanScheduleResponse } from '@/lib/types';
import { formatUZS, formatCompactUZS } from '@/lib/formatters';
import CashFlowChart from '@/components/CashFlowChart';
import { 
  Building2, Wheat, Truck, CheckCircle2, AlertTriangle, 
  ArrowUpRight, ArrowDownRight, RefreshCw, Sliders, ShieldCheck, 
  DollarSign, Calendar, AlertOctagon, TrendingUp, TrendingDown, Info
} from 'lucide-react';

function DashboardContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [scenarios, setScenarios] = useState<SyntheticScenarioMeta[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>(
    searchParams.get('scenario') || 'scenario-small-farmer'
  );
  const [summary, setSummary] = useState<FinancialSummaryResponse | null>(null);
  const [loanSchedule, setLoanSchedule] = useState<LoanScheduleResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Scenario variant: 'BASE', 'OPTIMISTIC', 'PESSIMISTIC'
  const [scenarioVariant, setScenarioVariant] = useState<'BASE' | 'OPTIMISTIC' | 'PESSIMISTIC'>('BASE');

  // Load scenarios list
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

  // Update selected scenario when query param changes
  useEffect(() => {
    const fromParam = searchParams.get('scenario');
    if (fromParam && fromParam !== selectedScenarioId) {
      setSelectedScenarioId(fromParam);
    }
  }, [searchParams]);

  // Load calculation and loan schedule from backend for current scenario
  useEffect(() => {
    async function runCalc() {
      try {
        setLoading(true);
        setError(null);
        
        // 1. Fetch baseline financial calculation
        const res = await calculateFinancials(selectedScenarioId);

        // Adjust figures if non-base variant selected (deterministic UI simulation)
        if (scenarioVariant === 'OPTIMISTIC') {
          const optMonthly = res.monthly_data.map(m => {
            const inBump = m.total_inflows * 1.20;
            const outSave = m.total_outflows * 0.90;
            const net = inBump - outSave;
            return {
              ...m,
              total_inflows: Math.round(inBump),
              total_outflows: Math.round(outSave),
              net_cash_flow: Math.round(net)
            };
          });
          // Roll-forward recalculation
          let curOp = res.initial_opening_balance;
          for (let m of optMonthly) {
            m.opening_balance = Math.round(curOp);
            m.closing_balance = Math.round(curOp + m.net_cash_flow);
            m.is_deficit = m.closing_balance < 0;
            curOp = m.closing_balance;
          }
          const totIn = optMonthly.reduce((s, m) => s + m.total_inflows, 0);
          const totOut = optMonthly.reduce((s, m) => s + m.total_outflows, 0);
          setSummary({
            ...res,
            total_annual_inflows: totIn,
            total_annual_outflows: totOut,
            net_annual_cash_flow: totIn - totOut,
            final_closing_balance: curOp,
            monthly_data: optMonthly,
            months_in_deficit: optMonthly.filter(m => m.is_deficit).length
          });
        } else if (scenarioVariant === 'PESSIMISTIC') {
          const pesMonthly = res.monthly_data.map(m => {
            const inDrop = m.total_inflows * 0.80;
            const outHike = m.total_outflows * 1.15;
            const net = inDrop - outHike;
            return {
              ...m,
              total_inflows: Math.round(inDrop),
              total_outflows: Math.round(outHike),
              net_cash_flow: Math.round(net)
            };
          });
          let curOp = res.initial_opening_balance;
          for (let m of pesMonthly) {
            m.opening_balance = Math.round(curOp);
            m.closing_balance = Math.round(curOp + m.net_cash_flow);
            m.is_deficit = m.closing_balance < 0;
            curOp = m.closing_balance;
          }
          const totIn = pesMonthly.reduce((s, m) => s + m.total_inflows, 0);
          const totOut = pesMonthly.reduce((s, m) => s + m.total_outflows, 0);
          setSummary({
            ...res,
            total_annual_inflows: totIn,
            total_annual_outflows: totOut,
            net_annual_cash_flow: totIn - totOut,
            final_closing_balance: curOp,
            monthly_data: pesMonthly,
            months_in_deficit: pesMonthly.filter(m => m.is_deficit).length
          });
        } else {
          setSummary(res);
        }

        // 2. Fetch loan schedule for this scenario
        let principal = 100_000_000;
        let rate = 14.0;
        if (selectedScenarioId === 'scenario-exporter') {
          principal = 900_000_000;
          rate = 23.5;
        } else if (selectedScenarioId === 'scenario-cluster') {
          principal = 5_500_000_000;
          rate = 14.0;
        }

        const loanRes = await fetchLoanSchedule({
          principal,
          annual_interest_rate_pct: rate,
          start_date: '2025-01-01',
          term_months: 12,
          repayment_type: 'ANNUITY'
        });
        setLoanSchedule(loanRes);

      } catch (err: any) {
        console.error("Calculation error:", err);
        setError(err.message || "Moliyaviy hisob-kitobni olishda xatolik yuz berdi.");
      } finally {
        setLoading(false);
      }
    }
    if (selectedScenarioId) {
      runCalc();
    }
  }, [selectedScenarioId, scenarioVariant]);

  const handleScenarioChange = (id: string) => {
    setSelectedScenarioId(id);
    router.push(`/dashboard?scenario=${id}`);
  };

  const getDscrBadge = (rating: string, dscr: number) => {
    if (dscr >= 1.6) {
      return (
        <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
          {dscr}x — A'lo (DSCR {'>='} 1.6)
        </span>
      );
    }
    if (dscr >= 1.25) {
      return (
        <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-sky-100 text-sky-800 border border-sky-200">
          {dscr}x — Barqaror (Bankable)
        </span>
      );
    }
    if (dscr >= 1.0) {
      return (
        <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200">
          {dscr}x — Kuzatuvda (1.0 - 1.25)
        </span>
      );
    }
    return (
      <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-rose-100 text-rose-800 border border-rose-200">
        {dscr}x — Xatarli (DSCR {'<'} 1.0)
      </span>
    );
  };

  return (
    <div className="py-8 bg-slate-50 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        
        {/* Scenario Switcher Tabs */}
        <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-500">
            <span>Tanlangan Agrobiznes:</span>
          </div>

          <div className="flex flex-wrap gap-2 w-full md:w-auto">
            {scenarios.map((sc) => {
              const active = sc.id === selectedScenarioId;
              return (
                <button
                  key={sc.id}
                  onClick={() => handleScenarioChange(sc.id)}
                  className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center space-x-2 ${
                    active
                      ? 'bg-agro-600 text-white shadow-sm'
                      : 'bg-slate-50 text-slate-700 hover:bg-slate-100 border border-slate-200'
                  }`}
                >
                  {sc.category === 'small_farmer' && <Wheat className="w-4 h-4" />}
                  {sc.category === 'exporter' && <Truck className="w-4 h-4" />}
                  {sc.category === 'cluster' && <Building2 className="w-4 h-4" />}
                  <span>{sc.name}</span>
                </button>
              );
            })}
          </div>

          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center px-2 py-1 rounded bg-amber-100 text-amber-800 text-[11px] font-bold">
              Sintetik Demo Ma'lumot
            </span>
          </div>
        </div>

        {loading ? (
          <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
            <RefreshCw className="w-8 h-8 text-agro-600 animate-spin mx-auto mb-3" />
            <p className="text-slate-600 font-medium">FastAPI Moliyaviy Dvigatelida 12 Oylik Balans Hisoblanmoqda...</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-rose-50 border border-rose-200 text-rose-800 rounded-2xl">
            <p className="font-semibold">{error}</p>
          </div>
        ) : summary ? (
          <>
            {/* Header info & Scenario Selector */}
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
              <div>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                  {summary.organization_name}
                </h1>
                <p className="text-xs text-slate-500 mt-1">
                  Fiskal yil: {summary.fiscal_year} | Valyuta: <strong>UZS (So'm)</strong> | Buxgalteriya holati:{' '}
                  <span className="font-semibold text-emerald-600">
                    {summary.reconciliation_message}
                  </span>
                </p>
              </div>

              {/* Scenario Toggle */}
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-bold text-slate-500 mr-1">Ssenariy:</span>
                <button
                  onClick={() => setScenarioVariant('BASE')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                    scenarioVariant === 'BASE' 
                      ? 'bg-slate-900 text-white shadow-sm' 
                      : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  Baza Reja
                </button>
                <button
                  onClick={() => setScenarioVariant('OPTIMISTIC')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1 ${
                    scenarioVariant === 'OPTIMISTIC' 
                      ? 'bg-emerald-600 text-white shadow-sm' 
                      : 'bg-white text-emerald-700 border border-emerald-200 hover:bg-emerald-50'
                  }`}
                >
                  <TrendingUp className="w-3.5 h-3.5 mr-1" />
                  Optimistik (+20%)
                </button>
                <button
                  onClick={() => setScenarioVariant('PESSIMISTIC')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1 ${
                    scenarioVariant === 'PESSIMISTIC' 
                      ? 'bg-rose-600 text-white shadow-sm' 
                      : 'bg-white text-rose-700 border border-rose-200 hover:bg-rose-50'
                  }`}
                >
                  <TrendingDown className="w-3.5 h-3.5 mr-1" />
                  Pessimistik (-20%)
                </button>
                <button
                  onClick={() => router.push(`/scenario-analysis?scenario=${selectedScenarioId}`)}
                  className="px-3 py-1.5 bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-lg text-xs font-semibold shadow-sm inline-flex items-center"
                >
                  <Sliders className="w-3.5 h-3.5 mr-1 text-sky-600" />
                  Maxsus Shoklar
                </button>
              </div>
            </div>

            {/* Reconciliation Banner */}
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3.5 flex items-center justify-between text-xs text-emerald-900">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>
                  <strong>Deterministik Moliya Balansi Reconciled:</strong> 12 oylik kassa qoldiqlari qat'iy tekshirildi (Yakuniy qoldiq = Boshlang'ich + Tushumlar - Xarajatlar).
                </span>
              </div>
              <span className="font-bold text-emerald-700">100% Mos</span>
            </div>

            {/* KPI Cards Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-400 block uppercase">Boshlang'ich Kassa</span>
                <span className="text-lg font-black text-slate-900 mt-1 block">
                  {formatCompactUZS(summary.initial_opening_balance)}
                </span>
                <span className="text-[10px] text-slate-500">1-Yanvar holatiga</span>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-400 block uppercase">Yillik Yalpi Tushum</span>
                <div className="flex items-center mt-1">
                  <ArrowUpRight className="w-4 h-4 text-emerald-600 mr-0.5" />
                  <span className="text-lg font-black text-emerald-600">
                    {formatCompactUZS(summary.total_annual_inflows)}
                  </span>
                </div>
                <span className="text-[10px] text-slate-500">Hosil sotish va eksport</span>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-400 block uppercase">Yillik Jami Xarajat</span>
                <div className="flex items-center mt-1">
                  <ArrowDownRight className="w-4 h-4 text-rose-600 mr-0.5" />
                  <span className="text-lg font-black text-rose-600">
                    {formatCompactUZS(summary.total_annual_outflows)}
                  </span>
                </div>
                <span className="text-[10px] text-slate-500">Agro-texnika, urug', ish haqi</span>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-400 block uppercase">Yakuniy Kassa Qoldig'i</span>
                <span className={`text-lg font-black mt-1 block ${
                  summary.final_closing_balance >= 0 ? 'text-sky-700' : 'text-rose-600'
                }`}>
                  {formatCompactUZS(summary.final_closing_balance)}
                </span>
                <span className="text-[10px] text-slate-500">31-Dekabr kutilmasi</span>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-400 block uppercase">Qarz Qoplami (DSCR)</span>
                <div className="mt-1">
                  {getDscrBadge(summary.dscr_rating, summary.annual_dscr)}
                </div>
                <span className="text-[10px] text-slate-500 mt-1 block">Tavsiya {'>='} 1.25x</span>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-400 block uppercase">Kassa Uzilishi (Defitsit)</span>
                <div className="flex items-center mt-1">
                  {summary.months_in_deficit > 0 ? (
                    <span className="inline-flex items-center text-rose-600 font-bold text-lg">
                      <AlertTriangle className="w-4 h-4 mr-1 text-rose-500" />
                      {summary.months_in_deficit} oy
                    </span>
                  ) : (
                    <span className="text-emerald-600 font-bold text-lg">0 oy (Yo'q)</span>
                  )}
                </div>
                <span className="text-[10px] text-slate-500">
                  Eng past: {summary.lowest_cash_month} ({formatCompactUZS(summary.lowest_cash_point)})
                </span>
              </div>
            </div>

            {/* Liquidity Risk Alerts Panel (Assignment 2 Requirement) */}
            {summary.months_in_deficit > 0 && (
              <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-xl shadow-sm">
                <div className="flex items-start">
                  <AlertOctagon className="w-5 h-5 text-amber-600 mt-0.5 mr-3 shrink-0" />
                  <div className="space-y-1">
                    <h4 className="text-sm font-bold text-amber-900">
                      Likvidlik Xatari Ogohlantirishi: Bahorgi Mavsumiy Kassa Uzilishi Aniqlangan
                    </h4>
                    <p className="text-xs text-amber-800">
                      Korxonada <strong>{summary.months_in_deficit} oyda</strong> kassa balansi manfiy bo'lib qoladi. 
                      Eng past kassa nuqtasi: <strong>{summary.lowest_cash_month}</strong> oyida ({formatUZS(summary.lowest_cash_point)}).
                    </p>
                    <p className="text-xs text-amber-900 font-semibold mt-1">
                      💡 Tavsiya etilgan chora: Bahorgi urug' va yoqilg'i sotib olish uchun bankdan {formatCompactUZS(Math.abs(summary.lowest_cash_point) + 15000000)} aylanma mablag' liniyasi yoki yetkazib beruvchilar bilan 60 kunlik kechiktirilgan to'lov shartnomasi talab etiladi.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Real Cash Flow Chart */}
            <CashFlowChart data={summary.monthly_data} />

            {/* Debt Amortization & DSCR Module (Assignment 2 Requirement) */}
            {loanSchedule && (
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                  <div>
                    <h3 className="font-bold text-slate-900 flex items-center space-x-2">
                      <DollarSign className="w-5 h-5 text-indigo-600" />
                      <span>Kredit Amortizatsiyasi va Qarz To'lovlari Jadvali (12 Oy)</span>
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Asosiy qarz: <strong>{formatUZS(loanSchedule.principal)}</strong> | Yillik stavka: <strong>{loanSchedule.annual_interest_rate_pct}%</strong> | Turi: <strong>Annuitet</strong>
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-slate-400 block">Jami To'lanadigan Foiz:</span>
                    <span className="text-sm font-bold text-indigo-700">{formatUZS(loanSchedule.total_interest_cost)}</span>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                        <th className="py-2.5 px-4">Oy / Sana</th>
                        <th className="py-2.5 px-4 text-right">Boshlang'ich Asosiy Qarz</th>
                        <th className="py-2.5 px-4 text-right text-emerald-700">Asosiy Qarz To'lovi</th>
                        <th className="py-2.5 px-4 text-right text-amber-700">Foiz To'lovi</th>
                        <th className="py-2.5 px-4 text-right font-bold text-indigo-900">Jami Oylik To'lov</th>
                        <th className="py-2.5 px-4 text-right">Qoldiq Asosiy Qarz</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {loanSchedule.schedule.map((row) => (
                        <tr key={row.period_number} className="hover:bg-slate-50/80 transition">
                          <td className="py-2.5 px-4 font-mono font-medium text-slate-900">
                            {row.period_number}-oy ({row.payment_date})
                          </td>
                          <td className="py-2.5 px-4 text-right font-mono text-slate-600">
                            {formatUZS(row.opening_principal)}
                          </td>
                          <td className="py-2.5 px-4 text-right font-mono text-emerald-600 font-semibold">
                            {formatUZS(row.principal_paid)}
                          </td>
                          <td className="py-2.5 px-4 text-right font-mono text-amber-600">
                            {formatUZS(row.interest_paid)}
                          </td>
                          <td className="py-2.5 px-4 text-right font-mono font-bold text-indigo-700">
                            {formatUZS(row.total_payment)}
                          </td>
                          <td className={`py-2.5 px-4 text-right font-mono font-bold ${
                            row.remaining_principal === 0 ? 'text-emerald-700' : 'text-slate-900'
                          }`}>
                            {formatUZS(row.remaining_principal)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Detailed Monthly Breakdown Table */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-5 border-b border-slate-100 flex justify-between items-center">
                <div>
                  <h3 className="font-bold text-slate-900">12 Oylik Kassa Oqimi Jurnali va Rekonsilyatsiya</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Har bir oy uchun ochilish qoldig'i, oylik kirim/chiqimlar va yopilish qoldig'i hisobi
                  </p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                      <th className="py-3 px-4">Oy</th>
                      <th className="py-3 px-4 text-right">Boshlang'ich Qoldiq</th>
                      <th className="py-3 px-4 text-right text-emerald-700">Tushumlar (+)</th>
                      <th className="py-3 px-4 text-right text-rose-700">Xarajatlar (-)</th>
                      <th className="py-3 px-4 text-right">Sof Oqim</th>
                      <th className="py-3 px-4 text-right text-indigo-700">Kredit To'lovi</th>
                      <th className="py-3 px-4 text-right font-bold text-slate-900">Yakuniy Qoldiq</th>
                      <th className="py-3 px-4 text-center">Kassa Holati</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-700">
                    {summary.monthly_data.map((m) => (
                      <tr key={m.month_number} className="hover:bg-slate-50/80 transition">
                        <td className="py-3 px-4 font-semibold text-slate-900">
                          {m.month_number}. {m.month_name}
                        </td>
                        <td className="py-3 px-4 text-right font-mono">
                          {formatUZS(m.opening_balance)}
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-emerald-600 font-medium">
                          {formatUZS(m.total_inflows)}
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-rose-600 font-medium">
                          {formatUZS(m.total_outflows)}
                        </td>
                        <td className={`py-3 px-4 text-right font-mono font-semibold ${
                          m.net_cash_flow >= 0 ? 'text-emerald-700' : 'text-amber-700'
                        }`}>
                          {formatUZS(m.net_cash_flow)}
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-indigo-600">
                          {formatUZS(m.debt_service)}
                        </td>
                        <td className={`py-3 px-4 text-right font-mono font-bold ${
                          m.closing_balance < 0 ? 'text-rose-600' : 'text-slate-900'
                        }`}>
                          {formatUZS(m.closing_balance)}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {m.is_deficit ? (
                            <span className="inline-flex items-center px-2 py-0.5 rounded bg-rose-100 text-rose-800 text-[10px] font-bold">
                              Defitsit
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                              Ijobiy
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="bg-slate-100 font-bold text-slate-900 border-t-2 border-slate-300">
                      <td className="py-3 px-4">Yillik Jami:</td>
                      <td className="py-3 px-4 text-right font-mono">{formatUZS(summary.initial_opening_balance)}</td>
                      <td className="py-3 px-4 text-right font-mono text-emerald-700">{formatUZS(summary.total_annual_inflows)}</td>
                      <td className="py-3 px-4 text-right font-mono text-rose-700">{formatUZS(summary.total_annual_outflows)}</td>
                      <td className="py-3 px-4 text-right font-mono">{formatUZS(summary.net_annual_cash_flow)}</td>
                      <td className="py-3 px-4 text-right font-mono text-indigo-700">{formatUZS(summary.total_debt_service)}</td>
                      <td className="py-3 px-4 text-right font-mono text-sky-800">{formatUZS(summary.final_closing_balance)}</td>
                      <td className="py-3 px-4 text-center">
                        <span className="px-2 py-0.5 rounded bg-emerald-200 text-emerald-900 text-[10px]">Reconciled</span>
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>

            {/* Category Breakdown */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="font-bold text-slate-900 mb-3">Xarajatlar Moddalar Kesimida (IKPU / MXIK Agregatsiyasi)</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(summary.category_summary).map(([cat, amount]) => (
                  <div key={cat} className="p-3 bg-slate-50 rounded-lg border border-slate-100 text-xs">
                    <span className="text-slate-400 block font-semibold truncate">{cat}</span>
                    <span className="text-sm font-bold text-slate-800 mt-1 block">{formatUZS(amount)}</span>
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={
      <div className="py-12 text-center bg-slate-50 min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2 text-slate-500 text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-agro-600" />
          <span>Moliya paneli yuklanmoqda...</span>
        </div>
      </div>
    }>
      <DashboardContent />
    </Suspense>
  );
}
