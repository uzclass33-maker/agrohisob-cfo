'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { fetchCreditReadiness, fetchScenarios } from '@/lib/api';
import { CreditReadinessScorecard, SyntheticScenarioMeta } from '@/lib/types';
import { formatUZS, formatCompactUZS } from '@/lib/formatters';
import { 
  ShieldCheck, AlertCircle, FileText, CheckCircle2, 
  Download, Printer, Building2, MapPin, Award, Layers, TrendingUp, AlertTriangle, RefreshCw 
} from 'lucide-react';

function CreditReportContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [scenarios, setScenarios] = useState<SyntheticScenarioMeta[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>(
    searchParams.get('scenario') || 'scenario-small-farmer'
  );
  const [scorecard, setScorecard] = useState<CreditReadinessScorecard | null>(null);
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

  useEffect(() => {
    async function loadScorecard() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchCreditReadiness(selectedScenarioId);
        setScorecard(data);
      } catch (err: any) {
        console.error(err);
        setError(err.message || "Kredit xulosasini olishda xatolik yuz berdi.");
      } finally {
        setLoading(false);
      }
    }
    if (selectedScenarioId) {
      loadScorecard();
    }
  }, [selectedScenarioId]);

  return (
    <div className="py-8 bg-slate-50 min-h-screen">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        
        {/* Header Actions */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-indigo-100 text-indigo-800 text-xs font-semibold mb-2">
              <ShieldCheck className="w-3.5 h-3.5 text-indigo-600" />
              <span>Pre-Underwriting Dossier</span>
            </div>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              Bank Kreditga Tayyorgarlik Dosyesi
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 mt-1">
              Agrobank va tijorat banklari kredit qo'mitasi talablariga mos dastlabki skoring va VMQ-613 yer ijarasi garov bahosi
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => window.print()}
              className="px-3.5 py-2 bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 rounded-xl text-xs font-semibold shadow-sm inline-flex items-center"
            >
              <Printer className="w-3.5 h-3.5 mr-1.5" />
              Chop Etish / PDF
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
                router.push(`/credit-report?scenario=${sc.id}`);
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

        {loading ? (
          <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
            <ShieldCheck className="w-8 h-8 text-indigo-600 animate-pulse mx-auto mb-2" />
            <p className="text-xs text-slate-500">Kreditga tayyorgarlik skoringi va VMQ-613 garov bahosi shakllanmoqda...</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-rose-50 border border-rose-200 text-rose-800 rounded-2xl text-xs">
            {error}
          </div>
        ) : scorecard ? (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden p-6 sm:p-8 space-y-8">
            
            {/* Dossier Header Info */}
            <div className="border-b border-slate-200 pb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <span className="text-xs font-bold text-agro-700 uppercase tracking-widest">
                  Kreditga Layoqatlilik Xulosasi
                </span>
                <h2 className="text-2xl font-black text-slate-900 mt-1">
                  {scorecard.organization_name}
                </h2>
                <div className="flex items-center space-x-3 text-xs text-slate-500 mt-2">
                  <span className="flex items-center"><MapPin className="w-3.5 h-3.5 mr-1" /> {scorecard.region}</span>
                  <span>•</span>
                  <span>Ekin maydoni: <strong>{scorecard.land_hectares} ga</strong></span>
                  <span>•</span>
                  <span>Tuproq boniteti: <strong>{scorecard.soil_bonitet_score} ball</strong></span>
                </div>
              </div>

              {/* Overall Score Badge */}
              <div className="flex items-center space-x-3 bg-slate-50 p-4 rounded-xl border border-slate-100">
                <div className="text-right">
                  <span className="text-xs text-slate-400 block font-semibold">Agro-Credit Score</span>
                  <span className="text-xs font-bold text-indigo-600 block">{scorecard.rating_tier}</span>
                </div>
                <div className="w-14 h-14 rounded-full bg-indigo-600 text-white font-black text-xl flex items-center justify-center shadow-md">
                  {scorecard.credit_score}
                </div>
              </div>
            </div>

            {/* Core Underwriting Indicators */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* DSCR Card */}
              <div className="p-5 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-xs font-semibold text-slate-400 uppercase block">Qarz Qoplami (DSCR)</span>
                <span className="text-2xl font-black text-slate-900 mt-1 block font-mono">
                  {scorecard.dscr}x
                </span>
                <span className="text-xs text-emerald-700 font-medium block mt-1">
                  {scorecard.dscr_assessment}
                </span>
                <p className="text-[11px] text-slate-500 mt-2">
                  Operatsion kassa oqimining joriy kredit to'lovlariga nisbati.
                </p>
              </div>

              {/* Borrowing Capacity */}
              <div className="p-5 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-xs font-semibold text-slate-400 uppercase block">Xavfsiz Qo'shimcha Qarz Sig'imi</span>
                <span className="text-2xl font-black text-indigo-700 mt-1 block font-mono">
                  {formatCompactUZS(scorecard.max_additional_borrowing_capacity_uzs)}
                </span>
                <span className="text-xs text-slate-600 font-medium block mt-1">
                  Tavsiya: {scorecard.recommended_loan_product}
                </span>
                <p className="text-[11px] text-slate-500 mt-2">
                  DSCR koeffitsiyentini 1.25x dan tushirmagan holda jalb qilish mumkin bo'lgan maksimal limit.
                </p>
              </div>

              {/* VMQ-613 Collateral */}
              <div className="p-5 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-xs font-semibold text-slate-400 uppercase block">VMQ-613 Yer Ijarasi Garovi</span>
                <span className="text-2xl font-black text-sky-700 mt-1 block font-mono">
                  {formatCompactUZS(scorecard.vmq613_bankable_collateral_uzs)}
                </span>
                <span className="text-xs text-sky-800 font-medium block mt-1">
                  LTV: 65% (DCF: {formatCompactUZS(scorecard.vmq613_leasehold_estimated_value_uzs)})
                </span>
                <p className="text-[11px] text-slate-500 mt-2">
                  VMQ-613 ga muvofiq yer ijara huquqining bank qabul qilishi mumkin bo'lgan likvid garov qiymati.
                </p>
              </div>
            </div>

            {/* Strengths & Risks */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-5 rounded-xl bg-emerald-50/50 border border-emerald-100">
                <div className="flex items-center space-x-2 text-emerald-800 font-bold text-sm mb-3">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Ijobiy Moliyaviy Omillar</span>
                </div>
                <ul className="space-y-2 text-xs text-slate-700">
                  {scorecard.key_strengths.map((s, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-emerald-500 mr-2">•</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-5 rounded-xl bg-amber-50/50 border border-amber-100">
                <div className="flex items-center space-x-2 text-amber-800 font-bold text-sm mb-3">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <span>Xatarlar va E'tibor Qaratish Zarur Bo'lgan Omillar</span>
                </div>
                <ul className="space-y-2 text-xs text-slate-700">
                  {scorecard.identified_risks.map((r, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-amber-500 mr-2">•</span>
                      <span>{r}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Committee Notes */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs">
              <span className="font-bold text-slate-800 block mb-1">
                Kredit Qo'mitasi Uchun Analitik Xulosa:
              </span>
              <p className="text-slate-600 leading-relaxed">
                {scorecard.credit_committee_readiness_notes}
              </p>
            </div>

            {/* Statutory Disclaimer */}
            <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-[11px] text-slate-500 leading-relaxed">
              <strong>Ogohlantirish:</strong> {scorecard.disclaimer}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default function CreditReportPage() {
  return (
    <Suspense fallback={
      <div className="py-12 text-center bg-slate-50 min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2 text-slate-500 text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-indigo-600" />
          <span>Kredit dosyesi yuklanmoqda...</span>
        </div>
      </div>
    }>
      <CreditReportContent />
    </Suspense>
  );
}
