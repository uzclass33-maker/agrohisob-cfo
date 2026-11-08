'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Sprout, LayoutDashboard, FileSpreadsheet, Sliders, ShieldCheck, Database } from 'lucide-react';

const NAV_ITEMS = [
  { href: '/', label: 'Asosiy', icon: Sprout },
  { href: '/demo', label: 'Demo Ssenariylar', icon: Database },
  { href: '/dashboard', label: 'Moliya Paneli', icon: LayoutDashboard },
  { href: '/data-import', label: 'Faktura & Data Yuklash', icon: FileSpreadsheet },
  { href: '/scenario-analysis', label: 'Ssenariy & Stress-Test', icon: Sliders },
  { href: '/credit-report', label: 'Kreditga Tayyorgarlik', icon: ShieldCheck },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
      {/* Uzbekistan Agri-FinTech Banner */}
      <div className="bg-agro-900 text-white text-xs py-1 px-4 font-medium flex justify-between items-center">
        <span>AGROVENTURES 2026 STARTAP SELEKSIYASI | B2B AGRI-FINTECH SaaS</span>
        <span className="hidden md:inline bg-agro-700 px-2 py-0.5 rounded text-[11px]">
          O'zbekiston agrar sektori uchun AI-CFO platformasi
        </span>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-agro-600 flex items-center justify-center text-white shadow-md">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-bold text-slate-900 tracking-tight">AgroHisob</span>
              <span className="text-xl font-semibold text-agro-600 ml-1">CFO</span>
              <span className="block text-[10px] text-slate-500 uppercase tracking-widest font-semibold">AgriFinTech B2B</span>
            </div>
          </Link>

          <nav className="hidden lg:flex space-x-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-agro-50 text-agro-700 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-agro-600' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center space-x-3">
            <Link
              href="/demo"
              className="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-agro-600 hover:bg-agro-700 shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-agro-500"
            >
              Demo Sinov
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
