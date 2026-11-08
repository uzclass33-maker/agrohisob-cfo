'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { 
  UploadCloud, FileSpreadsheet, CheckCircle2, Shield, 
  AlertCircle, ArrowRight, FileCheck, Layers, Info 
} from 'lucide-react';

export default function DataImportPage() {
  const [activeTab, setActiveTab] = useState<'efaktura' | 'bank' | 'kadastr'>('efaktura');
  const [zeroRetention, setZeroRetention] = useState<boolean>(true);
  const [mockUploaded, setMockUploaded] = useState<boolean>(true);

  const sampleParsedTransactions = [
    {
      date: '2026-03-12',
      direction: 'OUTFLOW',
      amount: "28 000 000 so'm",
      category: 'O\'g\'it va agroximiya (FERTILIZER_CHEMICALS)',
      mxik: '20.15.10.101',
      counterparty: '«Farg\'onaAzot» AJ',
      doc: 'SF-2026/0491',
      status: 'MXIK Tasdiqlangan'
    },
    {
      date: '2026-03-24',
      direction: 'OUTFLOW',
      amount: "18 000 000 so'm",
      category: 'Dizel va yoqilg\'i (FUEL_LUBRICANTS)',
      mxik: '19.20.21.000',
      counterparty: '«O\'zbekneftgaz» YoQSh',
      doc: 'E-FAKT-8849',
      status: 'MXIK Tasdiqlangan'
    },
    {
      date: '2026-06-15',
      direction: 'INFLOW',
      amount: "85 000 000 so'm",
      category: 'Hosil sotuvi (CROP_SALES)',
      mxik: '01.13.12.000',
      counterparty: '«Toshkent Agro Logistika» MChJ',
      doc: 'SF-2026/1102',
      status: 'MXIK Tasdiqlangan'
    },
    {
      date: '2026-07-20',
      direction: 'INFLOW',
      amount: "160 000 000 so'm",
      category: 'Sabzavot tushumlari (CROP_SALES)',
      mxik: '01.13.34.000',
      counterparty: '«Food City Tashkent» Ulgurji Bozor',
      doc: 'SF-2026/1844',
      status: 'MXIK Tasdiqlangan'
    }
  ];

  return (
    <div className="py-10 bg-slate-50 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        
        {/* Title */}
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-agro-100 text-agro-800 text-xs font-semibold mb-3">
            <FileSpreadsheet className="w-3.5 h-3.5 text-agro-600" />
            <span>Smart Data Ingestion</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Soliq E-Faktura & Bank Aylanmasi Importi
          </h1>
          <p className="mt-2 text-slate-600 text-sm sm:text-base leading-relaxed">
            Soliq.uz yoki 1C dan yuklab olingan elektron faktura va bank ko'chirmalarini yuklang. 
            Tizim MXIK (IKPU) kodlari bo'yicha xarajatlarni agronomik moddalarga avtomatik ajratadi.
          </p>
        </div>

        {/* Security & Zero Retention Notice */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start space-x-3">
            <Shield className="w-6 h-6 text-agro-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-bold text-slate-900">
                O'zbekiston Qonunchiligi (O'RQ-547) va Xavfsizlik Kafolati
              </h4>
              <p className="text-xs text-slate-500 mt-0.5">
                Moliyaviy ma'lumotlar faqat operativ xotirada tahlil qilinadi va mijoz xohishiga ko'ra darhol o'chiriladi.
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
              <span className="ml-2 text-xs font-semibold text-slate-700">Zero-Retention Mode</span>
            </label>
          </div>
        </div>

        {/* Upload Tabs & Dropzone */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="border-b border-slate-200 bg-slate-50/50 p-2 flex space-x-2">
            <button
              onClick={() => setActiveTab('efaktura')}
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition ${
                activeTab === 'efaktura'
                  ? 'bg-white text-agro-700 shadow-sm border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              1. Soliq E-Faktura (Excel / XML)
            </button>
            <button
              onClick={() => setActiveTab('bank')}
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition ${
                activeTab === 'bank'
                  ? 'bg-white text-agro-700 shadow-sm border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              2. Bank Ko'chirmasi (CSV / TXT)
            </button>
            <button
              onClick={() => setActiveTab('kadastr')}
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition ${
                activeTab === 'kadastr'
                  ? 'bg-white text-agro-700 shadow-sm border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              3. Kadastr / Yer Maydoni
            </button>
          </div>

          <div className="p-8">
            <div className="border-2 border-dashed border-slate-300 hover:border-agro-500 rounded-2xl p-10 text-center bg-slate-50/50 transition">
              <UploadCloud className="w-12 h-12 text-agro-600 mx-auto mb-3" />
              <h3 className="text-base font-bold text-slate-900">
                Soliq.uz E-Faktura reestrini shu yerga tashlang yoki tanlang
              </h3>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                .XLSX, .CSV yoki .XML formatdagi hisobvaraq-fakturalar to'plami. Maksimal hajm: 25 MB.
              </p>
              <div className="mt-4 flex items-center justify-center gap-3">
                <button className="px-4 py-2 bg-agro-600 hover:bg-agro-700 text-white rounded-lg text-xs font-semibold shadow-sm transition">
                  Faylni Tanlash
                </button>
                <button 
                  onClick={() => setMockUploaded(true)}
                  className="px-4 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold transition"
                >
                  Namunaviy E-Faktura Yuklash
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Smart MXIK Parser Preview Table */}
        {mockUploaded && (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
              <div>
                <div className="flex items-center space-x-2">
                  <FileCheck className="w-5 h-5 text-emerald-600" />
                  <h3 className="font-bold text-slate-900">E-Faktura Tahlil Natijasi (Smart MXIK Parser)</h3>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  Aniqlangan tranzaksiyalar va ularning agronomik xarajatlar/daromadlar toifasiga birikishi
                </p>
              </div>

              <Link
                href="/dashboard"
                className="px-4 py-2 bg-agro-600 hover:bg-agro-700 text-white rounded-xl text-xs font-semibold shadow-sm inline-flex items-center"
              >
                <span>Moliya Dashboardiga O'tish</span>
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                    <th className="py-3 px-4">Sana</th>
                    <th className="py-3 px-4">Yo'nalish</th>
                    <th className="py-3 px-4">Hujjat / SF</th>
                    <th className="py-3 px-4">Kontragent</th>
                    <th className="py-3 px-4">MXIK (IKPU)</th>
                    <th className="py-3 px-4">Agro Toifa</th>
                    <th className="py-3 px-4 text-right">Summa</th>
                    <th className="py-3 px-4 text-center">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {sampleParsedTransactions.map((tx, idx) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      <td className="py-3 px-4 font-mono">{tx.date}</td>
                      <td className="py-3 px-4 font-semibold">
                        {tx.direction === 'INFLOW' ? (
                          <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">Kirim (+)</span>
                        ) : (
                          <span className="text-rose-700 bg-rose-50 px-2 py-0.5 rounded">Chiqim (-)</span>
                        )}
                      </td>
                      <td className="py-3 px-4 font-mono">{tx.doc}</td>
                      <td className="py-3 px-4 font-medium text-slate-900">{tx.counterparty}</td>
                      <td className="py-3 px-4 font-mono text-slate-500">{tx.mxik}</td>
                      <td className="py-3 px-4">{tx.category}</td>
                      <td className="py-3 px-4 text-right font-mono font-bold text-slate-900">{tx.amount}</td>
                      <td className="py-3 px-4 text-center">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                          {tx.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
