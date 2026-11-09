'use client';

import React, { useState, useEffect } from 'react';
import {
  Landmark,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Droplets,
  Coins,
  FileText,
  TrendingUp,
  Percent,
  Calendar,
  Layers,
  ExternalLink,
  RefreshCw,
  Info,
  Building,
  CheckSquare,
  Sparkles,
} from 'lucide-react';

import {
  LandLeaseProfile,
  VMQ613ScreeningResult,
  IndicativeValuationResult,
  CollateralSensitivityAnalysis,
  CollateralDocumentChecklist,
  SubsidyMatchItem,
  PQ47CalculationResult,
  PF82CalculationResult,
  SubsidyFinancialImpactResponse,
  RegulatorySourceRecord,
} from '@/lib/types';

import {
  fetchDefaultCollateralProfile,
  screenCollateralEligibility,
  calculateCollateralValuation,
  calculateCollateralScenarios,
  fetchCollateralChecklist,
  fetchRegulatorySources,
  matchSubsidyPrograms,
  calculatePQ47,
  calculatePF82,
  calculateSubsidyFinancialImpact,
} from '@/lib/api';

export default function CollateralSubsidiesPage() {
  const [selectedOrgId, setSelectedOrgId] = useState<string>('scenario-small-farmer');
  const [activeTab, setActiveTab] = useState<'collateral' | 'subsidies' | 'regulatory'>('collateral');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Module A State
  const [leaseProfile, setLeaseProfile] = useState<LandLeaseProfile | null>(null);
  const [screeningResult, setScreeningResult] = useState<VMQ613ScreeningResult | null>(null);
  const [valuationResult, setValuationResult] = useState<IndicativeValuationResult | null>(null);
  const [sensitivityAnalysis, setSensitivityAnalysis] = useState<CollateralSensitivityAnalysis | null>(null);
  const [checklist, setChecklist] = useState<CollateralDocumentChecklist | null>(null);

  // Module B State
  const [matchedSubsidies, setMatchedSubsidies] = useState<SubsidyMatchItem[]>([]);
  const [subsidyImpact, setSubsidyImpact] = useState<SubsidyFinancialImpactResponse | null>(null);
  const [pq47Result, setPq47Result] = useState<PQ47CalculationResult | null>(null);
  const [pf82Result, setPf82Result] = useState<PF82CalculationResult | null>(null);

  // Interactive PQ47 Calculator inputs
  const [pq47Crop, setPq47Crop] = useState<string>('Paxta');
  const [pq47Hectares, setPq47Hectares] = useState<number>(25.0);
  const [pq47LoanUsed, setPq47LoanUsed] = useState<boolean>(true);
  const [pq47LoanAmount, setPq47LoanAmount] = useState<number>(200000000);

  // Interactive PF82 Calculator inputs
  const [pf82Crop, setPf82Crop] = useState<string>('Paxta');
  const [pf82Balance, setPf82Balance] = useState<number>(120000000);
  const [pf82ContractRate, setPf82ContractRate] = useState<number>(14.0);
  const [pf82Days, setPf82Days] = useState<number>(365);
  const [pf82Overdue, setPf82Overdue] = useState<boolean>(false);

  // Regulatory Registry State
  const [regulatorySources, setRegulatorySources] = useState<RegulatorySourceRecord[]>([]);

  // Load initial data
  const loadData = async (orgId: string) => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch Default Lease Profile
      const prof = await fetchDefaultCollateralProfile(orgId);
      setLeaseProfile(prof);

      // 2. Module A Collateral Evaluations
      const [screen, val, scen, chk] = await Promise.all([
        screenCollateralEligibility(prof),
        calculateCollateralValuation({
          area_hectares: prof.area_hectares,
          soil_bonitet_score: prof.soil_bonitet_score,
          remaining_lease_years: 25,
          normative_annual_net_benefit_per_ha_uzs: prof.normative_annual_net_benefit_per_ha_uzs,
          discount_rate_pct: prof.discount_rate_pct,
          annual_benefit_growth_pct: 2.0,
          target_ltv_pct: prof.target_ltv_pct,
        }),
        calculateCollateralScenarios({
          area_hectares: prof.area_hectares,
          soil_bonitet_score: prof.soil_bonitet_score,
          remaining_lease_years: 25,
          normative_annual_net_benefit_per_ha_uzs: prof.normative_annual_net_benefit_per_ha_uzs,
          discount_rate_pct: prof.discount_rate_pct,
          annual_benefit_growth_pct: 2.0,
          target_ltv_pct: prof.target_ltv_pct,
        }),
        fetchCollateralChecklist(prof),
      ]);

      setScreeningResult(screen);
      setValuationResult(val);
      setSensitivityAnalysis(scen);
      setChecklist(chk);

      // 3. Module B Subsidies Evaluations
      const subReq = {
        organization_id: orgId,
        region: prof.region,
        district: prof.district,
        crop_types: [prof.main_crop_type, 'Paxta', 'Sabzavot'],
        land_hectares: prof.area_hectares,
        has_drip_irrigation: true,
        has_bank_debt: true,
      };

      const [matches, impact, pqRes, pfRes, regSources] = await Promise.all([
        matchSubsidyPrograms(subReq),
        calculateSubsidyFinancialImpact(subReq),
        calculatePQ47({
          crop_type: pq47Crop,
          area_hectares: pq47Hectares,
          technology_type: 'DRIP_IRRIGATION',
          region: prof.region,
          district: prof.district,
          installation_cost_uzs: 250000000,
          financed_via_bank_loan: pq47LoanUsed,
          loan_principal_uzs: pq47LoanAmount,
        }),
        calculatePF82({
          crop_type: pf82Crop,
          harvest_year: 2026,
          loan_principal_uzs: 150000000,
          contractual_interest_rate_pct: pf82ContractRate,
          outstanding_balance_uzs: pf82Balance,
          days_on_time_repaid: pf82Days,
          has_overdue_debt: pf82Overdue,
        }),
        fetchRegulatorySources(true),
      ]);

      setMatchedSubsidies(matches);
      setSubsidyImpact(impact);
      setPq47Result(pqRes);
      setPf82Result(pfRes);
      setRegulatorySources(regSources);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Ma'lumotlarni yuklashda xatolik yuz berdi.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(selectedOrgId);
  }, [selectedOrgId]);

  // Handle Interactive recalculation of PQ47
  const handleRecalculatePQ47 = async () => {
    try {
      const res = await calculatePQ47({
        crop_type: pq47Crop,
        area_hectares: pq47Hectares,
        technology_type: 'DRIP_IRRIGATION',
        region: leaseProfile?.region || 'Andijon viloyati',
        district: leaseProfile?.district || 'Asaka tumani',
        installation_cost_uzs: 250000000,
        financed_via_bank_loan: pq47LoanUsed,
        loan_principal_uzs: pq47LoanAmount,
      });
      setPq47Result(res);
    } catch (err: any) {
      alert(`PQ-47 hisoblashda xatolik: ${err.message}`);
    }
  };

  // Handle Interactive recalculation of PF82
  const handleRecalculatePF82 = async () => {
    try {
      const res = await calculatePF82({
        crop_type: pf82Crop,
        harvest_year: 2026,
        loan_principal_uzs: 150000000,
        contractual_interest_rate_pct: pf82ContractRate,
        outstanding_balance_uzs: pf82Balance,
        days_on_time_repaid: pf82Days,
        has_overdue_debt: pf82Overdue,
      });
      setPf82Result(res);
    } catch (err: any) {
      alert(`PF-82 hisoblashda xatolik: ${err.message}`);
    }
  };

  const formatUZS = (val: number | undefined | null) => {
    if (val === undefined || val === null) return "0 so'm";
    return `${Math.round(val).toLocaleString('uz-UZ')} so'm`;
  };

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header Section */}
        <div className="bg-white rounded-2xl p-6 sm:p-8 shadow-sm border border-slate-200">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 flex items-center gap-1.5">
                  <Landmark className="w-3.5 h-3.5" />
                  ASSIGNMENT 6 • YURIDIK VA MOLIYAVIY MODUL
                </span>
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
                  VMQ-613 • PQ-47 • PF-82
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Qishloq Xo'jaligi Garov & Subsidiya Intellekti
              </h1>
              <p className="mt-1 text-sm text-slate-600 max-w-3xl">
                O'zbekiston Respublikasi qonunchiligi asosida yer ijara huquqini kredit garoviga qo'yishga tayyorlash (VMQ-613), 
                indikativ DCF baholash, hamda suv tejovchi (PQ-47) va paxta-g'alla (PF-82) davlat subsidiyalarini hisoblash.
              </p>
            </div>

            {/* Scenario Selector */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <label className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                Xo'jalik Ssenariysi:
              </label>
              <select
                value={selectedOrgId}
                onChange={(e) => setSelectedOrgId(e.target.value)}
                className="bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="scenario-small-farmer">Andijon Baraka Fermer (65 ga)</option>
                <option value="scenario-exporter">Samarqand Bog'dorchilik Agrofirmasi (120 ga)</option>
                <option value="scenario-cluster">Qashqadaryo Agrosanoat Klasteri (2,500 ga)</option>
              </select>
            </div>
          </div>

          {/* Statutory Non-Certification Legal Disclaimer */}
          <div className="mt-6 p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold uppercase tracking-wider">Rasmiy Ogohlantirish & Huquqiy Cheklov (Disclaimer):</span>
              <p className="mt-1 leading-relaxed text-amber-800">
                Mazkur modul O'zbekiston Respublikasi Vazirlar Mahkamasining 613-son qarori (VMQ-613) va Prezident qarorlari (PQ-47, PF-82) 
                asosida fermerlarga dastlabki yo'l-yo'riq ko'rsatuvchi <strong>indikativ raqamli vositadir</strong>. U baholash faoliyati to'g'risidagi 
                qonunchilikka binoan litsenziyaga ega mustaqil baholovchi tashkilotning rasmiy hisoboti yoki tijorat bankining qat'iy kredit qarori 
                o'rnini bosmaydi.
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="mt-6 flex border-b border-slate-200 space-x-8">
            <button
              onClick={() => setActiveTab('collateral')}
              className={`pb-4 text-sm font-semibold flex items-center gap-2 border-b-2 transition-colors ${
                activeTab === 'collateral'
                  ? 'border-emerald-600 text-emerald-600'
                  : 'border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300'
              }`}
            >
              <Landmark className="w-4 h-4" />
              Module A: Yer Ijara Huquqi Garovi (VMQ-613)
            </button>

            <button
              onClick={() => setActiveTab('subsidies')}
              className={`pb-4 text-sm font-semibold flex items-center gap-2 border-b-2 transition-colors ${
                activeTab === 'subsidies'
                  ? 'border-emerald-600 text-emerald-600'
                  : 'border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300'
              }`}
            >
              <Coins className="w-4 h-4" />
              Module B: Davlat Subsidiyalari (PQ-47 & PF-82)
            </button>

            <button
              onClick={() => setActiveTab('regulatory')}
              className={`pb-4 text-sm font-semibold flex items-center gap-2 border-b-2 transition-colors ${
                activeTab === 'regulatory'
                  ? 'border-emerald-600 text-emerald-600'
                  : 'border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300'
              }`}
            >
              <FileText className="w-4 h-4" />
              Qonunchilik & Lex.uz Reestri
            </button>
          </div>
        </div>

        {/* Loading / Error States */}
        {loading && (
          <div className="bg-white rounded-2xl p-12 text-center border border-slate-200">
            <RefreshCw className="w-8 h-8 animate-spin text-emerald-600 mx-auto mb-3" />
            <p className="text-sm font-medium text-slate-600">
              Qonunchilik mezonlari va moliyaviy modellar hisoblanmoqda...
            </p>
          </div>
        )}

        {error && (
          <div className="bg-rose-50 border border-rose-200 p-6 rounded-2xl text-rose-900 text-sm flex items-center gap-3">
            <XCircle className="w-6 h-6 text-rose-600 flex-shrink-0" />
            <div>
              <span className="font-bold">Xatolik:</span> {error}
            </div>
          </div>
        )}

        {!loading && !error && activeTab === 'collateral' && leaseProfile && screeningResult && valuationResult && sensitivityAnalysis && checklist && (
          <div className="space-y-6">
            {/* Top Cards: Legal Eligibility & Readiness */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 uppercase">VMQ-613 Huquqiy Holati</span>
                <div className="mt-2 flex items-center gap-2">
                  {screeningResult.is_eligible ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  ) : (
                    <XCircle className="w-5 h-5 text-rose-600" />
                  )}
                  <span className={`text-base font-bold ${screeningResult.is_eligible ? 'text-emerald-700' : 'text-rose-700'}`}>
                    {screeningResult.overall_legal_status_uz}
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  {screeningResult.post_maturity_buffer_years} yillik bufer (Kamida 5 yil talab etiladi)
                </p>
              </div>

              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 uppercase">Indikativ Bozor Qiymati (DCF)</span>
                <div className="mt-2 text-xl font-bold text-slate-900">
                  {formatUZS(valuationResult.indicative_market_value_uzs)}
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  {valuationResult.valuation_horizon_years} yillik cheklangan ijara muddati bo'yicha
                </p>
              </div>

              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 uppercase">Maksimal Garov Ta'minoti (LTV)</span>
                <div className="mt-2 text-xl font-bold text-emerald-700">
                  {formatUZS(valuationResult.max_pledge_value_uzs)}
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  LTV stavkasi: {valuationResult.target_ltv_pct}% (Tijorat banki me'yori)
                </p>
              </div>

              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 uppercase">Hujjatlar Tayyorgarligi</span>
                <div className="mt-2 text-xl font-bold text-blue-700">
                  {checklist.readiness_percentage}%
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  {checklist.available_count} / {checklist.total_documents} hujjat mavjud
                </p>
              </div>
            </div>

            {/* Section 1: VMQ-613 Statutory Screening Rule Checks */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                VMQ-613 Me'yoriy Talablar Screeningi (O'tkazilgan Tekshiruvlar)
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                2025-yil 30-sentabrdagi 613-son VMQ talablariga muvofiq qat'iy kalendar va huquqiy tekshiruvlar natijasi.
              </p>

              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr className="bg-slate-50 border-y border-slate-200 text-xs font-bold text-slate-600 uppercase">
                      <th className="py-3 px-4">Qoida / Band</th>
                      <th className="py-3 px-4">Me'yoriy Asos</th>
                      <th className="py-3 px-4">Holat</th>
                      <th className="py-3 px-4">Tafsilot & Huquqiy Xulosa</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {screeningResult.rule_checks.map((rule) => {
                      const isOk = rule.status === 'COMPLIANT' || rule.status === 'CONDITIONAL_PASS';
                      return (
                        <tr key={rule.rule_id} className="hover:bg-slate-50/50">
                          <td className="py-3 px-4 font-semibold text-slate-900">{rule.rule_name_uz}</td>
                          <td className="py-3 px-4 text-xs font-mono text-slate-600">{rule.statutory_basis}</td>
                          <td className="py-3 px-4">
                            <span
                              className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold ${
                                isOk ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                              }`}
                            >
                              {isOk ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                              {rule.status_label_uz}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-xs text-slate-700 leading-relaxed">
                            {rule.explanation_uz}
                            {rule.action_required_uz && (
                              <span className="block mt-1 font-semibold text-amber-700">
                                Tavsiya: {rule.action_required_uz}
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Section 2: Indicative DCF Valuation & Multi-Scenario Sensitivity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* DCF Valuation Parameters */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
                <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-emerald-600" />
                  Indikativ DCF Baholash Modeli Parametrlari
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Cheklangan ijara ufqiga asoslangan diskontlangan pul oqimlari modeli: PV = Σ [CF_t / (1 + r)^t]. 
                  Asossiz terminal qiymat (terminal value) mutlaqo kiritilmagan.
                </p>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <span className="text-slate-500">Yer Maydoni:</span>
                    <div className="font-bold text-slate-800 mt-1">{leaseProfile.area_hectares} gektar</div>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <span className="text-slate-500">Tuproq Bonitet Bali:</span>
                    <div className="font-bold text-slate-800 mt-1">
                      {valuationResult.soil_bonitet_score} ball (Koeffitsiyent: {valuationResult.bonitet_adjustment_factor}x)
                    </div>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <span className="text-slate-500">Diskont Stavkasi:</span>
                    <div className="font-bold text-slate-800 mt-1">{valuationResult.discount_rate_pct}% yillik</div>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <span className="text-slate-500">Ijara Qoldiq Muddati:</span>
                    <div className="font-bold text-slate-800 mt-1">{valuationResult.valuation_horizon_years} yil</div>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg col-span-2">
                    <span className="text-slate-500">Tuzatilgan Yillik Sof Daromad (1 ga):</span>
                    <div className="font-bold text-emerald-800 mt-1 text-sm">
                      {formatUZS(valuationResult.adjusted_annual_net_benefit_per_ha_uzs)} / gektar
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-200">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-semibold text-emerald-900">Jami Indikativ Bozor Qiymati:</span>
                    <span className="text-lg font-bold text-emerald-900">
                      {formatUZS(valuationResult.indicative_market_value_uzs)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center mt-2 pt-2 border-t border-emerald-200">
                    <span className="text-xs font-semibold text-emerald-800">Bank LTV Ta'minoti (65%):</span>
                    <span className="text-base font-bold text-emerald-800">
                      {formatUZS(valuationResult.max_pledge_value_uzs)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Multi-scenario Sensitivity Recalculation */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
                <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <Layers className="w-5 h-5 text-blue-600" />
                  Ko'p Ssenariyli Sezgirlik Tahlili (Haqiqiy Qayta Hisob)
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Hosildorlik va diskont stavkasi o'zgarishi bo'yicha mustaqil qayta hisoblangan uchta ssenariy.
                </p>

                <div className="space-y-3">
                  {/* Base */}
                  <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-slate-900">{sensitivityAnalysis.base_scenario.scenario_label_uz}</span>
                      <span className="text-xs font-bold text-slate-700">
                        {formatUZS(sensitivityAnalysis.base_scenario.indicative_valuation_uzs)}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 mt-1">
                      Diskont: {sensitivityAnalysis.base_scenario.discount_rate_pct}% • {sensitivityAnalysis.base_scenario.description_uz}
                    </p>
                  </div>

                  {/* Optimistic */}
                  <div className="p-3.5 rounded-xl border border-emerald-200 bg-emerald-50/50">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-emerald-900">
                        {sensitivityAnalysis.optimistic_scenario.scenario_label_uz} (+{sensitivityAnalysis.optimistic_scenario.variance_pct}%)
                      </span>
                      <span className="text-xs font-bold text-emerald-700">
                        {formatUZS(sensitivityAnalysis.optimistic_scenario.indicative_valuation_uzs)}
                      </span>
                    </div>
                    <p className="text-[11px] text-emerald-700 mt-1">
                      Diskont: {sensitivityAnalysis.optimistic_scenario.discount_rate_pct}% • {sensitivityAnalysis.optimistic_scenario.description_uz}
                    </p>
                  </div>

                  {/* Pessimistic */}
                  <div className="p-3.5 rounded-xl border border-rose-200 bg-rose-50/50">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-rose-900">
                        {sensitivityAnalysis.pessimistic_scenario.scenario_label_uz} ({sensitivityAnalysis.pessimistic_scenario.variance_pct}%)
                      </span>
                      <span className="text-xs font-bold text-rose-700">
                        {formatUZS(sensitivityAnalysis.pessimistic_scenario.indicative_valuation_uzs)}
                      </span>
                    </div>
                    <p className="text-[11px] text-rose-700 mt-1">
                      Diskont: {sensitivityAnalysis.pessimistic_scenario.discount_rate_pct}% • {sensitivityAnalysis.pessimistic_scenario.description_uz}
                    </p>
                  </div>
                </div>

                <div className="text-xs text-slate-600 bg-slate-100 p-3 rounded-lg">
                  <span className="font-semibold text-slate-800">Baholash diapazoni:</span>{' '}
                  {formatUZS(sensitivityAnalysis.volatility_range_uzs)} so'mlik noaniqlik oralig'i.
                </div>
              </div>
            </div>

            {/* Section 3: Document Preparation Checklist */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-4">
                <div>
                  <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                    <CheckSquare className="w-5 h-5 text-emerald-600" />
                    Garov Hujjatlarini Tayyorlash Nazorat Ro'yxati (9 ta Me'yoriy Hujjat)
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    VMQ-613 talablari va tijorat banki kredit qo'mitasiga taqdim etiladigan rasmiy paket.
                  </p>
                </div>
                <div className="px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800">
                  Tayyorgarlik: {checklist.readiness_percentage}% ({checklist.readiness_verdict_uz})
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {checklist.items.map((item) => {
                  let badgeClass = 'bg-slate-100 text-slate-700 border-slate-200';
                  if (item.status === 'AVAILABLE') badgeClass = 'bg-emerald-50 text-emerald-800 border-emerald-200';
                  if (item.status === 'MISSING') badgeClass = 'bg-rose-50 text-rose-800 border-rose-200';
                  if (item.status === 'NEEDS_VERIFICATION') badgeClass = 'bg-amber-50 text-amber-800 border-amber-200';

                  return (
                    <div key={item.id} className={`p-3.5 rounded-xl border ${badgeClass} text-xs flex flex-col justify-between`}>
                      <div>
                        <div className="flex justify-between items-start gap-2">
                          <span className="font-bold text-slate-900 leading-tight">{item.document_name_uz}</span>
                          <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-white/70">
                            {item.status_label_uz}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-600 mt-1">{item.description_uz}</p>
                      </div>
                      <div className="mt-3 pt-2 border-t border-slate-200/50 text-[10px] text-slate-500 flex justify-between items-center">
                        <span>Organ: {item.issuing_body_uz}</span>
                        <span className="font-mono text-[9px]">{item.statutory_reference}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Tab B: Subsidies Module */}
        {!loading && !error && activeTab === 'subsidies' && subsidyImpact && pq47Result && pf82Result && (
          <div className="space-y-6">
            {/* Top Cards: Subsidies Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 uppercase">Potentsial Subsidiya Imkoniyati</span>
                <div className="mt-2 text-xl font-bold text-emerald-700">
                  {formatUZS(subsidyImpact.total_potential_subsidy_uzs)}
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  {matchedSubsidies.filter((m) => m.eligibility_status === 'POTENTIALLY_ELIGIBLE').length} ta dastur bo'yicha mos
                </p>
              </div>

              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 uppercase">1-Bosqich (Dastlabki To'lov 50%)</span>
                <div className="mt-2 text-xl font-bold text-blue-700">
                  {formatUZS(subsidyImpact.immediate_cash_inflow_potential_uzs)}
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  Uskuna o'rnatilib dalolatnoma tuzilgach
                </p>
              </div>

              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 uppercase">2-Bosqich (Mavsumiy Shartli 50%)</span>
                <div className="mt-2 text-xl font-bold text-indigo-700">
                  {formatUZS(subsidyImpact.conditional_future_inflow_uzs)}
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  1 mavsum samarali ishlagandan so'ng
                </p>
              </div>

              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 uppercase">PF-82 Foiz Imtiyozi</span>
                <div className="mt-2 text-xl font-bold text-amber-700">
                  10 foiz bandi
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  O'z vaqtida qaytarilgan qarz qoldig'iga
                </p>
              </div>
            </div>

            {/* Interactive Calculators Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* PQ-47 Water Saving Calculator */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                    <Droplets className="w-5 h-5 text-blue-600" />
                    PQ-47: Suv Tejovchi Texnologiyalar Kalkulyatori
                  </h3>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                    PQ-47 Qarori
                  </span>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Tomchilatib sug'orish tizimi xarajatlarini qoplash: Paxta (8 mln), Sabzavot (6 mln), Bog' (10 mln), Uzum (8 mln so'm/ga).
                </p>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <label className="font-semibold text-slate-700 block mb-1">Ekin Turi:</label>
                    <select
                      value={pq47Crop}
                      onChange={(e) => setPq47Crop(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-medium"
                    >
                      <option value="Paxta">Paxta (8 mln/ga)</option>
                      <option value="Sabzavot">Sabzavot (6 mln/ga)</option>
                      <option value="Bog'dorchilik">Mevali bog' (10 mln/ga)</option>
                      <option value="Uzumzor">Uzumzor (8 mln/ga)</option>
                    </select>
                  </div>

                  <div>
                    <label className="font-semibold text-slate-700 block mb-1">Maydon (Gektar):</label>
                    <input
                      type="number"
                      value={pq47Hectares}
                      onChange={(e) => setPq47Hectares(parseFloat(e.target.value) || 0)}
                      className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-medium"
                    />
                  </div>

                  <div className="col-span-2 flex items-center gap-2 mt-1">
                    <input
                      type="checkbox"
                      id="pqLoan"
                      checked={pq47LoanUsed}
                      onChange={(e) => setPq47LoanUsed(e.target.checked)}
                      className="rounded text-blue-600"
                    />
                    <label htmlFor="pqLoan" className="text-xs font-semibold text-slate-700 cursor-pointer">
                      Bank krediti orqali moliyalashtirilgan (4 foiz bandi kompensatsiyasi)
                    </label>
                  </div>
                </div>

                <button
                  onClick={handleRecalculatePQ47}
                  className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition-colors"
                >
                  PQ-47 Subsidiyasini Qayta Hisoblash
                </button>

                {/* PQ-47 Calculation Output Card */}
                {pq47Result && (
                  <div className="p-4 bg-blue-50/70 rounded-xl border border-blue-200 text-xs space-y-2">
                    <div className="flex justify-between items-center font-bold text-blue-900">
                      <span>Jami Kutilayotgan Subsidiya:</span>
                      <span className="text-base">{formatUZS(pq47Result.estimated_total_subsidy_uzs)}</span>
                    </div>
                    <div className="flex justify-between text-slate-600 text-[11px]">
                      <span>1-bosqich (Dastlabki 50%):</span>
                      <span className="font-semibold text-slate-800">{formatUZS(pq47Result.phase_1_initial_disbursement_uzs)}</span>
                    </div>
                    <div className="flex justify-between text-slate-600 text-[11px]">
                      <span>2-bosqich (Shartli 50%):</span>
                      <span className="font-semibold text-slate-800">{formatUZS(pq47Result.phase_2_conditional_disbursement_uzs)}</span>
                    </div>
                    {pq47Result.interest_compensation_annual_uzs && (
                      <div className="flex justify-between text-emerald-700 text-[11px] pt-1 border-t border-blue-200">
                        <span>Yillik 4% kredit kompensatsiyasi:</span>
                        <span className="font-bold">{formatUZS(pq47Result.interest_compensation_annual_uzs)}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* PF-82 Cotton & Wheat Financial Support Calculator */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                    <Percent className="w-5 h-5 text-emerald-600" />
                    PF-82: Paxta & G'alla Foiz Kompensatsiyasi
                  </h3>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                    PF-82 Farmoni
                  </span>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  O'z vaqtida so'ndirilgan kreditlar bo'yicha yillik 10 foiz bandi davlat tomonidan kompensatsiya qilinadi.
                </p>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <label className="font-semibold text-slate-700 block mb-1">Ekin Turi:</label>
                    <select
                      value={pf82Crop}
                      onChange={(e) => setPf82Crop(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-medium"
                    >
                      <option value="Paxta">Paxta xom ashyosi</option>
                      <option value="G'alla">G'alla (Bug'doy)</option>
                      <option value="Boshqa">Boshqa (Kompensatsiya qo'llanilmaydi)</option>
                    </select>
                  </div>

                  <div>
                    <label className="font-semibold text-slate-700 block mb-1">Qarz Qoldig'i (UZS):</label>
                    <input
                      type="number"
                      value={pf82Balance}
                      onChange={(e) => setPf82Balance(parseFloat(e.target.value) || 0)}
                      className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-medium"
                    />
                  </div>

                  <div>
                    <label className="font-semibold text-slate-700 block mb-1">Shartnoma Foizi (%):</label>
                    <input
                      type="number"
                      value={pf82ContractRate}
                      onChange={(e) => setPf82ContractRate(parseFloat(e.target.value) || 0)}
                      className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-medium"
                    />
                  </div>

                  <div>
                    <label className="font-semibold text-slate-700 block mb-1">Intizomli Kunlar Soni:</label>
                    <input
                      type="number"
                      value={pf82Days}
                      onChange={(e) => setPf82Days(parseInt(e.target.value) || 0)}
                      className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-medium"
                    />
                  </div>

                  <div className="col-span-2 flex items-center gap-2 mt-1">
                    <input
                      type="checkbox"
                      id="pfOverdue"
                      checked={pf82Overdue}
                      onChange={(e) => setPf82Overdue(e.target.checked)}
                      className="rounded text-rose-600"
                    />
                    <label htmlFor="pfOverdue" className="text-xs font-semibold text-rose-700 cursor-pointer">
                      Muddati o'tgan qarzdorlik (prosrochka) mavjud (PF-82 imtiyozini to'xtatadi)
                    </label>
                  </div>
                </div>

                <button
                  onClick={handleRecalculatePF82}
                  className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold transition-colors"
                >
                  PF-82 Kompensatsiyasini Qayta Hisoblash
                </button>

                {/* PF-82 Calculation Output Card */}
                {pf82Result && (
                  <div
                    className={`p-4 rounded-xl border text-xs space-y-2 ${
                      pf82Result.is_eligible ? 'bg-emerald-50/70 border-emerald-200' : 'bg-rose-50/70 border-rose-200'
                    }`}
                  >
                    <div className="flex justify-between items-center font-bold">
                      <span className={pf82Result.is_eligible ? 'text-emerald-900' : 'text-rose-900'}>
                        Kompensatsiya Holati:
                      </span>
                      <span>{pf82Result.is_eligible ? 'MUVOFIQ (10 foiz bandi)' : 'RAD ETILGAN'}</span>
                    </div>
                    {pf82Result.is_eligible ? (
                      <>
                        <div className="flex justify-between text-slate-600 text-[11px]">
                          <span>Fermer uchun yakuniy samarali foiz stavkasi:</span>
                          <span className="font-bold text-emerald-800">{pf82Result.net_farmer_interest_rate_pct}%</span>
                        </div>
                        <div className="flex justify-between text-slate-900 text-sm font-bold pt-1 border-t border-emerald-200">
                          <span>Hisoblangan Davlat Kompensatsiyasi:</span>
                          <span className="text-emerald-700">{formatUZS(pf82Result.indicative_interest_compensation_uzs)}</span>
                        </div>
                      </>
                    ) : (
                      <p className="text-rose-800 text-[11px] leading-relaxed">{pf82Result.explanation_uz}</p>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Section: Matched Programs Table */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Coins className="w-5 h-5 text-emerald-600" />
                Davlat Subsidiyalari Dasturlari Ro'yxati & Moslik Tahlili
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Fermer xo'jaligi profili bo'yicha 5 ta deterministik statusda o'tkazilgan tahlil natijalari.
              </p>

              <div className="mt-4 divide-y divide-slate-100">
                {matchedSubsidies.map((match) => {
                  let badge = 'bg-slate-100 text-slate-700';
                  if (match.eligibility_status === 'POTENTIALLY_ELIGIBLE') badge = 'bg-emerald-100 text-emerald-800';
                  if (match.eligibility_status === 'NOT_ELIGIBLE_UNDER_VERIFIED_RULE') badge = 'bg-rose-100 text-rose-800';
                  if (match.eligibility_status === 'MORE_INFORMATION_REQUIRED') badge = 'bg-amber-100 text-amber-800';

                  return (
                    <div key={match.program.id} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div className="space-y-1 max-w-2xl">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-900 text-sm">{match.program.program_name_uz}</span>
                          <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-semibold">
                            {match.program.program_code}
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 leading-relaxed">{match.program.rate_description_uz}</p>
                        <div className="flex items-center gap-4 text-[11px] text-slate-500">
                          <span>Boshqaruvchi: {match.program.managing_authority_uz}</span>
                          <a
                            href={match.program.legal_source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline flex items-center gap-1"
                          >
                            <span>Lex.uz ({match.program.legal_source_code})</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      </div>

                      <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${badge}`}>
                          {match.eligibility_label_uz}
                        </span>
                        {match.indicative_support_amount_uzs && (
                          <span className="text-sm font-bold text-emerald-800">
                            {formatUZS(match.indicative_support_amount_uzs)}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Financial Impact Synthesis Card */}
            <div className="p-6 rounded-2xl bg-slate-900 text-white space-y-3">
              <h3 className="text-base font-bold flex items-center gap-2 text-emerald-400">
                <Sparkles className="w-5 h-5 text-emerald-400" />
                Moliyaviy Dvigatel Bilan Integratsiya & Kassa Ta'siri
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">{subsidyImpact.impact_on_cash_flow_uz}</p>
              <p className="text-xs text-emerald-300 leading-relaxed">{subsidyImpact.impact_on_dscr_uz}</p>
            </div>
          </div>
        )}

        {/* Tab C: Regulatory Registry */}
        {!loading && !error && activeTab === 'regulatory' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <FileText className="w-5 h-5 text-emerald-600" />
                O'zbekiston Respublikasi Rasmiy Qonunchilik Manbalari Reestri
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                AgroHisob CFO platformasi tomonidan to'liq verifikatsiya qilingan va Lex.uz rasmiy bazasiga bog'langan me'yoriy hujjatlar.
              </p>

              <div className="mt-6 space-y-4">
                {regulatorySources.map((source) => (
                  <div key={source.id} className="p-5 rounded-xl border border-slate-200 bg-slate-50/50 space-y-3">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="px-2.5 py-0.5 rounded bg-emerald-100 text-emerald-800 text-xs font-bold">
                            {source.document_code}
                          </span>
                          <span className="text-xs text-slate-500">
                            Amal qilish sanasi: {source.effective_from}
                          </span>
                        </div>
                        <h3 className="font-bold text-slate-900 text-base mt-1">{source.document_title_uz}</h3>
                      </div>

                      <a
                        href={source.official_lex_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-slate-300 text-blue-600 hover:text-blue-800 hover:border-blue-300 text-xs font-semibold shadow-sm transition-colors"
                      >
                        <span>Lex.uz da ko'rish</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>

                    <div className="text-xs text-slate-700 bg-white p-3.5 rounded-lg border border-slate-200 space-y-1.5">
                      <span className="font-bold text-slate-900 block mb-1">Asosiy Qoidalar & Talablar:</span>
                      {Object.entries(source.key_clauses_summary_uz).map(([clause, summary]) => (
                        <div key={clause} className="flex items-start gap-2 text-slate-600">
                          <span className="font-mono text-emerald-700 font-bold flex-shrink-0">•</span>
                          <span>{summary}</span>
                        </div>
                      ))}
                    </div>

                    <div className="flex items-center gap-2 text-[11px] text-slate-500">
                      <span>Kimlarga tatbiq etiladi:</span>
                      <span className="font-semibold text-slate-700">
                        {source.applicable_beneficiaries_uz.join(', ')}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
