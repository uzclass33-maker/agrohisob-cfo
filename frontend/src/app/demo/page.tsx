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
import Reveal from '@/components/Reveal';

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
        return <Wheat className="h-6 w-6 text-agro-700" />;
      case 'exporter':
        return <Truck className="h-6 w-6 text-sky-700" />;
      case 'cluster':
        return <Building2 className="h-6 w-6 text-navy-800" />;
      default:
        return <Wheat className="h-6 w-6 text-agro-700" />;
    }
  };

  return (
    <div className="page-shell py-10 lg:py-14">
      <div className="container-x">
        {/* Header */}
        <Reveal>
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-1.5 rounded-full border border-agro-200 bg-agro-50 px-3 py-1 text-xs font-semibold text-agro-800">
              <CheckCircle className="h-3.5 w-3.5 text-agro-700" />
              <span>Sintetik Agrobiznes Modellari</span>
            </div>
            <h1 className="mt-4 text-3xl font-bold tracking-tight text-navy-950 sm:text-4xl">
              Sintetik Agrobiznes Ssenariylari Tanlagichi
            </h1>
            <p className="mt-3 text-sm leading-relaxed text-slate-600 sm:text-base">
              Quyidagi 3 ta sintetik ssenariy O'zbekistonning haqiqiy agrar tsikllari, paxta/g'alla/bog'dorchilik 
              tannarxlari va kassa uzilishlari asosida deterministik aniqlikda ishlab chiqilgan.
            </p>
          </div>
        </Reveal>

        {/* Synthetic Disclaimer Banner */}
        <Reveal delay={80}>
          <div className="mt-6 flex items-start space-x-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-xs text-amber-900 sm:text-sm">
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
            <div>
              <span className="font-bold">Eslatma (Synthetic Benchmark):</span> Barcha ko'rsatkichlar 
              (boshlang'ich kassa, oylik faktura tushumlari, o'g'it/yoqilg'i xarajatlari, kredit to'lovlari) 
              gipotetik namoyish uchun mo'ljallangan va bir-biri bilan 100% matematik muvozanatlangan.
            </div>
          </div>
        </Reveal>

        {loading ? (
          <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="card h-96 animate-pulse p-6">
                <div className="mb-4 h-12 w-12 rounded-xl bg-slate-200"></div>
                <div className="mb-3 h-6 w-3/4 rounded bg-slate-200"></div>
                <div className="mb-2 h-4 w-full rounded bg-slate-100"></div>
                <div className="mb-6 h-4 w-2/3 rounded bg-slate-100"></div>
                <div className="mb-4 h-20 rounded-lg bg-slate-100"></div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="mt-8 rounded-xl border border-rose-200 bg-rose-50 p-6 text-center text-rose-800">
            <p className="font-semibold">{error}</p>
            <p className="mt-2 text-xs text-rose-600">
              FastAPI backendni ishga tushirish: <code>cd backend; uvicorn app.main:app --port 8000</code>
            </p>
          </div>
        ) : (
          <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
            {scenarios.map((sc, i) => (
              <Reveal key={sc.id} delay={i * 80} className="h-full">
                <div className="card card-hover flex h-full flex-col justify-between overflow-hidden">
                  <div className="p-6">
                    {/* Category Pill & Icon */}
                    <div className="mb-4 flex items-center justify-between">
                      <span className="inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-700">
                        {sc.category_label}
                      </span>
                      <div className="rounded-lg border border-slate-200/80 bg-white p-2.5 shadow-card">
                        {getCategoryIcon(sc.category)}
                      </div>
                    </div>

                    {/* Title & Location */}
                    <h3 className="text-xl font-bold tracking-tight text-navy-950">
                      {sc.name}
                    </h3>
                    <div className="mt-1 flex items-center text-xs text-slate-500">
                      <MapPin className="mr-1 h-3.5 w-3.5 text-slate-400" />
                      <span>{sc.region}, {sc.district}</span>
                    </div>

                    <p className="mt-3 text-xs leading-relaxed text-slate-600">
                      {sc.description}
                    </p>

                    {/* Key Metrics Grid */}
                    <div className="mt-5 grid grid-cols-2 gap-3 rounded-lg border border-slate-100 bg-slate-50/80 p-3.5 text-xs">
                      <div>
                        <span className="block text-slate-400">Ekin Maydoni:</span>
                        <span className="num font-bold text-navy-900">{sc.hectares} gektar</span>
                      </div>
                      <div>
                        <span className="block text-slate-400">Asosiy Ekin:</span>
                        <span className="block truncate font-bold text-navy-900">{sc.main_crop}</span>
                      </div>
                      <div>
                        <span className="block text-slate-400">Boshlang'ich Kassa:</span>
                        <span className="num font-bold text-agro-700">{formatCompactUZS(sc.initial_cash_uzs)}</span>
                      </div>
                      <div>
                        <span className="block text-slate-400">Mavjud Qarz Yuki:</span>
                        <span className="num font-bold text-rose-700">{formatCompactUZS(sc.debt_load_uzs)}</span>
                      </div>
                    </div>

                    {/* Dynamic Trait Note */}
                    <div className="mt-3 rounded-lg border border-agro-100 bg-agro-50 p-2.5 text-xs text-agro-900">
                      <span className="mb-0.5 block font-semibold">Mavsumiylik belgisi:</span>
                      {sc.key_dynamics}
                    </div>
                  </div>

                  {/* Card Actions */}
                  <div className="space-y-2 border-t border-slate-100 bg-slate-50/80 p-6">
                    <button
                      onClick={() => router.push(`/dashboard?scenario=${sc.id}`)}
                      className="flex w-full items-center justify-center gap-2 rounded-lg bg-agro-700 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all duration-200 hover:bg-agro-800 active:translate-y-px"
                    >
                      <span>Moliya Panelida Tahlil Qilish</span>
                      <ArrowRight className="h-4 w-4" />
                    </button>

                    <div className="grid grid-cols-2 gap-2 pt-1 text-xs">
                      <Link
                        href={`/scenario-analysis?scenario=${sc.id}`}
                        className="inline-flex items-center justify-center gap-1 rounded-lg border border-slate-200 bg-white px-2 py-2 font-medium text-slate-700 transition-colors hover:bg-slate-100"
                      >
                        <Sliders className="h-3.5 w-3.5 text-sky-700" />
                        <span>Stress-Test</span>
                      </Link>
                      <Link
                        href={`/credit-report?scenario=${sc.id}`}
                        className="inline-flex items-center justify-center gap-1 rounded-lg border border-slate-200 bg-white px-2 py-2 font-medium text-slate-700 transition-colors hover:bg-slate-100"
                      >
                        <ShieldCheck className="h-3.5 w-3.5 text-navy-700" />
                        <span>Kredit Dosyesi</span>
                      </Link>
                    </div>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
