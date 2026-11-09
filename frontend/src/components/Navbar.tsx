'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import {
  Sprout,
  LayoutDashboard,
  FileSpreadsheet,
  Sliders,
  ShieldCheck,
  Database,
  Landmark,
  Users,
  Menu,
  X,
  ArrowRight,
} from 'lucide-react';

const NAV_ITEMS = [
  { href: '/', label: 'Asosiy', icon: Sprout },
  { href: '/demo', label: 'Demo Ssenariylar', icon: Database },
  { href: '/dashboard', label: 'Moliya Paneli', icon: LayoutDashboard },
  { href: '/data-import', label: 'Data Yuklash', icon: FileSpreadsheet },
  { href: '/scenario-analysis', label: 'Stress-Test', icon: Sliders },
  { href: '/credit-report', label: 'Kredit Dosyesi', icon: ShieldCheck },
  { href: '/collateral-subsidies', label: 'Garov & Subsidiyalar', icon: Landmark },
  { href: '/pilot-dashboard', label: 'Pilot & Tadqiqot', icon: Users },
];

export default function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  // Close the mobile panel whenever navigation happens
  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  // Lock body scroll while the mobile panel is open
  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [open]);

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/70 bg-white/90 backdrop-blur-md">
      <div className="container-x">
        <div className="flex h-16 items-center justify-between gap-4">
          {/* Brand */}
          <Link href="/" className="group flex shrink-0 items-center gap-2.5" aria-label="AgroHisob CFO — asosiy sahifa">
            <span className="flex h-9 w-9 items-center justify-center rounded-[10px] bg-agro-700 text-white shadow-sm transition-colors duration-300 group-hover:bg-agro-800">
              <Sprout className="h-5 w-5" />
            </span>
            <span className="leading-none">
              <span className="flex items-baseline gap-1 text-[17px] font-bold tracking-tight text-navy-900">
                AgroHisob
                <span className="text-agro-700">CFO</span>
              </span>
              <span className="mt-1 block text-[9px] font-semibold uppercase tracking-[0.2em] text-slate-400">
                AgriFinTech Platformasi
              </span>
            </span>
          </Link>

          {/* Desktop navigation */}
          <nav className="hidden items-center gap-0.5 xl:flex" aria-label="Asosiy menyu">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`relative flex items-center gap-1.5 rounded-lg px-3 py-2 text-[13px] font-medium transition-colors duration-200 ${
                    isActive
                      ? 'bg-agro-50 text-agro-800'
                      : 'text-slate-600 hover:bg-slate-100/80 hover:text-navy-900'
                  }`}
                >
                  <Icon className={`h-4 w-4 ${isActive ? 'text-agro-700' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <Link
              href="/login"
              className="hidden items-center justify-center rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-sm font-medium text-slate-700 shadow-sm transition-all duration-200 hover:border-slate-400 hover:text-navy-900 md:inline-flex"
            >
              Kirish
            </Link>
            <Link
              href="/demo"
              className="hidden items-center justify-center gap-1.5 rounded-lg bg-agro-700 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all duration-200 hover:bg-agro-800 hover:shadow-md active:translate-y-px sm:inline-flex"
            >
              Demo Sinov
              <ArrowRight className="h-4 w-4" />
            </Link>
            <button
              type="button"
              onClick={() => setOpen((v) => !v)}
              aria-expanded={open}
              aria-controls="mobile-nav"
              aria-label={open ? 'Menyuni yopish' : 'Menyuni ochish'}
              className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-700 shadow-sm transition-colors hover:bg-slate-50 xl:hidden"
            >
              {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile navigation panel */}
      {open && (
        <div
          id="mobile-nav"
          className="border-t border-slate-200/70 bg-white xl:hidden"
        >
          <div className="container-x max-h-[calc(100vh-4rem)] overflow-y-auto py-4">
            <nav className="grid grid-cols-1 gap-1" aria-label="Mobil menyu">
              {NAV_ITEMS.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 rounded-lg px-3 py-3 text-[15px] font-medium transition-colors ${
                      isActive
                        ? 'bg-agro-50 text-agro-800'
                        : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <span
                      className={`flex h-9 w-9 items-center justify-center rounded-lg border ${
                        isActive
                          ? 'border-agro-200 bg-white text-agro-700'
                          : 'border-slate-200 bg-slate-50 text-slate-500'
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                    </span>
                    {item.label}
                  </Link>
                );
              })}
            </nav>

            <div className="mt-4 grid grid-cols-2 gap-2 border-t border-slate-100 pt-4">
              <Link
                href="/login"
                className="flex items-center justify-center rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50"
              >
                Kirish
              </Link>
              <Link
                href="/demo"
                className="flex items-center justify-center gap-1.5 rounded-lg bg-agro-700 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-agro-800"
              >
                Demo Sinov
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
