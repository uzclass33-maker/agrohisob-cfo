'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { supabase } from '@/lib/supabaseClient';
import { 
  UploadCloud, FileSpreadsheet, CheckCircle2, Shield, 
  AlertCircle, ArrowRight, FileCheck, Layers, Info, 
  RefreshCw, Check, AlertTriangle, XCircle, Copy, ArrowDownRight, ArrowUpRight
} from 'lucide-react';
import { 
  uploadImportFile, 
  commitImportBatch, 
  fetchImportHistory,
  overrideBatchRow,
  updateBatchMapping,
  loginAsDemoSession,
  getStoredDemoUser,
  getAuthToken,
  logoutDemoSession
} from '@/lib/api';

interface RowData {
  row_id: string;
  row_index: number;
  raw_data: Record<string, any>;
  normalized?: {
    transaction_date: string;
    amount: number;
    direction: 'INFLOW' | 'OUTFLOW';
    counterparty_name: string;
    counterparty_inn?: string;
    document_number?: string;
    purpose?: string;
    mxik_code?: string;
    vat_amount?: number;
  };
  validation_status: 'VALID' | 'WARNING' | 'ERROR' | 'DUPLICATE' | 'NEEDS_REVIEW';
  validation_messages: string[];
  classification?: {
    category: string;
    category_name_uz: string;
    confidence: number;
    rule_source: string;
    applied_rule?: string;
  };
  fingerprint?: string;
  is_duplicate?: boolean;
}

interface MappingItem {
  source_header: string;
  target_field: string;
  confidence: number;
  sample_values: string[];
}

interface BatchPreview {
  batch_id: string;
  file_name: string;
  file_hash_sha256: string;
  document_type: 'E_FAKTURA' | 'BANK_STATEMENT';
  total_rows: number;
  valid_rows: number;
  warning_rows: number;
  error_rows: number;
  duplicate_rows: number;
  total_inflow: number;
  total_outflow: number;
  net_flow: number;
  detected_mappings: MappingItem[];
  rows: RowData[];
  accounting_notice: string;
}

const CATEGORY_OPTIONS = [
  { value: 'CROP_SALES_GRAIN', label: "G'alla va don ekinlari sotuvi" },
  { value: 'CROP_SALES_COTTON', label: "Paxta xomashyosi sotuvi" },
  { value: 'CROP_SALES_HORTICULTURE', label: "Meva va sabzavotlar sotuvi" },
  { value: 'FERTILIZER_CHEMICALS', label: "Mineral o'g'itlar va agroximiya" },
  { value: 'FUEL_LUBRICANTS', label: "Dizel va yoqilg'i-moylash (GSM)" },
  { value: 'SEEDS_SEEDLINGS', label: "Urug'lik va ko'chatlar" },
  { value: 'MACHINERY_SERVICES', label: "Texnika ijarasi va mexanizatsiya" },
  { value: 'LABOR_PAYROLL', label: "Ish haqi va terimchilar xarajati" },
  { value: 'IRRIGATION_WATER', label: "Sug'orish suvi va gidrotexnika" },
  { value: 'LAND_LEASE', label: "Yer ijarasi va kadastr to'lovlari" },
  { value: 'TAXES_DUTIES', label: "Yagona yer solig'i va majburiy to'lovlar" },
  { value: 'DEBT_SERVICE', label: "Bank kredit foiz va asosiy qarz to'lovi" },
  { value: 'SUBSIDY_GRANTS', label: "Davlat subsidiyalari va grantlar" },
  { value: 'OTHER_OPERATING_EXPENSES', label: "Boshqa operatsion xarajatlar" },
  { value: 'OTHER_OPERATING_INCOME', label: "Boshqa operatsion tushumlar" },
];

export default function DataImportPage() {
  const [docType, setDocType] = useState<'E_FAKTURA' | 'BANK_STATEMENT'>('BANK_STATEMENT');
  const [zeroRetention, setZeroRetention] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [preview, setPreview] = useState<BatchPreview | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [commitResult, setCommitResult] = useState<any | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(true);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    async function syncAuth() {
      try {
        const { data } = await supabase.auth.getSession();
        if (data?.session?.user?.email) {
          setIsAuthenticated(true);
          setUserEmail(data.session.user.email);
          return;
        }
      } catch {}

      const demoUser = getStoredDemoUser();
      if (demoUser?.email) {
        setIsAuthenticated(true);
        setUserEmail(demoUser.email);
        return;
      }

      setIsAuthenticated(false);
      setUserEmail(null);
    }

    syncAuth();

    const { data: authListener } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.user?.email) {
        setIsAuthenticated(true);
        setUserEmail(session.user.email);
      } else {
        const demoUser = getStoredDemoUser();
        if (demoUser?.email) {
          setIsAuthenticated(true);
          setUserEmail(demoUser.email);
        } else {
          setIsAuthenticated(false);
          setUserEmail(null);
        }
      }
    });

    const handleCustomAuthChange = () => {
      syncAuth();
      loadHistory();
    };
    window.addEventListener('agrohisob_auth_change', handleCustomAuthChange);

    loadHistory();

    return () => {
      authListener?.subscription?.unsubscribe();
      window.removeEventListener('agrohisob_auth_change', handleCustomAuthChange);
    };
  }, []);

  async function loadHistory() {
    try {
      const hist = await fetchImportHistory('demo-org-agro-01');
      setHistory(hist || []);
    } catch {
      // Fallback
    }
  }

  async function handleQuickDemoLogin() {
    setLoading(true);
    setErrorMessage(null);
    try {
      const res = await loginAsDemoSession();
      setIsAuthenticated(true);
      setUserEmail(res.user.email);
      await loadHistory();
    } catch (err: any) {
      setErrorMessage(err.message || "Demo profilga ulanishda xatolik yuz berdi.");
    } finally {
      setLoading(false);
    }
  }

  // Handle actual file upload
  async function handleFileUpload(file: File) {
    setLoading(true);
    setErrorMessage(null);
    setCommitResult(null);

    // If not authenticated, automatically acquire demo session for demo-org-agro-01
    const token = await getAuthToken('demo-org-agro-01');
    if (!token) {
      try {
        const demoRes = await loginAsDemoSession();
        setIsAuthenticated(true);
        setUserEmail(demoRes.user.email);
      } catch {}
    }

    try {
      const data = await uploadImportFile(file, docType, 'demo-org-agro-01');
      setPreview(data);
    } catch (err: any) {
      if (err?.isSessionExpired || err?.isAuthError || err?.status === 401 || err?.message?.includes("token") || err?.message?.includes("Autentifikatsiya")) {
        setErrorMessage("Autentifikatsiya talab etiladi: Hujjatlarni yuklash va buxgalteriya reestriga kiritish uchun Bosh buxgalter yoki Demo CFO profiliga kiring.");
        setIsAuthenticated(false);
      } else {
        setErrorMessage(err.detail || err.message || 'Faylni yuklashda xatolik yuz berdi');
      }
    } finally {
      setLoading(false);
    }
  }

  // Generate and upload sample synthetic file
  async function handleLoadSample(type: 'E_FAKTURA' | 'BANK_STATEMENT') {
    setDocType(type);
    setLoading(true);
    setErrorMessage(null);
    setCommitResult(null);

    // Auto-ensure demo session if not already logged in
    const token = await getAuthToken('demo-org-agro-01');
    if (!token) {
      try {
        const demoRes = await loginAsDemoSession();
        setIsAuthenticated(true);
        setUserEmail(demoRes.user.email);
      } catch {}
    }

    try {
      let file: File;
      if (type === 'BANK_STATEMENT') {
        const csvContent = 
`Sana;Debet;Kredit;Kontragent;INN;Hujjat raqami;To'lov maqsadi
2026-03-12;28000000;;Farg'onaAzot AJ;200025114;PP-101;Mineral o'g'it ammofos va selitra xaridi uchun
2026-03-24;18500000;;O'zbekneftgaz YoQSh;200115542;PP-102;Dizel yoqilg'isi solyarka uchun to'lov
2026-04-10;12000000;;Urug'chilik Klasteri;204551234;PP-103;Bug'doy va g'alla elita urug'lik xaridi
2026-06-18;;85000000;O'zdonmahsulot filial;302998877;PO-201;G'alla hosili topshirishdan tushum
2026-07-22;;160000000;Toshkent Agro Klaster;305112233;PO-202;Paxta xomashyosi topshirishdan tushum
2026-08-05;9500000;;Agrobank ATB;200000001;PP-104;Kredit asosiy qarz va foiz to'lovi
2026-09-10;4200000;;Davlat Soliq Boshqarmasi;201122334;PP-105;Yagona yer solig'i to'lovi`;
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        file = new File([blob], `namuna_bank_statement_${Date.now()}.csv`, { type: 'text/csv' });
      } else {
        const csvContent = 
`Sana;Faktura raqami;Yetkazib beruvchi;Xaridor;Yetkazib beruvchi STIR;Xaridor STIR;MXIK kodi;Tovar va xizmatlar tavsifi;Summa;QQS summasi
2026-03-15;SF-2026/0114;Farg'onaAzot AJ;AgroBaraka Farm MChJ;200025114;309876543;20.15.10.101;Karbamid va ammofos mineral o'g'itlari;28000000;3360000
2026-03-22;SF-2026/0290;O'zbekneftgaz YoQSh;AgroBaraka Farm MChJ;200115542;309876543;19.20.21.000;Dizel yoqilg'isi E-5 (solyarka);18500000;2220000
2026-04-05;SF-2026/0441;MTP Agrotexnika Servis MChJ;AgroBaraka Farm MChJ;205667788;309876543;01.61.10.000;Traktor haydov va kultivatsiya xizmatlari;14000000;1680000
2026-07-28;SF-2026/0890;AgroBaraka Farm MChJ;Toshkent Agro Klaster MChJ;309876543;305112233;01.16.11.000;Paxta xomashyosi 1-nav;160000000;19200000
2026-08-15;SF-2026/1012;AgroBaraka Farm MChJ;O'zdonmahsulot AJ;309876543;302998877;01.11.12.000;Oziq-ovqat bug'doyi 3-sinf;95000000;11400000`;
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        file = new File([blob], `namuna_soliq_efaktura_${Date.now()}.csv`, { type: 'text/csv' });
      }

      const data = await uploadImportFile(file, type, 'demo-org-agro-01');
      setPreview(data);
    } catch (err: any) {
      setErrorMessage(err.message || 'Namunaviy faylni yuklashda xatolik');
    } finally {
      setLoading(false);
    }
  }

  // Handle Category Override
  async function handleCategoryChange(rowId: string, newCategory: string) {
    if (!preview) return;
    try {
      const updated = await overrideBatchRow(preview.batch_id, rowId, { category: newCategory });
      setPreview({
        ...preview,
        rows: preview.rows.map(r => r.row_id === rowId ? { ...r, classification: updated.classification } : r)
      });
    } catch {
      // Local fallback
      setPreview({
        ...preview,
        rows: preview.rows.map(r => {
          if (r.row_id === rowId && r.classification) {
            const opt = CATEGORY_OPTIONS.find(c => c.value === newCategory);
            return {
              ...r,
              classification: {
                ...r.classification,
                category: newCategory,
                category_name_uz: opt ? opt.label : newCategory,
                rule_source: 'MANUAL_USER_OVERRIDE'
              }
            };
          }
          return r;
        })
      });
    }
  }

  // Commit batch to ledger
  async function handleCommitBatch() {
    if (!preview) return;
    setLoading(true);
    setErrorMessage(null);
    try {
      const res = await commitImportBatch(preview.batch_id, 'demo-org-agro-01');
      setCommitResult(res);
      await loadHistory();
    } catch (err: any) {
      setErrorMessage(err.message || 'Bazaga yozishda xatolik yuz berdi');
    } finally {
      setLoading(false);
    }
  }

  const filteredRows = preview?.rows.filter(r => {
    if (filterStatus === 'ALL') return true;
    return r.validation_status === filterStatus;
  }) || [];

  return (
    <div className="page-shell py-10 lg:py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        
        {/* Header */}
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-agro-100 text-agro-800 text-xs font-semibold mb-3">
            <FileSpreadsheet className="w-3.5 h-3.5 text-agro-600" />
            <span>Smart Data Ingestion & Ledger Separation</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-navy-950 sm:text-4xl">
            Aqlli Moliyaviy Ma&apos;lumotlar Importi & Toifalash
          </h1>
          <p className="mt-2 text-slate-600 text-sm sm:text-base leading-relaxed">
            Soliq.uz E-fakturalari va Bank ko&apos;chirmalarini (.csv / .xlsx) avtomatlashtirilgan tarzda yuklang.
            Tizim MXIK (IKPU) kodlari va semantik qoidalar yordamida toifalarni aniqlaydi hamda
            Invoys va Kassa reestrlarini buxgalteriya qonuniyatlariga binoan qat&apos;iy ajratadi.
          </p>
        </div>

        {/* Security & Regulatory Notice */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-card flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start space-x-3">
            <Shield className="w-6 h-6 text-agro-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-bold text-slate-900">
                O&apos;RQ-547 Qonuni va Bank Sirlari Xavfsizlik Kafolati
              </h4>
              <p className="text-xs text-slate-500 mt-0.5 max-w-2xl">
                Barcha hisob-kitoblar faqat O&apos;zbekiston Respublikasi hududida deterministik dvigatelda amalga oshiriladi.
                Fayl xesh summalari SHA-256 orqali takroriy kiritishdan himoyalangan.
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={zeroRetention} 
                onChange={(e) => setZeroRetention(e.target.checked)} 
                className="sr-only peer" 
              />
              <div className="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-agro-600"></div>
              <span className="ml-2 text-xs font-semibold text-slate-700">Zero-Retention Rejimi</span>
            </label>
          </div>
        </div>

        {/* Authenticated User Status */}
        {isAuthenticated && userEmail && (
          <div className="bg-emerald-50 border border-emerald-200 p-3.5 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-emerald-900 text-xs">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>
                Faol hisob: <strong>{userEmail}</strong>
                {userEmail === 'demo@agrohisob.uz' && (
                  <span className="ml-2 px-2 py-0.5 rounded-full text-[10px] font-bold bg-agro-100 text-agro-800 border border-agro-300">
                    DEMO CFO PROFILI
                  </span>
                )}
              </span>
            </div>
            {userEmail === 'demo@agrohisob.uz' && (
              <button
                type="button"
                onClick={() => {
                  logoutDemoSession();
                  setIsAuthenticated(false);
                  setUserEmail(null);
                }}
                className="px-2.5 py-1 text-[11px] font-semibold text-slate-600 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition"
              >
                Chiqish
              </button>
            )}
          </div>
        )}

        {/* Unauthenticated Security Notice */}
        {!isAuthenticated && (
          <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-amber-900">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-xs uppercase tracking-wide text-amber-800">Autentifikatsiya Talab Etiladi</p>
                <p className="text-xs text-amber-800 mt-0.5">
                  Bank ko&apos;chirmasi va Soliq E-Faktura fayllarini import qilish hamda buxgalteriya reestrlariga yozish uchun Bosh buxgalter yoki Demo CFO profiliga kiring.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={handleQuickDemoLogin}
                disabled={loading}
                className="px-3.5 py-1.5 bg-agro-700 hover:bg-agro-800 text-white rounded-lg text-xs font-bold inline-flex items-center gap-1 shadow-sm transition"
              >
                Demo Profil Bilan Kirish
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
              <Link
                href="/login?redirect=/data-import"
                className="px-3.5 py-1.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold inline-flex items-center gap-1 shadow-sm transition"
              >
                Tizimga Kirish
              </Link>
            </div>
          </div>
        )}

        {/* Error notification */}
        {errorMessage && (
          <div className="bg-rose-50 border border-rose-200 p-4 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-rose-800 text-sm">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-xs uppercase tracking-wide text-rose-900">
                  {errorMessage.toLowerCase().includes('autentifikatsiya') || errorMessage.toLowerCase().includes('token')
                    ? "Ruxsat Cheklangan"
                    : "Xatolik Yuz Berdi"}
                </p>
                <p className="text-xs text-rose-700 mt-0.5">{errorMessage}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={handleQuickDemoLogin}
                disabled={loading}
                className="px-3.5 py-1.5 bg-agro-700 hover:bg-agro-800 text-white rounded-lg text-xs font-bold inline-flex items-center gap-1 shadow-sm transition"
              >
                Demo Profil Bilan Kirish
              </button>
              <Link
                href="/login?redirect=/data-import"
                className="px-3.5 py-1.5 bg-white border border-rose-300 hover:bg-rose-100/50 text-rose-800 rounded-lg text-xs font-semibold inline-flex items-center gap-1 shadow-sm transition"
              >
                Kirish Sahifasi
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        )}

        {/* Stage 1: Upload Container */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-card overflow-hidden">
          <div className="border-b border-slate-200 bg-slate-50/60 p-3 flex flex-wrap gap-2">
            <button
              onClick={() => { setDocType('BANK_STATEMENT'); }}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-2 ${
                docType === 'BANK_STATEMENT'
                  ? 'bg-navy-900 text-white shadow-card'
                  : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
              }`}
            >
              <FileCheck className="w-4 h-4" />
              <span>1. Bank Ko&apos;chirmasi (Cash Inflow/Outflow)</span>
            </button>
            <button
              onClick={() => { setDocType('E_FAKTURA'); }}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-2 ${
                docType === 'E_FAKTURA'
                  ? 'bg-navy-900 text-white shadow-card'
                  : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
              }`}
            >
              <FileSpreadsheet className="w-4 h-4" />
              <span>2. Soliq E-Faktura (Invoice Obligations)</span>
            </button>
          </div>

          <div className="p-8">
            <div className="border-2 border-dashed border-slate-300 hover:border-agro-400 rounded-xl p-8 sm:p-12 text-center bg-slate-50/60 transition">
              <UploadCloud className="w-12 h-12 text-agro-600 mx-auto mb-3" />
              <h3 className="text-base font-bold text-slate-900">
                {docType === 'BANK_STATEMENT' 
                  ? "Bank aylanmasi ko'chirmasi faylini tanlang (.CSV yoki .XLSX)"
                  : "Soliq.uz E-Faktura reestrini yuklang (.XLSX yoki .CSV)"}
              </h3>
              <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                Maksimal fayl hajmi: 10 MB. Tizim o&apos;zbek (lotin/kirill) va rus tillaridagi ustun nomlarini avtomatik taniydi.
              </p>

              <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
                <label className="px-4 py-2.5 bg-agro-700 hover:bg-agro-800 text-white rounded-xl text-xs font-semibold shadow-card transition cursor-pointer inline-flex items-center space-x-1.5">
                  <UploadCloud className="w-4 h-4" />
                  <span>Kompyuterdan Fayl Tanlash</span>
                  <input 
                    type="file" 
                    accept=".csv,.xlsx" 
                    className="hidden" 
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        handleFileUpload(e.target.files[0]);
                      }
                    }} 
                  />
                </label>

                <button 
                  onClick={() => handleLoadSample('BANK_STATEMENT')}
                  disabled={loading}
                  className="px-4 py-2.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold transition"
                >
                  Namunaviy Bank Ko&apos;chirmasi (.csv)
                </button>

                <button 
                  onClick={() => handleLoadSample('E_FAKTURA')}
                  disabled={loading}
                  className="px-4 py-2.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold transition"
                >
                  Namunaviy E-Faktura (.xlsx)
                </button>
              </div>

              {loading && (
                <div className="mt-4 flex items-center justify-center space-x-2 text-xs text-agro-700 font-semibold">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Ma&apos;lumotlar xavfsiz dekodlanmoqda va toifalanmoqda...</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Stage 2 & 3: Preview & Smart Column Mappings */}
        {preview && (
          <div className="space-y-6">
            
            {/* Ledger Invariant Alert */}
            <div className={`p-5 rounded-xl border ${
              preview.document_type === 'E_FAKTURA'
                ? 'bg-amber-50/80 border-amber-200 text-amber-900'
                : 'bg-emerald-50/80 border-emerald-200 text-emerald-900'
            }`}>
              <div className="flex items-start space-x-3">
                <Info className="w-5 h-5 shrink-0 mt-0.5" />
                <div className="text-xs sm:text-sm">
                  <h4 className="font-bold">
                    {preview.document_type === 'E_FAKTURA'
                      ? "Invoys Majburiyatlari Reestri (Invoice Obligation Ledger)"
                      : "Kassa va Real Pul Oqimlari Reestri (Cash Ledger)"}
                  </h4>
                  <p className="mt-1 leading-relaxed opacity-90">
                    {preview.accounting_notice}
                  </p>
                </div>
              </div>
            </div>

            {/* Column Mappings Bar */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-card">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <Layers className="w-4 h-4 text-agro-600" />
                  <h3 className="text-sm font-bold text-slate-900">
                    Avtomatik Aniqlangan Ustunlar Xaritasi (Smart Mapping)
                  </h3>
                </div>
                <span className="text-[11px] font-mono text-slate-400">
                  SHA-256: {preview.file_hash_sha256.slice(0, 16)}...
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
                {preview.detected_mappings.map((m, idx) => (
                  <div key={idx} className="bg-slate-50 p-2.5 rounded-xl border border-slate-200 text-xs">
                    <p className="text-[10px] uppercase font-semibold text-slate-400">{m.target_field}</p>
                    <p className="font-bold text-slate-800 truncate mt-0.5">{m.source_header}</p>
                    <div className="flex items-center space-x-1 mt-1 text-[10px] text-emerald-700 font-medium">
                      <Check className="w-3 h-3" />
                      <span>{(Number(m.confidence || 0) * 100).toFixed(0)}% moslik</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Summary Statistics Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card">
                <p className="text-[11px] font-semibold text-slate-500">Jami Qatorlar</p>
                <p className="text-xl font-bold text-slate-900 mt-1">{preview.total_rows}</p>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card">
                <p className="text-[11px] font-semibold text-emerald-600">Yaroqli Qatorlar</p>
                <p className="text-xl font-bold text-emerald-700 mt-1">{preview.valid_rows}</p>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card">
                <p className="text-[11px] font-semibold text-amber-600">Ogohlantirish</p>
                <p className="text-xl font-bold text-amber-700 mt-1">{preview.warning_rows}</p>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card">
                <p className="text-[11px] font-semibold text-rose-600">Xatoliklar</p>
                <p className="text-xl font-bold text-rose-700 mt-1">{preview.error_rows}</p>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card">
                <p className="text-[11px] font-semibold text-slate-500">Kutilayotgan Kirim</p>
                <p className="text-sm font-mono font-bold text-emerald-700 mt-1">
                  +{Number(preview.total_inflow).toLocaleString()} so&apos;m
                </p>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card">
                <p className="text-[11px] font-semibold text-slate-500">Kutilayotgan Chiqim</p>
                <p className="text-sm font-mono font-bold text-rose-700 mt-1">
                  -{Number(preview.total_outflow).toLocaleString()} so&apos;m
                </p>
              </div>
            </div>

            {/* Table & Inline Review */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-card overflow-hidden">
              <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold text-slate-700">Filtr:</span>
                  {(['ALL', 'VALID', 'WARNING', 'ERROR', 'DUPLICATE'] as const).map(st => (
                    <button
                      key={st}
                      onClick={() => setFilterStatus(st)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition ${
                        filterStatus === st 
                          ? 'bg-slate-900 text-white' 
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      {st === 'ALL' ? 'Barchasi' : st}
                    </button>
                  ))}
                </div>

                <button
                  onClick={handleCommitBatch}
                  disabled={loading || preview.valid_rows === 0}
                  className="px-5 py-2.5 bg-agro-700 hover:bg-agro-800 disabled:opacity-50 text-white rounded-xl text-xs font-bold shadow-card transition inline-flex items-center space-x-1.5"
                >
                  <Check className="w-4 h-4" />
                  <span>Bazaga Kiritish va Tasdiqlash ({preview.valid_rows} ta qator)</span>
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                      <th className="py-3 px-3">#</th>
                      <th className="py-3 px-3">Sana</th>
                      <th className="py-3 px-3">Yo&apos;nalish</th>
                      <th className="py-3 px-3">Hujjat №</th>
                      <th className="py-3 px-3">Kontragent & INN</th>
                      <th className="py-3 px-3">MXIK (IKPU)</th>
                      <th className="py-3 px-3">Agronomik Toifa (Tahrirlash mumkin)</th>
                      <th className="py-3 px-3 text-right">Summa (so&apos;m)</th>
                      <th className="py-3 px-3 text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-700">
                    {filteredRows.map((r, idx) => (
                      <tr key={r.row_id || idx} className="hover:bg-slate-50">
                        <td className="py-3 px-3 font-mono text-slate-400">{r.row_index}</td>
                        <td className="py-3 px-3 font-mono whitespace-nowrap">
                          {r.normalized?.transaction_date || '-'}
                        </td>
                        <td className="py-3 px-3 whitespace-nowrap">
                          {r.normalized?.direction === 'INFLOW' ? (
                            <span className="inline-flex items-center space-x-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-bold">
                              <ArrowDownRight className="w-3 h-3" />
                              <span>Kirim</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center space-x-1 text-rose-700 bg-rose-50 px-2 py-0.5 rounded font-bold">
                              <ArrowUpRight className="w-3 h-3" />
                              <span>Chiqim</span>
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-3 font-mono text-slate-600">
                          {r.normalized?.document_number || '-'}
                        </td>
                        <td className="py-3 px-3">
                          <p className="font-bold text-slate-900 truncate max-w-xs">
                            {r.normalized?.counterparty_name}
                          </p>
                          {r.normalized?.counterparty_inn && (
                            <p className="text-[10px] font-mono text-slate-400">
                              INN: {r.normalized.counterparty_inn}
                            </p>
                          )}
                        </td>
                        <td className="py-3 px-3 font-mono text-slate-500 whitespace-nowrap">
                          {r.normalized?.mxik_code || '-'}
                        </td>
                        <td className="py-3 px-3">
                          <select
                            value={r.classification?.category || ''}
                            onChange={(e) => handleCategoryChange(r.row_id, e.target.value)}
                            className="text-xs bg-slate-50 border border-slate-300 rounded-lg px-2 py-1 focus:ring-1 focus:ring-agro-500 font-medium text-slate-800"
                          >
                            {CATEGORY_OPTIONS.map(opt => (
                              <option key={opt.value} value={opt.value}>
                                {opt.label}
                              </option>
                            ))}
                          </select>
                          {r.classification?.rule_source && (
                            <p className="text-[10px] text-slate-400 mt-0.5">
                              {r.classification.rule_source === 'MXIK_DICTIONARY' && '🎯 MXIK klassifikatori'}
                              {r.classification.rule_source === 'KEYWORD_HEURISTIC' && '🔍 Kalit so\'z qoidasi'}
                              {r.classification.rule_source === 'COUNTERPARTY_RULE' && '🏢 Kontragent profili'}
                              {r.classification.rule_source === 'MANUAL_USER_OVERRIDE' && '✍️ Foydalanuvchi tanlovi'}
                            </p>
                          )}
                        </td>
                        <td className="py-3 px-3 text-right font-mono font-bold text-slate-900 whitespace-nowrap">
                          {r.normalized?.amount ? Number(r.normalized.amount).toLocaleString() : '-'}
                        </td>
                        <td className="py-3 px-3 text-center whitespace-nowrap">
                          {r.validation_status === 'VALID' && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                              Yaroqli
                            </span>
                          )}
                          {r.validation_status === 'WARNING' && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[10px] font-bold">
                              Ogohlantirish
                            </span>
                          )}
                          {r.validation_status === 'ERROR' && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 text-[10px] font-bold">
                              Xatolik
                            </span>
                          )}
                          {r.validation_status === 'DUPLICATE' && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-slate-200 text-slate-700 text-[10px] font-bold">
                              Takroriy
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

        {/* Commit Result Success Card */}
        {commitResult && (
          <div className="bg-agro-50 border border-agro-200 p-6 rounded-xl shadow-card text-agro-950 space-y-3">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-6 h-6 text-emerald-600" />
              <h3 className="text-base font-bold text-emerald-900">
                Import Muvaffaqiyatli Yakunlandi va Bazaga Kiritildi
              </h3>
            </div>
            <p className="text-xs sm:text-sm text-emerald-800">
              {commitResult.message}
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
              <div className="bg-white p-3 rounded-xl border border-emerald-200">
                <p className="text-[10px] text-slate-500 font-semibold uppercase">Reestr Turi</p>
                <p className="text-xs font-bold font-mono text-slate-800 mt-0.5">{commitResult.target_ledger}</p>
              </div>
              <div className="bg-white p-3 rounded-xl border border-emerald-200">
                <p className="text-[10px] text-slate-500 font-semibold uppercase">Kiritilgan Qatorlar</p>
                <p className="text-sm font-bold text-slate-800 mt-0.5">{commitResult.committed_count} ta</p>
              </div>
              <div className="bg-white p-3 rounded-xl border border-emerald-200">
                <p className="text-[10px] text-slate-500 font-semibold uppercase">Sof Pul Oqimi</p>
                <p className="text-sm font-mono font-bold text-emerald-700 mt-0.5">
                  {commitResult.updated_cash_balance !== null && commitResult.updated_cash_balance !== undefined
                    ? `${Number(commitResult.updated_cash_balance).toLocaleString()} so'm`
                    : "O'zgarmadi (Invoys)"}
                </p>
              </div>
              <div className="bg-white p-3 rounded-xl border border-emerald-200">
                <p className="text-[10px] text-slate-500 font-semibold uppercase">Yangilangan DSCR</p>
                <p className="text-sm font-mono font-bold text-agro-700 mt-0.5">
                  {commitResult.updated_dscr ? `${commitResult.updated_dscr}x` : "Hisoblanmagan"}
                </p>
              </div>
            </div>

            <div className="pt-2 flex items-center space-x-3">
              <Link
                href="/dashboard"
                className="px-4 py-2 bg-agro-700 hover:bg-agro-800 text-white rounded-xl text-xs font-bold inline-flex items-center space-x-1.5 shadow-card"
              >
                <span>Dashboardda Ko&apos;rish</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        )}

        {/* Stage 5: Import History Audit */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-card overflow-hidden">
          <div className="p-5 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <FileCheck className="w-5 h-5 text-agro-600" />
              <h3 className="font-bold text-slate-900">Import Tarixi va Audit Jurnali</h3>
            </div>
            <button 
              onClick={loadHistory}
              className="text-xs text-agro-600 hover:text-agro-800 font-semibold inline-flex items-center space-x-1"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Yangilash</span>
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                  <th className="py-3 px-4">Fayl Nomi</th>
                  <th className="py-3 px-4">Hujjat Turi</th>
                  <th className="py-3 px-4">Kiritilgan Qatorlar</th>
                  <th className="py-3 px-4">Jami Kirim</th>
                  <th className="py-3 px-4">Jami Chiqim</th>
                  <th className="py-3 px-4">Sana va Vaqt</th>
                  <th className="py-3 px-4 text-center">Holat</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {history.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-6 text-center text-slate-400">
                      Hali hech qanday import partiyasi kiritilmagan.
                    </td>
                  </tr>
                ) : (
                  history.map((h, idx) => (
                    <tr key={h.batch_id || idx} className="hover:bg-slate-50">
                      <td className="py-3 px-4 font-medium text-slate-900">{h.file_name}</td>
                      <td className="py-3 px-4 font-mono">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-800">
                          {h.document_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-bold">{h.committed_count} / {h.total_rows}</td>
                      <td className="py-3 px-4 text-emerald-700 font-mono">
                        +{Number(h.total_inflow).toLocaleString()} so&apos;m
                      </td>
                      <td className="py-3 px-4 text-rose-700 font-mono">
                        -{Number(h.total_outflow).toLocaleString()} so&apos;m
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-500">
                        {h.committed_at ? new Date(h.committed_at).toLocaleString() : '-'}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                          {h.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}
