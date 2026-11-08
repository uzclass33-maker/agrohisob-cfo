'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { runStressTest, fetchScenarios } from '@/lib/api';
import { StressTestResponse, SyntheticScenarioMeta } from '@/lib/types';
import { formatUZS, formatCompactUZS, formatPercent } from '@/lib/formatters';
import CashFlowChart from '@/components/CashFlowChart';
import { 
  Sliders, TrendingDown, AlertTriangle, CheckCircle2, 
  RotateCcw, ShieldCheck, ArrowRight, RefreshCw, BarChart3 
} from 'lucide-react';

function ScenarioAnalysisContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [scenarios, setScenarios] = useState<SyntheticScenarioMeta[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>(
    searchParams.get('scenario') || 'scenario-small-farmer'
  );

  // Shock parameters
  const [yieldShock, setYieldShock] = useState<number>(-15); // -15% default shock
  const [priceShock, setPriceShock] = useState<number>(-10); // -10% price decline
  const [costShock, setCostShock] = useState<number>(10);   // +10% cost increase
  const [interestRate, setInterestRate] = useState<number>(14.0);

  const [result, setResult] = useState<StressTestResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const scs = await fetchScenarios();
        setScenarios(scs);
      } catch (e) {
        console.error(e);
      }
    }
    load();
  }, []);

  const executeSimulation = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await runStressTest({
        scenario_id: selectedScenarioId,
        yield_shock_pct: yieldShock,
        price_shock_pct: priceShock,
        cost_shock_pct: costShock,
        interest_rate_override: interestRate
      });
      setResult(res);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Simulyatsiyani bajarishda xatolik yuz berdi.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    executeSimulation();
  }, [selectedScenarioId, yieldShock, priceShock, costShock, interestRate]);

  const resetShocks = () => {
    setYieldShock(0);
    setPriceShock(0);
    setCostShock(0);
    setInterestRate(14.0);
  };

  return (
    <div className="py-8 bg-slate-50 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-sky-100 text-sky-800 text-xs font-semibold mb-2">
              <Sliders className="w-3.5 h-3.5 text-sky-600" />
              <span>Sensitivity & Stress-Testing Engine</span>
            </div>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              Hosil, Narx va Xarajatlar Stress-Testi
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 mt-1">
              Qurg'oqchilik, sovuq urishi, xomashyo narxi tushishi va yoqilg'i qimmatlashganda korxonaning kredit to'lash qobiliyatini (DSCR) sinash.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={resetShocks}
              className="px-3.5 py-2 bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 rounded-xl text-xs font-semibold shadow-sm inline-flex items-center"
            >
              <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
              Nolga Qaytarish (Bazaviy Holat)
            </button>
          </div>
        </div>

        {/* Business Selector */}
        <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap gap-2 items-center">
          <span className="text-xs font-bold text-slate-500 uppercase px-2">Korxona:</span>
          {scenarios.map((sc) => (
            <button
              key={sc.id}
              onClick={() => {
                setSelectedScenarioId(sc.id);
                router.push(`/scenario-analysis?scenario=${sc.id}`);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                sc.id === selectedScenarioId
                  ? 'bg-agro-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {sc.name}
            </button>
          ))}
        </div>

        {/* Shock Sliders Box */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="font-bold text-slate-900 mb-4 text-sm sm:text-base">
            Stress-Test Parametrlari (Shok Omillari)
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Yield Shock */}
            <div>
              <div className="flex justify-between items-center mb-1 text-xs">
                <span className="font-semibold text-slate-700">Hosildorlik Shoki:</span>
                <span className={`font-mono font-bold ${yieldShock < 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                  {formatPercent(yieldShock)}
                </span>
              </div>
              <input
                type="range"
                min="-40"
                max="40"
                step="5"
                value={yieldShock}
                onChange={(e) => setYieldShock(Number(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-agro-600"
              />
              <span className="text-[10px] text-slate-400">Ayoz, qurg'oqchilik yoki kasallik ta'siri</span>
            </div>

            {/* Price Shock */}
            <div>
              <div className="flex justify-between items-center mb-1 text-xs">
                <span className="font-semibold text-slate-700">Mahsulot Narxi Tebranishi:</span>
                <span className={`font-mono font-bold ${priceShock < 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                  {formatPercent(priceShock)}
                </span>
              </div>
              <input
                type="range"
                min="-40"
                max="40"
                step="5"
                value={priceShock}
                onChange={(e) => setPriceShock(Number(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-agro-600"
              />
              <span className="text-[10px] text-slate-400">Bozor taklifi ko'payishi yoki eksport narxi</span>
            </div>

            {/* Cost Shock */}
            <div>
              <div className="flex justify-between items-center mb-1 text-xs">
                <span className="font-semibold text-slate-700">Xarajatlar Inflyatsiyasi:</span>
                <span className="font-mono font-bold text-rose-600">
                  {formatPercent(costShock)}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="50"
                step="5"
                value={costShock}
                onChange={(e) => setCostShock(Number(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-rose-600"
              />
              <span className="text-[10px] text-slate-400">Dizel, o'g'it va logistika qimmatlashuvi</span>
            </div>

            {/* Interest Rate */}
            <div>
              <div className="flex justify-between items-center mb-1 text-xs">
                <span className="font-semibold text-slate-700">Kredit Foiz Stavkasi:</span>
                <span className="font-mono font-bold text-indigo-700">
                  {interestRate.toFixed(1)}%
                </span>
              </div>
              <input
                type="range"
                min="10"
                max="28"
                step="0.5"
                value={interestRate}
                onChange={(e) => setInterestRate(Number(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <span className="text-[10px] text-slate-400">10-14% Imtiyozli | 23.5% Tijoriy</span>
            </div>
          </div>
        </div>

        {/* Results */}
        {loading ? (
          <div className="p-8 text-center bg-white rounded-2xl border border-slate-200">
            <RefreshCw className="w-6 h-6 text-sky-600 animate-spin mx-auto mb-2" />
            <p className="text-xs text-slate-500">Stoxastik stress-test modeli qayta hisoblanmoqda...</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-rose-50 border border-rose-200 text-rose-800 rounded-2xl text-xs">
            {error}
          </div>
        ) : result ? (
          <>
            {/* Solvency Status Alert */}
            <div className={`p-4 rounded-xl border flex items-center justify-between text-xs sm:text-sm ${
              result.solvency_status.includes('RESILIENT')
                ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                : result.solvency_status.includes('VULNERABLE')
                ? 'bg-amber-50 border-amber-200 text-amber-900'
                : 'bg-rose-50 border-rose-200 text-rose-900'
            }`}>
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 shrink-0" />
                <div>
                  <span className="font-bold">Stress-Test Natijasi:</span> {result.solvency_status}
                </div>
              </div>
              <span className="font-mono font-bold">DSCR: {result.stressed_dscr}x</span>
            </div>

            {/* Baseline vs Stressed Comparative Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-400 block uppercase">Yillik Yalpi Tushum</span>
                <div className="mt-1 flex items-baseline justify-between">
                  <span className="text-base font-bold text-slate-900">{formatCompactUZS(result.stressed_annual_inflow)}</span>
                  <span className="text-xs text-slate-400 line-through">{formatCompactUZS(result.baseline_annual_inflow)}</span>
                </div>
                <span className="text-[10px] text-slate-500">Shokdan keyingi kassa kirimi</span>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-400 block uppercase">Yillik Xarajatlar</span>
                <div className="mt-1 flex items-baseline justify-between">
                  <span className="text-base font-bold text-rose-600">{formatCompactUZS(result.stressed_annual_outflow)}</span>
                  <span className="text-xs text-slate-400 line-through">{formatCompactUZS(result.baseline_annual_outflow)}</span>
                </div>
                <span className="text-[10px] text-slate-500">Inflyatsiya hisobga olingan holda</span>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-400 block uppercase">DSCR O'zgarishi</span>
                <div className="mt-1 flex items-baseline justify-between">
                  <span className="text-base font-bold text-indigo-700">{result.stressed_dscr}x</span>
                  <span className="text-xs text-slate-400">Bazaviy: {result.baseline_dscr}x</span>
                </div>
                <span className={`text-[10px] font-semibold ${result.dscr_change_pct < 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                  Delta: {formatPercent(result.dscr_change_pct)}
                </span>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-400 block uppercase">Defitsit Oylari</span>
                <div className="mt-1 flex items-baseline justify-between">
                  <span className="text-base font-bold text-amber-700">{result.deficit_months_stressed} oy</span>
                  <span className="text-xs text-slate-400">Oldin: {result.deficit_months_baseline} oy</span>
                </div>
                <span className="text-[10px] text-slate-500">
                  Minimal kassa: {formatCompactUZS(result.minimum_cash_stressed)}
                </span>
              </div>
            </div>

            {/* Stressed Cash Flow Chart */}
            <CashFlowChart 
              data={result.stressed_monthly_data} 
              title="Stress-Test Shokidan Keyingi 12 Oylik Kassa Oqimi Dinamikasi" 
            />
          </>
        ) : null}
      </div>
    </div>
  );
}

export default function ScenarioAnalysisPage() {
  return (
    <Suspense fallback={
      <div className="py-12 text-center bg-slate-50 min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2 text-slate-500 text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-sky-600" />
          <span>Stress-test moduli yuklanmoqda...</span>
        </div>
      </div>
    }>
      <ScenarioAnalysisContent />
    </Suspense>
  );
}
