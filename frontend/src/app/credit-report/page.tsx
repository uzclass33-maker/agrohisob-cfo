'use client';

import React, { useState, useEffect, useMemo, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { 
  fetchScenarios,
  previewCreditDossier,
  generateCreditDossier,
  fetchDocumentReadinessChecklist,
  fetchReportHistory,
  getFullDownloadUrl,
  validateCreditProfileAPI
} from '@/lib/api';
import { 
  CreditDossierData, 
  CreditProfile, 
  DocumentReadinessChecklist, 
  ChecklistItem,
  GeneratedReportRecord, 
  SyntheticScenarioMeta,
  LoanPurpose
} from '@/lib/types';
import { formatUZS, formatCompactUZS } from '@/lib/formatters';
import { 
  ShieldCheck, AlertCircle, FileText, CheckCircle2, 
  Download, Printer, Building2, MapPin, Award, Layers, 
  TrendingUp, AlertTriangle, RefreshCw, FileSpreadsheet, 
  Calendar, Check, X, HelpCircle, ChevronRight, Sliders,
  DollarSign, ArrowDownToLine, Clock, Scale
} from 'lucide-react';

const LOAN_PURPOSES: { value: LoanPurpose; label: string }[] = [
  { value: 'WORKING_CAPITAL', label: "Aylanma mablag'larni to'ldirish (Agro-revolving)" },
  { value: 'AGRICULTURAL_INPUTS', label: "Urug'lik, o'g'it va yoqilg'i sotib olish" },
  { value: 'MACHINERY_EQUIPMENT', label: "Qishloq xo'jaligi texnikasi va agregatlar" },
  { value: 'DRIP_IRRIGATION', label: "Tomchilatib sug'orish tizimi (PQ-47)" },
  { value: 'COLD_STORAGE', label: "Muzlatkichli omborxona qurish" },
  { value: 'BUSINESS_EXPANSION', label: "Ekin maydonlari va faoliyatni kengaytirish" },
  { value: 'OTHER', label: "Boshqa agrar loyihalar" }
];

function CreditReportContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [scenarios, setScenarios] = useState<SyntheticScenarioMeta[]>([]);
  const [selectedOrgId, setSelectedOrgId] = useState<string>(
    searchParams.get('scenario') || 'scenario-small-farmer'
  );
  
  const [dossier, setDossier] = useState<CreditDossierData | null>(null);
  const [profile, setProfile] = useState<CreditProfile | null>(null);
  const [checklist, setChecklist] = useState<DocumentReadinessChecklist | null>(null);
  const [history, setHistory] = useState<GeneratedReportRecord[]>([]);

  const [activeTab, setActiveTab] = useState<'preview' | 'checklist' | 'history'>('preview');
  const [checklistFilter, setChecklistFilter] = useState<'ALL' | 'AVAILABLE' | 'MISSING' | 'NEEDS_REVIEW'>('ALL');
  
  const [loading, setLoading] = useState<boolean>(true);
  const [generating, setGenerating] = useState<boolean>(false);
  const [genMessage, setGenMessage] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [showConfig, setShowConfig] = useState<boolean>(false);

  // Load scenarios on mount
  useEffect(() => {
    async function init() {
      try {
        const scs = await fetchScenarios();
        setScenarios(scs);
      } catch (e) {
        console.error(e);
      }
    }
    init();
  }, []);

  // Fetch Dossier Data, Checklist, and History
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        
        // 1. Fetch live preview
        const data = await previewCreditDossier(selectedOrgId);
        setDossier(data);
        setProfile(data.credit_profile);
        setChecklist(data.checklist);

        // 2. Fetch history
        const hist = await fetchReportHistory(selectedOrgId);
        setHistory(hist);
      } catch (err: any) {
        console.error(err);
        setError(err.message || "Kredit dosye ma'lumotlarini yuklashda xatolik yuz berdi.");
      } finally {
        setLoading(false);
      }
    }

    if (selectedOrgId) {
      loadData();
    }
  }, [selectedOrgId]);

  // Recalculate preview when profile is edited
  const handleApplyProfileChanges = async () => {
    if (!profile) return;
    try {
      setLoading(true);
      setError(null);
      const data = await previewCreditDossier(selectedOrgId, profile);
      setDossier(data);
      setChecklist(data.checklist);
      setShowConfig(false);
    } catch (err: any) {
      setError(err.message || "Profil parametrlarini qayta hisoblashda xatolik.");
    } finally {
      setLoading(false);
    }
  };

  // Generate real PDF & Excel and trigger download
  const handleGenerateAndDownload = async (fileType: 'pdf' | 'xlsx') => {
    try {
      setGenerating(true);
      setGenMessage(fileType === 'pdf' ? "Bank andozasidagi PDF dosye shakllanmoqda..." : "8 varaqli Excel moliyaviy modeli tuzilmoqda...");
      
      const record = await generateCreditDossier(selectedOrgId, profile);
      
      // Update history
      setHistory(prev => [record, ...prev.filter(r => r.report_id !== record.report_id)]);

      // Download file
      const downloadPath = fileType === 'pdf' ? record.pdf_url : record.xlsx_url;
      if (downloadPath) {
        const absoluteUrl = getFullDownloadUrl(downloadPath);
        const link = document.createElement('a');
        link.href = absoluteUrl;
        link.setAttribute('download', '');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
      setGenMessage("Fayl muvaffaqiyatli yuklab olindi!");
      setTimeout(() => setGenMessage(''), 3000);
    } catch (err: any) {
      setError(err.message || "Hisobot faylini yaratishda xatolik yuz berdi.");
    } finally {
      setGenerating(false);
    }
  };

  // Filtered checklist items
  const filteredChecklist = useMemo(() => {
    if (!checklist) return [];
    if (checklistFilter === 'ALL') return checklist.items;
    return checklist.items.filter(i => i.status === checklistFilter);
  }, [checklist, checklistFilter]);

  return (
    <div className="page-shell py-8 lg:py-10">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        
        {/* Top Header & Export Controls */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 bg-white p-6 rounded-xl border border-slate-200/80 shadow-card">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-agro-100 text-agro-800 text-xs font-semibold mb-2">
              <ShieldCheck className="w-3.5 h-3.5 text-agro-700" />
              <span>Professional Bank Dosyesi & Moliyaviy Baholash Tizimi</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-navy-950 tracking-tight">
              Bank Kreditga Tayyorgarlik Dosyesi va Moliyaviy Modeli
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-2xl">
              Tijorat banklari anderraytingi uchun 12 oylik kassa oqimlari, qarzga xizmat ko'rsatish (DSCR), hujjatlar to'liqligi va ssenariylar tahlili.
            </p>
          </div>

          {/* Action Export Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => handleGenerateAndDownload('pdf')}
              disabled={generating || loading}
              className="px-4 py-2.5 bg-navy-900 hover:bg-navy-800 text-white rounded-lg text-xs font-bold shadow-card inline-flex items-center transition disabled:opacity-50"
            >
              <Download className="w-4 h-4 mr-2 text-emerald-400" />
              PDF Dosye Yuklab Olish
            </button>
            <button
              onClick={() => handleGenerateAndDownload('xlsx')}
              disabled={generating || loading}
              className="px-4 py-2.5 bg-agro-700 hover:bg-agro-800 text-white rounded-lg text-xs font-bold shadow-card inline-flex items-center transition disabled:opacity-50"
            >
              <FileSpreadsheet className="w-4 h-4 mr-2" />
              Excel Model Yuklab Olish
            </button>
            <button
              onClick={() => setShowConfig(!showConfig)}
              className="px-3.5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold border border-slate-200 inline-flex items-center transition"
            >
              <Sliders className="w-3.5 h-3.5 mr-1.5" />
              Kredit Shartlari
            </button>
          </div>
        </div>

        {/* Status Message / Notification */}
        {genMessage && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-center space-x-2 animate-fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span className="font-medium">{genMessage}</span>
          </div>
        )}

        {/* Business Entity Switcher */}
        <div className="bg-white p-3 rounded-xl border border-slate-200/80 shadow-card flex flex-wrap gap-2 items-center">
          <span className="text-xs font-bold text-slate-500 uppercase px-2 flex items-center">
            <Building2 className="w-3.5 h-3.5 mr-1" /> Korxona:
          </span>
          {scenarios.map((sc) => (
            <button
              key={sc.id}
              onClick={() => {
                setSelectedOrgId(sc.id);
                router.push(`/credit-report?scenario=${sc.id}`);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                sc.id === selectedOrgId
                  ? 'bg-navy-900 text-white shadow-card'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {sc.name}
            </button>
          ))}
        </div>

        {/* Configurable Credit Parameters Panel (Collapsible) */}
        {showConfig && profile && (
          <div className="bg-white p-6 rounded-xl border border-agro-200 shadow-card space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-bold text-slate-800 flex items-center">
                <Sliders className="w-4 h-4 mr-2 text-emerald-600" />
                So'ralayotgan Kredit Parametrlarini Sozlash
              </h3>
              <span className="text-xs text-slate-500">O'zgartirishlar darhol tahlil modeliga qo'llaniladi</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Kredit Miqdori (UZS)</label>
                <input
                  type="number"
                  step="10000000"
                  value={profile.requested_loan_amount_uzs}
                  onChange={(e) => setProfile({ ...profile, requested_loan_amount_uzs: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Kredit Maqsadi</label>
                <select
                  value={profile.loan_purpose}
                  onChange={(e) => setProfile({ ...profile, loan_purpose: e.target.value as LoanPurpose })}
                  className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                >
                  {LOAN_PURPOSES.map(p => (
                    <option key={p.value} value={p.value}>{p.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Muddati (Oyda)</label>
                <input
                  type="number"
                  min="3"
                  max="120"
                  value={profile.proposed_term_months}
                  onChange={(e) => setProfile({ ...profile, proposed_term_months: parseInt(e.target.value) || 12 })}
                  className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Yillik Foiz Stavkasi (%)</label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  max="50"
                  value={profile.proposed_annual_interest_rate_pct}
                  onChange={(e) => setProfile({ ...profile, proposed_annual_interest_rate_pct: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Qaytarish Sxemasi</label>
                <select
                  value={profile.repayment_structure}
                  onChange={(e) => setProfile({ ...profile, repayment_structure: e.target.value as 'ANNUITY' | 'EQUAL_PRINCIPAL' })}
                  className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="ANNUITY">Annuitet (Teng to'lovlar)</option>
                  <option value="EQUAL_PRINCIPAL">Differensial (Asosiy qarz teng bo'lingan)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Imtiyozli Davr (Asosiy qarzdan, oy)</label>
                <input
                  type="number"
                  min="0"
                  max="24"
                  value={profile.grace_period_months}
                  onChange={(e) => setProfile({ ...profile, grace_period_months: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 font-mono"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setShowConfig(false)}
                className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-800"
              >
                Bekor Qilish
              </button>
              <button
                onClick={handleApplyProfileChanges}
                className="px-4 py-1.5 bg-agro-700 hover:bg-agro-800 text-white rounded-lg text-xs font-bold transition shadow-card"
              >
                Qayta Hisoblash
              </button>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200">
          <button
            onClick={() => setActiveTab('preview')}
            className={`pb-3 px-4 text-xs font-bold border-b-2 transition flex items-center space-x-1.5 ${
              activeTab === 'preview'
                ? 'border-emerald-700 text-emerald-800'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Kredit Dosyesi Ko'rinishi</span>
          </button>
          
          <button
            onClick={() => setActiveTab('checklist')}
            className={`pb-3 px-4 text-xs font-bold border-b-2 transition flex items-center space-x-1.5 ${
              activeTab === 'checklist'
                ? 'border-emerald-700 text-emerald-800'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Hujjatlar Nazorati ({checklist?.completeness_percentage || 0}%)</span>
          </button>

          <button
            onClick={() => setActiveTab('history')}
            className={`pb-3 px-4 text-xs font-bold border-b-2 transition flex items-center space-x-1.5 ${
              activeTab === 'history'
                ? 'border-emerald-700 text-emerald-800'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <Clock className="w-4 h-4" />
            <span>Hisobotlar Tarixi ({history.length})</span>
          </button>
        </div>

        {/* Loading / Error States */}
        {loading ? (
          <div className="p-16 text-center bg-white rounded-xl border border-slate-200 shadow-card">
            <RefreshCw className="w-8 h-8 text-emerald-600 animate-spin mx-auto mb-3" />
            <p className="text-xs font-semibold text-slate-600">Kredit dosyesi va moliyaviy prognoz hisoblanmoqda...</p>
            <p className="text-[11px] text-slate-400 mt-1">Deterministik moliyaviy dvigatel ishlamoqda</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-xs flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
            <div>
              <p className="font-bold">Xatolik aniqlandi</p>
              <p className="mt-1">{error}</p>
            </div>
          </div>
        ) : dossier ? (
          <>
            {/* TAB 1: LIVE DOSSIER PREVIEW */}
            {activeTab === 'preview' && (
              <div className="space-y-6">
                
                {/* 1. Executive Summary & Readiness Scorecard */}
                <div className="bg-white p-6 sm:p-8 rounded-xl border border-slate-200 shadow-card space-y-6">
                  <div className="border-b border-slate-100 pb-5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                      <span className="text-xs font-bold text-emerald-700 uppercase tracking-widest block">
                        1. Ijroiya Xulosa va Kreditga Tayyorgarlik Reytingi
                      </span>
                      <h2 className="text-2xl font-black text-slate-900 mt-1">
                        {dossier.organization_name}
                      </h2>
                      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 mt-2">
                        <span>STIR: <strong>{dossier.credit_profile.inn || 'Mavjud emas'}</strong></span>
                        <span>•</span>
                        <span>Ekin maydoni: <strong>{dossier.credit_profile.land_hectares} ga</strong></span>
                        <span>•</span>
                        <span>Faoliyat: <strong>{dossier.credit_profile.business_activity}</strong></span>
                        <span>•</span>
                        <span>Hisobot: <strong>{dossier.generation_timestamp}</strong></span>
                      </div>
                    </div>

                    {/* Score Badge */}
                    <div className="flex items-center space-x-4 bg-slate-50 p-4 rounded-xl border border-slate-200">
                      <div className="text-right">
                        <span className="text-xs text-slate-400 block font-semibold">Tayyorgarlik Bahosi</span>
                        <span className={`text-xs font-bold block ${
                          dossier.readiness_assessment.readiness_score >= 75 ? 'text-emerald-700' : 'text-amber-700'
                        }`}>
                          {dossier.readiness_assessment.status_label_uz}
                        </span>
                      </div>
                      <div className={`w-14 h-14 rounded-full text-white font-black text-xl flex items-center justify-center shadow-md ${
                        dossier.readiness_assessment.readiness_score >= 75 ? 'bg-emerald-600' : 'bg-amber-600'
                      }`}>
                        {dossier.readiness_assessment.readiness_score}
                      </div>
                    </div>
                  </div>

                  {/* High-Level Financial Snapshot */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                      <span className="text-[11px] text-slate-500 block uppercase font-medium">Prognoz Tushumlar</span>
                      <span className="text-base sm:text-lg font-bold text-slate-900 mt-1 block font-mono">
                        {formatCompactUZS(dossier.forecast_summary.total_annual_inflows)}
                      </span>
                      <span className="text-[10px] text-emerald-600 font-semibold block mt-1">12 oylik reja</span>
                    </div>

                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                      <span className="text-[11px] text-slate-500 block uppercase font-medium">Prognoz Chiqimlar</span>
                      <span className="text-base sm:text-lg font-bold text-slate-900 mt-1 block font-mono">
                        {formatCompactUZS(dossier.forecast_summary.total_annual_outflows)}
                      </span>
                      <span className="text-[10px] text-slate-500 block mt-1">Opex + Qarz</span>
                    </div>

                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                      <span className="text-[11px] text-slate-500 block uppercase font-medium">Birlashgan DSCR</span>
                      <span className="text-base sm:text-lg font-bold text-indigo-700 mt-1 block font-mono">
                        {dossier.debt_dscr_summary.combined_dscr ? `${dossier.debt_dscr_summary.combined_dscr}x` : '—'}
                      </span>
                      <span className="text-[10px] text-slate-600 block mt-1">
                        {dossier.debt_dscr_summary.combined_dscr && dossier.debt_dscr_summary.combined_dscr >= 1.25 ? 'Barqaror qoplash' : 'Diqqat talab'}
                      </span>
                    </div>

                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                      <span className="text-[11px] text-slate-500 block uppercase font-medium">Hujjatlar To'liqligi</span>
                      <span className="text-base sm:text-lg font-bold text-emerald-700 mt-1 block font-mono">
                        {dossier.checklist.completeness_percentage}%
                      </span>
                      <span className="text-[10px] text-slate-500 block mt-1">
                        {dossier.checklist.available_count} / {dossier.checklist.total_items} ta mavjud
                      </span>
                    </div>
                  </div>

                  {/* Strengths & Risks */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                    <div className="p-5 rounded-xl bg-emerald-50/60 border border-emerald-100">
                      <div className="flex items-center space-x-2 text-emerald-800 font-bold text-xs mb-3">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span>Kreditga Tayyorgarlikning Asosiy Kuchli Tomonlari</span>
                      </div>
                      <ul className="space-y-2 text-xs text-slate-700">
                        {dossier.readiness_assessment.key_strengths_uz.map((st, i) => (
                          <li key={i} className="flex items-start">
                            <span className="text-emerald-600 font-bold mr-2">•</span>
                            <span>{st}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="p-5 rounded-xl bg-amber-50/60 border border-amber-100">
                      <div className="flex items-center space-x-2 text-amber-800 font-bold text-xs mb-3">
                        <AlertTriangle className="w-4 h-4 text-amber-600" />
                        <span>Aniqlangan Moliyaviy Xatarlar va Kamchiliklar</span>
                      </div>
                      <ul className="space-y-2 text-xs text-slate-700">
                        {dossier.readiness_assessment.identified_risks_uz.map((rk, i) => (
                          <li key={i} className="flex items-start">
                            <span className="text-amber-600 font-bold mr-2">•</span>
                            <span>{rk}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>

                {/* 2. Historical Financial Analysis */}
                <div className="bg-white p-6 sm:p-8 rounded-xl border border-slate-200 shadow-card space-y-4">
                  <span className="text-xs font-bold text-emerald-700 uppercase tracking-widest block">
                    2. Tarixiy Moliyaviy Ko'rsatkichlar Tahlili (O'tgan 12 oy)
                  </span>
                  <p className="text-xs text-slate-600">
                    Birlamchi hisob-kitoblar va bank ko'chirmalari asosidagi oylik pul oqimi dinamikasi:
                  </p>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left text-slate-700 border border-slate-200 rounded-lg">
                      <thead className="bg-slate-100 text-slate-800 font-bold uppercase text-[11px]">
                        <tr>
                          <th className="py-2.5 px-3 border-b">Oy</th>
                          <th className="py-2.5 px-3 border-b text-right">Boshlang'ich Qoldiq</th>
                          <th className="py-2.5 px-3 border-b text-right">Tushumlar</th>
                          <th className="py-2.5 px-3 border-b text-right">Chiqimlar</th>
                          <th className="py-2.5 px-3 border-b text-right">Sof Oqim (Net)</th>
                          <th className="py-2.5 px-3 border-b text-right">Yakuniy Qoldiq</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dossier.historical_summary.monthly_data.map((m) => (
                          <tr key={m.month_number} className="border-b hover:bg-slate-50">
                            <td className="py-2 px-3 font-semibold">{m.month_name}</td>
                            <td className="py-2 px-3 text-right font-mono">{formatUZS(m.opening_balance)}</td>
                            <td className="py-2 px-3 text-right font-mono text-emerald-700">+{formatUZS(m.inflows)}</td>
                            <td className="py-2 px-3 text-right font-mono text-rose-700">-{formatUZS(m.outflows)}</td>
                            <td className={`py-2 px-3 text-right font-mono font-bold ${m.net_cash_flow >= 0 ? 'text-emerald-700' : 'text-rose-600'}`}>
                              {formatUZS(m.net_cash_flow)}
                            </td>
                            <td className={`py-2 px-3 text-right font-mono font-semibold ${m.closing_balance < 0 ? 'text-rose-700 bg-rose-50' : 'text-slate-900'}`}>
                              {formatUZS(m.closing_balance)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                      <tfoot className="bg-slate-100 font-bold text-slate-900">
                        <tr>
                          <td className="py-2.5 px-3">Yillik Jami:</td>
                          <td className="py-2.5 px-3 text-right font-mono">{formatUZS(dossier.historical_summary.initial_opening_balance)}</td>
                          <td className="py-2.5 px-3 text-right font-mono text-emerald-800">+{formatUZS(dossier.historical_summary.total_inflows)}</td>
                          <td className="py-2.5 px-3 text-right font-mono text-rose-800">-{formatUZS(dossier.historical_summary.total_outflows)}</td>
                          <td className="py-2.5 px-3 text-right font-mono text-indigo-800">{formatUZS(dossier.historical_summary.net_cash_flow)}</td>
                          <td className="py-2.5 px-3 text-right font-mono">{formatUZS(dossier.historical_summary.final_closing_balance)}</td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>

                {/* 3. 12-Month Seasonal Forecast */}
                <div className="bg-white p-6 sm:p-8 rounded-xl border border-slate-200 shadow-card space-y-4">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                    <div>
                      <span className="text-xs font-bold text-emerald-700 uppercase tracking-widest block">
                        3. 12 Oylik Mavsumiy Kassa Prognozi (2026-yil)
                      </span>
                      <p className="text-xs text-slate-600">
                        Agrotexnik bosqichlar, hosil terimi va sotuv davrlariga bog'langan pul oqimi:
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-[11px] text-slate-500 block">Eng past kassa nuqtasi (Gap):</span>
                      <span className={`text-xs font-bold font-mono ${dossier.forecast_summary.lowest_cash_point < 0 ? 'text-rose-600' : 'text-emerald-700'}`}>
                        {formatUZS(dossier.forecast_summary.lowest_cash_point)} ({dossier.forecast_summary.lowest_cash_month})
                      </span>
                    </div>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left text-slate-700 border border-slate-200 rounded-lg">
                      <thead className="bg-slate-100 text-slate-800 font-bold uppercase text-[11px]">
                        <tr>
                          <th className="py-2.5 px-3 border-b">Oy</th>
                          <th className="py-2.5 px-3 border-b text-right">Prognoz Tushum</th>
                          <th className="py-2.5 px-3 border-b text-right">Operatsion Chiqim</th>
                          <th className="py-2.5 px-3 border-b text-right">Qarz Xizmati</th>
                          <th className="py-2.5 px-3 border-b text-right">CFADS (Qarzgacha)</th>
                          <th className="py-2.5 px-3 border-b text-right">Yakuniy Kassa</th>
                          <th className="py-2.5 px-3 border-b text-center">Oylik DSCR</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dossier.forecast_summary.monthly_forecast.map((m) => (
                          <tr key={m.month_number} className="border-b hover:bg-slate-50">
                            <td className="py-2 px-3 font-semibold">{m.month_name}</td>
                            <td className="py-2 px-3 text-right font-mono text-emerald-700">+{formatUZS(m.inflows)}</td>
                            <td className="py-2 px-3 text-right font-mono text-slate-600">-{formatUZS(m.operating_outflows)}</td>
                            <td className="py-2 px-3 text-right font-mono text-rose-600">-{formatUZS(m.debt_service)}</td>
                            <td className="py-2 px-3 text-right font-mono font-semibold text-slate-800">{formatUZS(m.cfads)}</td>
                            <td className={`py-2 px-3 text-right font-mono font-bold ${m.closing_balance < 0 ? 'text-rose-600 bg-rose-50' : 'text-slate-900'}`}>
                              {formatUZS(m.closing_balance)}
                            </td>
                            <td className="py-2 px-3 text-center font-mono font-semibold">
                              {m.monthly_dscr !== null ? `${m.monthly_dscr}x` : '—'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                      <tfoot className="bg-slate-100 font-bold text-slate-900">
                        <tr>
                          <td className="py-2.5 px-3">Yillik Jami:</td>
                          <td className="py-2.5 px-3 text-right font-mono text-emerald-800">+{formatUZS(dossier.forecast_summary.total_annual_inflows)}</td>
                          <td className="py-2.5 px-3 text-right font-mono text-slate-800">
                            -{formatUZS(dossier.forecast_summary.total_annual_outflows - dossier.debt_dscr_summary.existing_annual_debt_service)}
                          </td>
                          <td className="py-2.5 px-3 text-right font-mono text-rose-800">-{formatUZS(dossier.debt_dscr_summary.existing_annual_debt_service)}</td>
                          <td className="py-2.5 px-3 text-right font-mono text-indigo-800">
                            {formatUZS(dossier.forecast_summary.total_annual_inflows - (dossier.forecast_summary.total_annual_outflows - dossier.debt_dscr_summary.existing_annual_debt_service))}
                          </td>
                          <td className="py-2.5 px-3 text-right font-mono">{formatUZS(dossier.forecast_summary.final_closing_balance)}</td>
                          <td className="py-2.5 px-3 text-center font-mono text-indigo-700">
                            {dossier.debt_dscr_summary.standalone_dscr ? `${dossier.debt_dscr_summary.standalone_dscr}x` : '—'}
                          </td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>

                {/* 4. Debt & DSCR Analysis */}
                <div className="bg-white p-6 sm:p-8 rounded-xl border border-slate-200 shadow-card space-y-6">
                  <div>
                    <span className="text-xs font-bold text-emerald-700 uppercase tracking-widest block">
                      4. Qarz Yuklamasi va DSCR Qoplash Tahlili
                    </span>
                    <p className="text-xs text-slate-600 mt-1">
                      So'ralayotgan yangi kredit va mavjud majburiyatlarning yillik qoplash ko'rsatkichlari:
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                      <span className="text-xs text-slate-500 uppercase font-semibold block">So'ralayotgan Kredit</span>
                      <span className="text-xl font-black text-slate-900 mt-1 block font-mono">
                        {formatUZS(dossier.debt_dscr_summary.requested_principal)}
                      </span>
                      <p className="text-xs text-slate-600 mt-2">
                        Muddati: <strong>{dossier.debt_dscr_summary.requested_term_months} oy</strong> | Foiz: <strong>{dossier.debt_dscr_summary.annual_interest_rate_pct}%</strong>
                      </p>
                      <p className="text-xs text-slate-500 mt-1">
                        Imtiyozli davr: <strong>{dossier.debt_dscr_summary.grace_period_months} oy</strong> ({dossier.debt_dscr_summary.repayment_structure})
                      </p>
                    </div>

                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                      <span className="text-xs text-slate-500 uppercase font-semibold block">Birinchi Yil Yangi Xizmat</span>
                      <span className="text-xl font-black text-indigo-700 mt-1 block font-mono">
                        {formatUZS(dossier.debt_dscr_summary.first_year_new_loan_service)}
                      </span>
                      <p className="text-xs text-slate-600 mt-2">
                        Mavjud qarz xizmati: <strong>{formatUZS(dossier.debt_dscr_summary.existing_annual_debt_service)}</strong>
                      </p>
                      <p className="text-xs text-slate-800 font-semibold mt-1">
                        Jami birlashgan xizmat: <strong>{formatUZS(dossier.debt_dscr_summary.combined_annual_debt_service)}</strong>
                      </p>
                    </div>

                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                      <span className="text-xs text-slate-500 uppercase font-semibold block">Kombinatsiyalangan DSCR</span>
                      <span className="text-xl font-black text-emerald-700 mt-1 block font-mono">
                        {dossier.debt_dscr_summary.combined_dscr ? `${dossier.debt_dscr_summary.combined_dscr}x` : '—'}
                      </span>
                      <p className="text-xs text-emerald-800 font-medium mt-2">
                        Tavsiya me'yori: &gt;= 1.25x
                      </p>
                      <p className="text-[11px] text-slate-500 mt-1 font-mono">
                        {dossier.debt_dscr_summary.dscr_formula}
                      </p>
                    </div>
                  </div>

                  {/* Amortization Schedule Preview */}
                  <div>
                    <h4 className="text-xs font-bold text-slate-800 uppercase mb-2">
                      So'ralayotgan Kredit To'lov Grafigi (Dastlabki 12 oy ko'rinishi)
                    </h4>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs text-left text-slate-700 border border-slate-200 rounded-lg">
                        <thead className="bg-slate-100 text-slate-800 font-bold uppercase text-[11px]">
                          <tr>
                            <th className="py-2 px-3 border-b">Oy #</th>
                            <th className="py-2 px-3 border-b text-right">Boshlang'ich Qarz</th>
                            <th className="py-2 px-3 border-b text-right">Asosiy Qarz To'lovi</th>
                            <th className="py-2 px-3 border-b text-right">Foiz To'lovi</th>
                            <th className="py-2 px-3 border-b text-right">Jami Oylik To'lov</th>
                            <th className="py-2 px-3 border-b text-right">Qoldiq Asosiy Qarz</th>
                          </tr>
                        </thead>
                        <tbody>
                          {dossier.debt_dscr_summary.amortization_schedule.map((row) => (
                            <tr key={row.period} className="border-b hover:bg-slate-50">
                              <td className="py-2 px-3 font-semibold">{row.period}-oy</td>
                              <td className="py-2 px-3 text-right font-mono">{formatUZS(row.opening_principal)}</td>
                              <td className="py-2 px-3 text-right font-mono text-emerald-700">{formatUZS(row.principal_paid)}</td>
                              <td className="py-2 px-3 text-right font-mono text-amber-700">{formatUZS(row.interest_paid)}</td>
                              <td className="py-2 px-3 text-right font-mono font-bold text-indigo-700">{formatUZS(row.total_payment)}</td>
                              <td className="py-2 px-3 text-right font-mono">{formatUZS(row.remaining_principal)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

                {/* 5. Risk & Scenario Analysis */}
                <div className="bg-white p-6 sm:p-8 rounded-xl border border-slate-200 shadow-card space-y-4">
                  <span className="text-xs font-bold text-emerald-700 uppercase tracking-widest block">
                    5. Xatarlar va Stress-Ssenariylar Tahlili
                  </span>
                  <p className="text-xs text-slate-600">
                    Bozor va agrar shoklar holatida korxonaning to'lov qobiliyati (DSCR va yakuniy kassa qoldig'i):
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                      <span className="text-xs font-bold text-slate-800 uppercase block">1. Bazaviy Ssenariy</span>
                      <div className="mt-3 space-y-1 text-xs">
                        <div className="flex justify-between"><span>Yalpi tushum:</span><span className="font-mono font-bold">{formatCompactUZS(dossier.risks_scenarios_summary.base.inflows)}</span></div>
                        <div className="flex justify-between"><span>Yalpi chiqim:</span><span className="font-mono">{formatCompactUZS(dossier.risks_scenarios_summary.base.outflows)}</span></div>
                        <div className="flex justify-between"><span>DSCR koeffitsienti:</span><span className="font-mono font-bold text-emerald-700">{dossier.risks_scenarios_summary.base.dscr}x</span></div>
                        <div className="flex justify-between"><span>Kassa uzilishi (oy):</span><span className="font-mono">{dossier.risks_scenarios_summary.base.deficits} oy</span></div>
                      </div>
                    </div>

                    <div className="p-4 bg-emerald-50/50 rounded-xl border border-emerald-200">
                      <span className="text-xs font-bold text-emerald-800 uppercase block">2. Optimistik Ssenariy</span>
                      <div className="mt-3 space-y-1 text-xs">
                        <div className="flex justify-between"><span>Yalpi tushum:</span><span className="font-mono font-bold text-emerald-800">{formatCompactUZS(dossier.risks_scenarios_summary.optimistic.inflows)}</span></div>
                        <div className="flex justify-between"><span>DSCR koeffitsienti:</span><span className="font-mono font-bold text-emerald-700">{dossier.risks_scenarios_summary.optimistic.dscr}x</span></div>
                        <div className="flex justify-between"><span>Kassa farqi:</span><span className="font-mono text-emerald-700">+{formatCompactUZS(dossier.risks_scenarios_summary.optimistic.variance_closing)}</span></div>
                      </div>
                    </div>

                    <div className="p-4 bg-rose-50/50 rounded-xl border border-rose-200">
                      <span className="text-xs font-bold text-rose-800 uppercase block">3. Pessimistik (Stress)</span>
                      <div className="mt-3 space-y-1 text-xs">
                        <div className="flex justify-between"><span>Yalpi tushum:</span><span className="font-mono font-bold text-rose-800">{formatCompactUZS(dossier.risks_scenarios_summary.pessimistic.inflows)}</span></div>
                        <div className="flex justify-between"><span>DSCR koeffitsienti:</span><span className="font-mono font-bold text-rose-700">{dossier.risks_scenarios_summary.pessimistic.dscr}x</span></div>
                        <div className="flex justify-between"><span>Kassa farqi:</span><span className="font-mono text-rose-700">{formatCompactUZS(dossier.risks_scenarios_summary.pessimistic.variance_closing)}</span></div>
                        <p className="text-[11px] text-rose-700 font-semibold mt-2">{dossier.risks_scenarios_summary.pessimistic.solvency_impact}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 6. Statutory Disclaimer Box */}
                <div className="p-5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 leading-relaxed space-y-2">
                  <div className="flex items-center space-x-2 font-bold text-amber-950">
                    <Scale className="w-4 h-4 text-amber-700 flex-shrink-0" />
                    <span>RASMIY OGOHLANTIRISH VA HUQUQIY CHEKLOV</span>
                  </div>
                  <p>{dossier.regulatory_disclaimer_uz}</p>
                </div>
              </div>
            )}

            {/* TAB 2: DOCUMENT READINESS CHECKLIST */}
            {activeTab === 'checklist' && (
              <div className="bg-white p-6 sm:p-8 rounded-xl border border-slate-200 shadow-card space-y-6">
                <div>
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                    <div>
                      <span className="text-xs font-bold text-emerald-700 uppercase tracking-widest block">
                        Kreditga Tayyorgarlik Hujjatlar Nazorat Ro'yxati
                      </span>
                      <h3 className="text-xl font-bold text-slate-900 mt-1">
                        Bank Anderraytingi Uchun Talab Qilinuvchi Hujjatlar Holati
                      </h3>
                    </div>
                    <div className="text-right">
                      <span className="text-2xl font-black text-emerald-700 font-mono">
                        {checklist?.completeness_percentage}%
                      </span>
                      <span className="text-xs text-slate-500 block">Ma'lumotlar To'liqligi</span>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden mt-4">
                    <div 
                      className="bg-emerald-600 h-full transition-all duration-500 rounded-full"
                      style={{ width: `${checklist?.completeness_percentage || 0}%` }}
                    />
                  </div>
                </div>

                {/* Filter Pills */}
                <div className="flex flex-wrap gap-2 pt-2">
                  <button
                    onClick={() => setChecklistFilter('ALL')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                      checklistFilter === 'ALL' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    Barchasi ({checklist?.total_items})
                  </button>
                  <button
                    onClick={() => setChecklistFilter('AVAILABLE')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                      checklistFilter === 'AVAILABLE' ? 'bg-emerald-700 text-white' : 'bg-emerald-50 text-emerald-800 hover:bg-emerald-100'
                    }`}
                  >
                    Mavjud ({checklist?.available_count})
                  </button>
                  <button
                    onClick={() => setChecklistFilter('MISSING')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                      checklistFilter === 'MISSING' ? 'bg-rose-700 text-white' : 'bg-rose-50 text-rose-800 hover:bg-rose-100'
                    }`}
                  >
                    Yetishmaydi ({checklist?.missing_count})
                  </button>
                  <button
                    onClick={() => setChecklistFilter('NEEDS_REVIEW')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                      checklistFilter === 'NEEDS_REVIEW' ? 'bg-amber-700 text-white' : 'bg-amber-50 text-amber-800 hover:bg-amber-100'
                    }`}
                  >
                    Qayta Ko'rish Zarur ({checklist?.needs_review_count})
                  </button>
                </div>

                {/* Checklist Items Table */}
                <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden">
                  {filteredChecklist.map((item) => (
                    <div key={item.id} className="p-4 hover:bg-slate-50 transition flex items-start justify-between gap-4">
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-[10px] uppercase font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                            {item.category_title_uz}
                          </span>
                          {item.is_critical && (
                            <span className="text-[10px] uppercase font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded">
                              Majburiy
                            </span>
                          )}
                        </div>
                        <h4 className="text-xs font-bold text-slate-900">{item.title_uz}</h4>
                        <p className="text-xs text-slate-500 leading-relaxed">{item.rationale_uz}</p>
                      </div>

                      <div className="flex-shrink-0">
                        {item.status === 'AVAILABLE' ? (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                            <Check className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                            Mavjud
                          </span>
                        ) : item.status === 'MISSING' ? (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800">
                            <X className="w-3.5 h-3.5 mr-1 text-rose-600" />
                            Yetishmaydi
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800">
                            <HelpCircle className="w-3.5 h-3.5 mr-1 text-amber-600" />
                            Qayta ko'rish zarur
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-[11px] text-slate-500">
                  {checklist?.disclaimer_uz}
                </div>
              </div>
            )}

            {/* TAB 3: REPORT GENERATION HISTORY & DOWNLOADS */}
            {activeTab === 'history' && (
              <div className="bg-white p-6 sm:p-8 rounded-xl border border-slate-200 shadow-card space-y-6">
                <div>
                  <span className="text-xs font-bold text-emerald-700 uppercase tracking-widest block">
                    Avval Yaratilgan Hisobotlar Tarixi
                  </span>
                  <h3 className="text-xl font-bold text-slate-900 mt-1">
                    PDF va Excel Fayllari Reestri
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Barcha hisobotlar SHA-256 kriptografik xesh-kodi bilan saqlanadi va qayta yuklab olish mumkin:
                  </p>
                </div>

                {history.length === 0 ? (
                  <div className="p-8 text-center border border-dashed border-slate-300 rounded-xl">
                    <Clock className="w-6 h-6 text-slate-400 mx-auto mb-2" />
                    <p className="text-xs text-slate-500">Ushbu korxona uchun hali rasmiy hisobot generatsiya qilinmagan.</p>
                    <button
                      onClick={() => handleGenerateAndDownload('pdf')}
                      className="mt-3 px-4 py-2 bg-emerald-700 text-white rounded-lg text-xs font-bold hover:bg-emerald-800 transition"
                    >
                      Dastlabki Hisobotni Yaratish
                    </button>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left text-slate-700 border border-slate-200 rounded-lg">
                      <thead className="bg-slate-100 text-slate-800 font-bold uppercase text-[11px]">
                        <tr>
                          <th className="py-2.5 px-3 border-b">Hisobot ID</th>
                          <th className="py-2.5 px-3 border-b">Yaratilgan Vaqt</th>
                          <th className="py-2.5 px-3 border-b">Fayl Hajmi</th>
                          <th className="py-2.5 px-3 border-b">SHA-256 Nazorat Kesh</th>
                          <th className="py-2.5 px-3 border-b text-right">Yuklab Olish</th>
                        </tr>
                      </thead>
                      <tbody>
                        {history.map((rep) => (
                          <tr key={rep.report_id} className="border-b hover:bg-slate-50">
                            <td className="py-2.5 px-3 font-semibold font-mono text-slate-900">
                              {rep.report_id}
                            </td>
                            <td className="py-2.5 px-3 text-slate-600">
                              {rep.created_at.slice(0, 19).replace('T', ' ')}
                            </td>
                            <td className="py-2.5 px-3 text-slate-600 font-mono">
                              PDF: {Math.round((rep.file_size_bytes_pdf || 0) / 1024)} KB | XLSX: {Math.round((rep.file_size_bytes_xlsx || 0) / 1024)} KB
                            </td>
                            <td className="py-2.5 px-3 font-mono text-[10px] text-slate-400">
                              {rep.file_hash ? rep.file_hash.slice(0, 16) + '...' : '—'}
                            </td>
                            <td className="py-2.5 px-3 text-right space-x-2">
                              {rep.pdf_url && (
                                <a
                                  href={getFullDownloadUrl(rep.pdf_url)}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded text-[11px] font-semibold transition"
                                >
                                  <Download className="w-3 h-3 mr-1 text-emerald-400" />
                                  PDF
                                </a>
                              )}
                              {rep.xlsx_url && (
                                <a
                                  href={getFullDownloadUrl(rep.xlsx_url)}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center px-2.5 py-1 bg-agro-700 hover:bg-agro-800 text-white rounded text-[11px] font-semibold transition"
                                >
                                  <FileSpreadsheet className="w-3 h-3 mr-1" />
                                  Excel
                                </a>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </>
        ) : null}
      </div>
    </div>
  );
}

export default function CreditReportPage() {
  return (
    <Suspense fallback={
      <div className="py-12 text-center bg-canvas min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2 text-slate-500 text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
          <span>Kredit dosyesi yuklanmoqda...</span>
        </div>
      </div>
    }>
      <CreditReportContent />
    </Suspense>
  );
}
