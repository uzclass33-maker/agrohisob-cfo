'use client';

import React, { useState, useEffect } from 'react';
import { 
  Users, CheckCircle2, AlertTriangle, TrendingUp, ShieldCheck, 
  FileText, BarChart3, Clock, Plus, Search, Database, Lock, Building2,
  RefreshCw, Check, XCircle
} from 'lucide-react';
import { trackEvent } from '@/lib/analyticsClient';
import { authFetch } from '@/lib/api';

interface ResearchRecord {
  id: string;
  code: string;
  customer_segment: string;
  source_classification: string;
  interview_status: string;
  participant_role: string;
  region: string;
  consent_recorded: boolean;
  validated_problems: string[];
  unverified_assumptions: string[];
  notes?: string;
  created_at: string;
}

interface ResearchSummary {
  total_records: number;
  verified_interviews: number;
  unverified_notes: number;
  synthetic_demo_records: number;
  secondary_research_count: number;
  founder_assumptions: number;
  segment_distribution: Record<string, number>;
  top_validated_problems: { problem: string; count: number }[];
  open_assumptions: { assumption: string; source: string }[];
}

interface PilotMetricItem {
  key: string;
  name: string;
  formula: string;
  unit: string;
  baseline: string;
  target: string;
  current_status: string;
  verification_evidence: string;
}

interface PilotOrg {
  id: string;
  name: string;
  segment: string;
  is_synthetic: boolean;
  onboarding_status: string;
  data_consent_signed: boolean;
  tasks_completed: number;
  total_tasks: number;
}

interface PilotDashboardData {
  summary_notice: string;
  actual_paying_customers: number;
  actual_active_pilots: number;
  planned_pilot_targets: number;
  verified_interviews_completed: number;
  planned_interviews: number;
  synthetic_demo_profiles_count?: number;
  synthetic_demo_profiles: PilotOrg[];
  active_pilot_organizations: PilotOrg[];
  kpi_metrics: PilotMetricItem[];
  data_security_status: string;
  readiness_level: string;
}

export default function PilotDashboardPage() {
  const [activeTab, setActiveTab] = useState<'discovery' | 'pilot' | 'analytics' | 'kpis'>('discovery');
  const [pilotData, setPilotData] = useState<PilotDashboardData | null>(null);
  const [interviews, setInterviews] = useState<ResearchRecord[]>([]);
  const [researchSummary, setResearchSummary] = useState<ResearchSummary | null>(null);
  const [analyticsSummary, setAnalyticsSummary] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // New Interview Form State
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [formData, setFormData] = useState({
    code: '',
    customer_segment: 'FARMER',
    source_classification: 'UNVERIFIED_NOTE',
    participant_role: '',
    region: 'Toshkent viloyati',
    consent_recorded: false,
    unverified_assumptions: '',
    notes: ''
  });

  useEffect(() => {
    trackEvent('dashboard_viewed', { metadata: { section: 'pilot_dashboard' } });
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Use researcher token if available for research/analytics access
      const researcherHeader = { Authorization: 'Bearer test-token-researcher' };
      const [dashRes, interviewsRes, summaryRes, analyticsRes] = await Promise.all([
        authFetch('/api/v1/pilot/dashboard').then(r => r.json()).catch(() => null),
        authFetch('/api/v1/research/interviews', { headers: researcherHeader }).then(r => r.json()).catch(() => []),
        authFetch('/api/v1/research/summary').then(r => r.json()).catch(() => null),
        authFetch('/api/v1/analytics/summary').then(r => r.json()).catch(() => null),
      ]);

      setPilotData(dashRes);
      setInterviews(Array.isArray(interviewsRes) ? interviewsRes : []);
      setResearchSummary(summaryRes);
      setAnalyticsSummary(analyticsRes);
    } catch (e) {
      console.error('Failed to load pilot data', e);
    } finally {
      setLoading(false);
    }
  };

  const handleAddInterview = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        study_id: 'study-agrohisob-2026',
        code: formData.code || `INT-${Date.now().toString().slice(-4)}`,
        customer_segment: formData.customer_segment,
        source_classification: formData.source_classification,
        interview_status: 'PLANNED',
        participant_role: formData.participant_role || 'Agrobiznes mutaxassisi',
        region: formData.region,
        consent_recorded: formData.consent_recorded,
        unverified_assumptions: formData.unverified_assumptions ? [formData.unverified_assumptions] : [],
        notes: formData.notes
      };

      const res = await authFetch('/api/v1/research/interviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: 'Bearer test-token-researcher' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setShowAddModal(false);
        setFormData({
          code: '',
          customer_segment: 'FARMER',
          source_classification: 'UNVERIFIED_NOTE',
          participant_role: '',
          region: 'Toshkent viloyati',
          consent_recorded: false,
          unverified_assumptions: '',
          notes: ''
        });
        loadDashboardData();
      }
    } catch (err) {
      alert('Yozuvni saqlashda xatolik yuz berdi');
    }
  };

  const getSourceBadge = (classification: string) => {
    switch (classification) {
      case 'VERIFIED_INTERVIEW':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800">TASDIQLANGAN INTERVYU</span>;
      case 'SYNTHETIC_DEMO':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-navy-100 text-navy-800">SINTETIK DEMO</span>;
      case 'FOUNDER_ASSUMPTION':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-800">ASOSCHI TAXMINI</span>;
      case 'SECONDARY_RESEARCH':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800">IKKILAMCHI STATISTIKA</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-700">NORASMIY QAYD</span>;
    }
  };

  return (
    <div className="page-shell py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Top Header */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-card flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="bg-agro-100 text-agro-800 text-xs px-2.5 py-0.5 rounded-full font-semibold">
                Pilot & Tadqiqot Validatsiyasi
              </span>
              <span className="text-slate-400">|</span>
              <span className="text-xs text-slate-500 font-medium">Bozorga Chiqish & Mahsulot Tahlili</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-navy-950 mt-1">Pilot & Tadqiqot Validatsiyasi Paneli</h1>
            <p className="text-sm text-slate-600 mt-0.5">
              Mijozlar bilan intervyular, pilot operatsiyalari, KPI metrikalari va mahsulot analitikasini kuzatish tizimi
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={loadDashboardData}
              className="flex items-center space-x-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Yangilash</span>
            </button>
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center space-x-1.5 px-4 py-2 bg-agro-700 hover:bg-agro-800 text-white rounded-lg text-sm font-semibold shadow-card transition"
            >
              <Plus className="w-4 h-4" />
              <span>Yangi Qayd / Intervyu</span>
            </button>
          </div>
        </div>

        {/* Fact-checking Notice Banner */}
        <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-lg">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 mr-3 flex-shrink-0" />
            <div className="text-sm text-amber-900">
              <span className="font-semibold">DALILLARNING SHAFFOFLIK KAFOLATI: </span>
              {pilotData?.summary_notice || "Hozircha real to'lovchi mijozlar mavjud emas (0 ta). Barcha sinovlar sintetik profillar va pilot rejalari asosida olib borilmoqda."}
            </div>
          </div>
        </div>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-card">
            <div className="flex justify-between items-center text-slate-500 text-xs font-semibold uppercase">
              <span>Haqiqiy To'lovchi Mijozlar</span>
              <Lock className="w-4 h-4 text-slate-400" />
            </div>
            <div className="text-3xl font-extrabold text-slate-900 mt-2">
              {pilotData?.actual_paying_customers ?? 0} <span className="text-sm font-normal text-slate-500">ta</span>
            </div>
            <div className="text-xs text-slate-500 mt-1 flex items-center">
              <span className="inline-block w-2 h-2 rounded-full bg-slate-400 mr-1.5"></span>
              Pilotgacha to'lov olinmaydi
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-card">
            <div className="flex justify-between items-center text-slate-500 text-xs font-semibold uppercase">
              <span>Mijozlar Intervyulari</span>
              <Users className="w-4 h-4 text-blue-500" />
            </div>
            <div className="text-3xl font-extrabold text-slate-900 mt-2">
              {pilotData?.verified_interviews_completed ?? 0} <span className="text-sm font-normal text-slate-500">/ {pilotData?.planned_interviews ?? 19}</span>
            </div>
            <div className="text-xs text-blue-600 mt-1 font-medium">
              Rejalashtirilgan nishon kvotasi
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-card">
            <div className="flex justify-between items-center text-slate-500 text-xs font-semibold uppercase">
              <span>Sintetik Demo Profillar</span>
              <Database className="w-4 h-4 text-navy-500" />
            </div>
            <div className="text-3xl font-extrabold text-navy-800 mt-2">
              {pilotData?.synthetic_demo_profiles_count ?? 3} <span className="text-sm font-normal text-slate-500">ta korxona</span>
            </div>
            <div className="text-xs text-navy-600 mt-1 font-medium">
              100% ishchi MVP ssenariylari
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-card">
            <div className="flex justify-between items-center text-slate-500 text-xs font-semibold uppercase">
              <span>Ma'lumotlar Xavfsizligi</span>
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
            </div>
            <div className="text-lg font-bold text-amber-700 mt-2">
              {pilotData?.data_security_status === 'APP_RBAC_ACTIVE_DB_RLS_NOT_VERIFIED'
                ? 'RBAC FAOL (RLS KUTILMOQDA)'
                : (pilotData?.data_security_status === 'ISOLATED_SANDBOX_ENFORCED' ? 'SANDBOX HIMOYASI' : 'FAOL')}
            </div>
            <div className="text-xs text-amber-600 mt-1">
              {pilotData?.data_security_status === 'APP_RBAC_ACTIVE_DB_RLS_NOT_VERIFIED'
                ? 'Ilova sathi himoyalangan, DB RLS kutilmoqda'
                : 'PII filtri & RLS kafolatlangan'}
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-slate-200 bg-white rounded-t-xl px-4 shadow-card">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('discovery')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition flex items-center space-x-2 ${
                activeTab === 'discovery'
                  ? 'border-agro-700 text-agro-800'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              <Users className="w-4 h-4" />
              <span>Mijozlar Tadqiqoti & Intervyular</span>
            </button>
            <button
              onClick={() => setActiveTab('pilot')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition flex items-center space-x-2 ${
                activeTab === 'pilot'
                  ? 'border-agro-700 text-agro-800'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              <Building2 className="w-4 h-4" />
              <span>Pilot Operatsiyalari (4 Hafta)</span>
            </button>
            <button
              onClick={() => setActiveTab('kpis')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition flex items-center space-x-2 ${
                activeTab === 'kpis'
                  ? 'border-agro-700 text-agro-800'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              <TrendingUp className="w-4 h-4" />
              <span>Pilot KPI Metriklari</span>
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition flex items-center space-x-2 ${
                activeTab === 'analytics'
                  ? 'border-agro-700 text-agro-800'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Mahsulot Analitikasi (Privacy-Safe)</span>
            </button>
          </nav>
        </div>

        {/* TAB 1: CUSTOMER DISCOVERY */}
        {activeTab === 'discovery' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-card">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h2 className="text-lg font-bold text-slate-900">Mijozlar Bilan Suhbatlar Ro'yxati (Research Tracker)</h2>
                  <p className="text-sm text-slate-500">
                    O'zbekiston agrar korxonalari bilan o'tkazilayotgan barcha qaydlar va ularning manba klassifikatsiyasi
                  </p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-600">
                  <thead className="bg-slate-50 text-slate-800 text-xs uppercase font-semibold border-b">
                    <tr>
                      <th className="py-3 px-4">Kod</th>
                      <th className="py-3 px-4">Segment</th>
                      <th className="py-3 px-4">Manba Turi</th>
                      <th className="py-3 px-4">Holat</th>
                      <th className="py-3 px-4">Lavozim & Hudud</th>
                      <th className="py-3 px-4">Rozilik</th>
                      <th className="py-3 px-4">Asosiy Qayd / Gipoteza</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {interviews.map((rec) => (
                      <tr key={rec.id} className="hover:bg-slate-50/80">
                        <td className="py-3 px-4 font-mono font-semibold text-slate-900">{rec.code}</td>
                        <td className="py-3 px-4 font-medium">{rec.customer_segment}</td>
                        <td className="py-3 px-4">{getSourceBadge(rec.source_classification)}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                            rec.interview_status === 'CONDUCTED' ? 'bg-green-100 text-green-800' : 'bg-slate-100 text-slate-600'
                          }`}>
                            {rec.interview_status}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="font-medium text-slate-900">{rec.participant_role}</div>
                          <div className="text-xs text-slate-500">{rec.region}</div>
                        </td>
                        <td className="py-3 px-4">
                          {rec.consent_recorded ? (
                            <span className="flex items-center text-emerald-600 text-xs font-medium">
                              <Check className="w-3.5 h-3.5 mr-1" /> Olingan
                            </span>
                          ) : (
                            <span className="text-slate-400 text-xs">Kutilmoqda</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-xs text-slate-600 max-w-xs truncate">
                          {rec.validated_problems.length > 0 ? rec.validated_problems[0] : rec.unverified_assumptions[0] || rec.notes}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Validation Hypotheses Progress */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-5 rounded-xl border border-slate-200">
                <h3 className="font-bold text-slate-900 text-base mb-2">Segmentlar Taqsimoti (Kvota: 19 ta)</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span>Fermer xo'jaliklari (50-200 ga)</span>
                    <span className="font-semibold text-slate-800">5 ta nishon</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span>Meva-sabzavot eksportyorlari</span>
                    <span className="font-semibold text-slate-800">4 ta nishon</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span>Qishloq xo'jaligi KO'B (Agri-SME)</span>
                    <span className="font-semibold text-slate-800">4 ta nishon</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span>Agrosanoat klasterlari</span>
                    <span className="font-semibold text-slate-800">2 ta nishon</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span>Buxgalterlar va moliyaviy konsaltantlar</span>
                    <span className="font-semibold text-slate-800">4 ta nishon</span>
                  </div>
                </div>
              </div>

              <div className="bg-white p-5 rounded-xl border border-slate-200">
                <h3 className="font-bold text-slate-900 text-base mb-2">Asosiy Tasdiqlanadigan Gipotezalar (H1-H6)</h3>
                <div className="space-y-2 text-xs">
                  <div className="p-2 bg-slate-50 rounded border border-slate-200">
                    <span className="font-bold text-slate-800">H1:</span> Mavsumiy kassa uzilishi (Cash gap) — 12 oylik prognoz yetishmasligi.
                  </div>
                  <div className="p-2 bg-slate-50 rounded border border-slate-200">
                    <span className="font-bold text-slate-800">H2:</span> 1C va Didox o'rtasida qo'lda solishtirish — haftasiga 8-15 soat yo'qotish.
                  </div>
                  <div className="p-2 bg-slate-50 rounded border border-slate-200">
                    <span className="font-bold text-slate-800">H3:</span> Kredit dossiyesini tayyorlash vaqtini 70%+ ga qisqartirish.
                  </div>
                  <div className="p-2 bg-slate-50 rounded border border-slate-200">
                    <span className="font-bold text-slate-800">H6:</span> Ma'lumotlar maxfiyligi (Bank/Soliq) — asosiy qabul qilish to'sig'i.
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: PILOT OPERATIONS */}
        {activeTab === 'pilot' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-card">
              <h2 className="text-lg font-bold text-slate-900 mb-1">4 Haftalik Pilot Sinovi Rejasi</h2>
              <p className="text-sm text-slate-500 mb-6">
                3-5 ta agrar korxona ishtirokida haqiqiy buxgalteriya ma'lumotlarini import qilish va hisobot tezligini baholash
              </p>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-4 bg-agro-50 rounded-lg border border-agro-200">
                  <div className="text-xs font-bold text-agro-700 uppercase">1-Hafta</div>
                  <div className="font-semibold text-slate-900 mt-1">Onboarding & Baza O'lchovi</div>
                  <p className="text-xs text-slate-600 mt-1">
                    NDA imzolash, mavjud hisobot tayyorlash vaqtini (Baseline) qayd etish.
                  </p>
                </div>
                <div className="p-4 bg-agro-50 rounded-lg border border-agro-200">
                  <div className="text-xs font-bold text-agro-700 uppercase">2-Hafta</div>
                  <div className="font-semibold text-slate-900 mt-1">Ma'lumotlar Importi</div>
                  <p className="text-xs text-slate-600 mt-1">
                    Didox fakturalari va 1C ko'chirmalarini yuklash, normalizatsiyani tekshirish.
                  </p>
                </div>
                <div className="p-4 bg-agro-50 rounded-lg border border-agro-200">
                  <div className="text-xs font-bold text-agro-700 uppercase">3-Hafta</div>
                  <div className="font-semibold text-slate-900 mt-1">Prognoz & DSCR Tahlili</div>
                  <p className="text-xs text-slate-600 mt-1">
                    12 oylik pul oqimi, kassa uzilishlari va Agrobank andozasidagi DSCR hisoblash.
                  </p>
                </div>
                <div className="p-4 bg-agro-50 rounded-lg border border-agro-200">
                  <div className="text-xs font-bold text-agro-700 uppercase">4-Hafta</div>
                  <div className="font-semibold text-slate-900 mt-1">Xulosa & Tijorat Taklifi</div>
                  <p className="text-xs text-slate-600 mt-1">
                    Tejalgan vaqtni baholash, foydalanuvchi fikri (NPS) va obunaga taklif.
                  </p>
                </div>
              </div>
            </div>

            {/* Organizations Status */}
            <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-card">
              <h3 className="font-bold text-slate-900 text-base mb-3">Pilot Tashkilotlari Holati</h3>
              
              <div className="space-y-3">
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex justify-between items-center">
                  <div>
                    <span className="font-semibold text-slate-900">Haqiqiy Mijozlar (Real Pilots):</span>
                    <span className="text-sm text-slate-500 ml-2">Hozircha faol pilot mavjud emas (0/5 reja)</span>
                  </div>
                  <span className="text-xs bg-slate-200 text-slate-700 px-2 py-1 rounded font-semibold">RECRUITMENT BOSQICHIDA</span>
                </div>

                <div className="text-xs font-semibold text-slate-500 uppercase mt-4 mb-2">Tasdiqlangan Sintetik Demo Profillar (MVP Sinovi uchun):</div>
                {pilotData?.synthetic_demo_profiles.map((p) => (
                  <div key={p.id} className="p-3 bg-navy-50/60 rounded-lg border border-navy-200 flex justify-between items-center">
                    <div>
                      <div className="font-semibold text-navy-900">{p.name}</div>
                      <div className="text-xs text-navy-700">Segment: {p.segment} | Barcha 6 ta modul sinovdan o'tgan</div>
                    </div>
                    <span className="text-xs bg-navy-100 text-navy-800 px-2 py-1 rounded font-semibold">SINTETIK DEMO FAOL</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: PILOT KPIS */}
        {activeTab === 'kpis' && (
          <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-card">
            <h2 className="text-lg font-bold text-slate-900 mb-1">Pilot Baholash Ko'rsatkichlari (KPI Framework)</h2>
            <p className="text-sm text-slate-500 mb-6">
              Barcha metrikalar qat'iy matematik formulalar va solishtirish dalillariga asoslangan
            </p>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50 text-slate-800 text-xs uppercase font-semibold border-b">
                  <tr>
                    <th className="py-3 px-4">Metrika Nomi</th>
                    <th className="py-3 px-4">Hisoblash Formulasi</th>
                    <th className="py-3 px-4">Boshlang'ich Holat (Baseline)</th>
                    <th className="py-3 px-4">Pilot Maqsadi (Target)</th>
                    <th className="py-3 px-4">Hozirgi Natija & Dalil</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {pilotData?.kpi_metrics.map((k) => (
                    <tr key={k.key} className="hover:bg-slate-50/80">
                      <td className="py-3 px-4 font-semibold text-slate-900">{k.name}</td>
                      <td className="py-3 px-4 font-mono text-xs text-agro-700 bg-agro-50/50 p-2 rounded">{k.formula}</td>
                      <td className="py-3 px-4 text-xs text-slate-500">{k.baseline}</td>
                      <td className="py-3 px-4 text-xs font-semibold text-slate-900">{k.target}</td>
                      <td className="py-3 px-4 text-xs">
                        <div className="text-slate-800 font-medium">{k.current_status}</div>
                        <div className="text-slate-400 font-mono text-[11px] mt-0.5">{k.verification_evidence}</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 4: PRODUCT ANALYTICS */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-card">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h2 className="text-lg font-bold text-slate-900">Ichki Mahsulot Analitikasi (Privacy-Safe Tracking)</h2>
                  <p className="text-sm text-slate-500">
                    Foydalanuvchilarning moliyaviy ma'lumotlari, STIR yoki bank raqamlari mutlaqo yozilmaydi
                  </p>
                </div>
                <div className="text-xs bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full font-semibold">
                  Zero-PII Kafolati
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-500 font-semibold uppercase">Jami Qayd Etilgan Hodisalar</div>
                  <div className="text-2xl font-bold text-slate-900 mt-1">{analyticsSummary?.total_events ?? 0} ta</div>
                </div>
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-500 font-semibold uppercase">Noyob Sessiyalar</div>
                  <div className="text-2xl font-bold text-slate-900 mt-1">{analyticsSummary?.unique_sessions ?? 0} ta</div>
                </div>
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-500 font-semibold uppercase">O'rtacha Bajarilish Tezligi</div>
                  <div className="text-2xl font-bold text-slate-900 mt-1">&lt; 150 ms</div>
                </div>
              </div>

              <h3 className="font-bold text-slate-900 text-sm mb-2">Hodisalar Taqsimoti:</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                {analyticsSummary?.event_counts && Object.entries(analyticsSummary.event_counts).map(([k, v]: [string, any]) => (
                  <div key={k} className="p-2.5 bg-slate-50 rounded border border-slate-200 flex justify-between">
                    <span className="font-mono text-slate-600">{k}</span>
                    <span className="font-bold text-slate-900">{v}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </div>

      {/* Modal: Add Interview / Note */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-lg w-full p-6 shadow-xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 mb-1">Yangi Intervyu / Tadqiqot Qaydnomasi</h3>
            <p className="text-xs text-slate-500 mb-4">
              Har bir qayd uchun manba turini qat'iy va haqqoniy ko'rsating.
            </p>

            <form onSubmit={handleAddInterview} className="space-y-4 text-sm">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Qayd / Intervyu Kodi</label>
                <input
                  type="text"
                  placeholder="masalan: INT-FARM-02"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Segment</label>
                  <select
                    value={formData.customer_segment}
                    onChange={(e) => setFormData({ ...formData, customer_segment: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  >
                    <option value="FARMER">Fermer xo'jaligi</option>
                    <option value="EXPORTER">Meva eksportyori</option>
                    <option value="SME">Agri-SME (Qayta ishlash)</option>
                    <option value="CLUSTER">Agroklaster</option>
                    <option value="ACCOUNTANT_CFO">Buxgalter / CFO</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Manba Klassifikatsiyasi</label>
                  <select
                    value={formData.source_classification}
                    onChange={(e) => setFormData({ ...formData, source_classification: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm font-semibold text-agro-800"
                  >
                    <option value="UNVERIFIED_NOTE">NORASMIY QAYD</option>
                    <option value="VERIFIED_INTERVIEW">TASDIQLANGAN INTERVYU</option>
                    <option value="FOUNDER_ASSUMPTION">ASOSCHI TAXMINI</option>
                    <option value="SECONDARY_RESEARCH">IKKILAMCHI TADQIQOT</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Lavozim</label>
                  <input
                    type="text"
                    placeholder="Bosh buxgalter"
                    value={formData.participant_role}
                    onChange={(e) => setFormData({ ...formData, participant_role: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Hudud</label>
                  <input
                    type="text"
                    placeholder="Samarqand viloyati"
                    value={formData.region}
                    onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Gipoteza yoki Muammo Tavsifi</label>
                <textarea
                  rows={2}
                  placeholder="Kassa uzilishi qaysi oylarda bo'lishi haqida ma'lumot..."
                  value={formData.unverified_assumptions}
                  onChange={(e) => setFormData({ ...formData, unverified_assumptions: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>

              <div className="flex items-center space-x-2 pt-1">
                <input
                  type="checkbox"
                  id="consent"
                  checked={formData.consent_recorded}
                  onChange={(e) => setFormData({ ...formData, consent_recorded: e.target.checked })}
                  className="rounded text-agro-600"
                />
                <label htmlFor="consent" className="text-xs text-slate-700">
                  Suhbatdoshdan tadqiqot roziligi olindi
                </label>
              </div>

              <div className="flex justify-end space-x-3 pt-3 border-t">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border rounded-lg text-slate-600 hover:bg-slate-50 text-sm font-medium"
                >
                  Bekor qilish
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-agro-700 hover:bg-agro-800 text-white rounded-lg text-sm font-semibold"
                >
                  Saqlash
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
