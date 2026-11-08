'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { fetchScenarios } from '@/lib/api';
import { SyntheticScenarioMeta } from '@/lib/types';
import { formatCompactUZS } from '@/lib/formatters';
import { 
  Building2, Wheat, Truck, AlertCircle, ArrowRight, 
  MapPin, CheckCircle, TrendingUp, Sliders, ShieldCheck 
} from 'lucide-react';

export default function DemoSelectorPage() {
  const router = useRouter();
  const [scenarios, setScenarios] = useState<SyntheticScenarioMeta[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = await fetchScenarios();
        setScenarios(data);
      } catch (err: any) {
        console.error(err);
        setError("Backend bilan aloqa o'rnatilmadi. Iltimos FastAPI serveri ishlayotganligini tekshiring.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const getCategoryIcon = (cat: string) => {
    switch (cat) {
      case 'small_farmer':
        return <Wheat className="w-6 h-6 text-emerald-600" />;
      case 'exporter':
        return <Truck className="w-6 h-6 text-sky-600" />;
      case 'cluster':
        return <Building2 className="w-6 h-6 text-indigo-600" />;
      default:
        return <Wheat className="w-6 h-6 text-emerald-600" />;
    }
  };

  return (
    <div className="py-10 bg-slate-50 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="max-w-3xl mb-8">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-agro-100 text-agro-800 text-xs font-semibold mb-3">
            <CheckCircle className="w-3.5 h-3.5 text-agro-600" />
            <span>Sintetik Agrobiznes Modellari</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Sintetik Agrobiznes Ssenariylari Tanlagichi
          </h1>
          <p className="mt-2 text-slate-600 text-sm sm:text-base leading-relaxed">
            Quyidagi 3 ta sintetik ssenariy O'zbekistonning haqiqiy agrar tsikllari, paxta/g'alla/bog'dorchilik 
            tannarxlari va kassa uzilishlari asosida deterministik aniqlikda ishlab chiqilgan.
          </p>
        </div>

        {/* Synthetic Disclaimer Banner */}
        <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-xl mb-8 flex items-start space-x-3 text-amber-900 text-xs sm:text-sm">
          <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Eslatma (Synthetic Benchmark):</span> Barcha ko'rsatkichlar 
            (boshlang'ich kassa, oylik faktura tushumlari, o'g'it/yoqilg'i xarajatlari, kredit to'lovlari) 
            gipotetik namoyish uchun mo'ljallangan va bir-biri bilan 100% matematik muvozanatlangan.
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white p-6 rounded-2xl border border-slate-200 animate-pulse h-96">
                <div className="w-12 h-12 bg-slate-200 rounded-xl mb-4"></div>
                <div className="h-6 bg-slate-200 rounded w-3/4 mb-3"></div>
                <div className="h-4 bg-slate-100 rounded w-full mb-2"></div>
                <div className="h-4 bg-slate-100 rounded w-2/3 mb-6"></div>
                <div className="h-20 bg-slate-100 rounded mb-4"></div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="bg-rose-50 border border-rose-200 text-rose-800 p-6 rounded-2xl text-center">
            <p className="font-semibold">{error}</p>
            <p className="text-xs text-rose-600 mt-2">
              FastAPI backendni ishga tushirish: <code>cd backend; uvicorn app.main:app --port 8000</code>
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {scenarios.map((sc) => (
              <div
                key={sc.id}
                className="bg-white rounded-2xl border border-slate-200 hover:border-agro-500 hover:shadow-lg transition-all flex flex-col justify-between overflow-hidden"
              >
                <div className="p-6">
                  {/* Category Pill & Icon */}
                  <div className="flex justify-between items-center mb-4">
                    <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 text-xs font-semibold">
                      {sc.category_label}
                    </span>
                    <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                      {getCategoryIcon(sc.category)}
                    </div>
                  </div>

                  {/* Title & Location */}
                  <h3 className="text-xl font-bold text-slate-900 tracking-tight mb-1">
                    {sc.name}
                  </h3>
                  <div className="flex items-center text-xs text-slate-500 mb-4">
                    <MapPin className="w-3.5 h-3.5 mr-1 text-slate-400" />
                    <span>{sc.region}, {sc.district}</span>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed mb-5">
                    {sc.description}
                  </p>

                  {/* Key Metrics Grid */}
                  <div className="grid grid-cols-2 gap-3 p-3.5 rounded-xl bg-slate-50 border border-slate-100 mb-5 text-xs">
                    <div>
                      <span className="text-slate-400 block">Ekin Maydoni:</span>
                      <span className="font-bold text-slate-800">{sc.hectares} gektar</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Asosiy Ekin:</span>
                      <span className="font-bold text-slate-800 truncate block">{sc.main_crop}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Boshlang'ich Kassa:</span>
                      <span className="font-bold text-emerald-700">{formatCompactUZS(sc.initial_cash_uzs)}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Mavjud Qarz Yuki:</span>
                      <span className="font-bold text-rose-700">{formatCompactUZS(sc.debt_load_uzs)}</span>
                    </div>
                  </div>

                  {/* Dynamic Trait Note */}
                  <div className="text-xs bg-agro-50 text-agro-900 p-2.5 rounded-lg border border-agro-100 mb-2">
                    <span className="font-semibold block mb-0.5">Mavsumiylik belgisi:</span>
                    {sc.key_dynamics}
                  </div>
                </div>

                {/* Card Actions */}
                <div className="p-6 bg-slate-50 border-t border-slate-100 space-y-2">
                  <button
                    onClick={() => router.push(`/dashboard?scenario=${sc.id}`)}
                    className="w-full inline-flex items-center justify-center px-4 py-2.5 rounded-xl text-sm font-semibold text-white bg-agro-600 hover:bg-agro-700 shadow-sm transition"
                  >
                    <span>Moliya Panelida Tahlil Qilish</span>
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </button>

                  <div className="grid grid-cols-2 gap-2 pt-1 text-xs">
                    <Link
                      href={`/scenario-analysis?scenario=${sc.id}`}
                      className="inline-flex items-center justify-center py-2 px-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 font-medium transition text-center"
                    >
                      <Sliders className="w-3.5 h-3.5 mr-1 text-sky-600" />
                      <span>Stress-Test</span>
                    </Link>
                    <Link
                      href={`/credit-report?scenario=${sc.id}`}
                      className="inline-flex items-center justify-center py-2 px-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 font-medium transition text-center"
                    >
                      <ShieldCheck className="w-3.5 h-3.5 mr-1 text-indigo-600" />
                      <span>Kredit Dosyesi</span>
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
