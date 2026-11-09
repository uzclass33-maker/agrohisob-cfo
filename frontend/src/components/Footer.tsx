import Link from 'next/link';
import { Sprout, ShieldCheck } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-navy-800 bg-navy-950 text-slate-400">
      <div className="container-x py-14">
        <div className="grid grid-cols-1 gap-10 md:grid-cols-12">
          {/* Brand */}
          <div className="md:col-span-6 lg:col-span-5">
            <div className="flex items-center gap-2.5">
              <span className="flex h-9 w-9 items-center justify-center rounded-[10px] bg-agro-600 text-white">
                <Sprout className="h-5 w-5" />
              </span>
              <span className="flex items-baseline gap-1 text-lg font-bold tracking-tight text-white">
                AgroHisob
                <span className="text-agro-400">CFO</span>
              </span>
            </div>
            <p className="mt-4 max-w-md text-sm leading-relaxed text-slate-400">
              O'zbekiston agro-klasterlari, meva-sabzavot eksportyorlari va tijoriy fermer xo'jaliklari uchun
              Soliq E-faktura va bank aylanmalarini avtomatik tahlil qilib, 12 oylik mavsumiy Cash-Flow,
              DSCR kredit riski va VMQ-613 bo'yicha yer ijarasi garov bahosini tayyorlab beruvchi B2B FinTech tizimi.
            </p>
            <div className="mt-5 inline-flex items-center gap-2 rounded-lg border border-navy-700 bg-navy-900/60 px-3 py-2 text-xs text-slate-300">
              <ShieldCheck className="h-4 w-4 text-agro-400" />
              <span>Barcha namoyish ma'lumotlari sintetik va gipotetik xarakterga ega.</span>
            </div>
          </div>

          {/* Product sections */}
          <div className="md:col-span-3 lg:col-span-3">
            <h4 className="text-xs font-bold uppercase tracking-[0.16em] text-slate-200">
              Mahsulot Bo'limlari
            </h4>
            <ul className="mt-4 space-y-2.5 text-sm">
              <li><Link href="/demo" className="transition-colors hover:text-white">Sintetik Demo Ssenariylar</Link></li>
              <li><Link href="/dashboard" className="transition-colors hover:text-white">Moliya & Kassa Paneli</Link></li>
              <li><Link href="/data-import" className="transition-colors hover:text-white">Soliq E-Faktura & Bank Yuklash</Link></li>
              <li><Link href="/scenario-analysis" className="transition-colors hover:text-white">Hosil & Narx Stress-Testi</Link></li>
              <li><Link href="/credit-report" className="transition-colors hover:text-white">Kreditga Tayyorgarlik Dosyesi</Link></li>
              <li><Link href="/collateral-subsidies" className="transition-colors hover:text-white">Garov Baholash & Subsidiyalar</Link></li>
            </ul>
          </div>

          {/* Regulatory & methodology */}
          <div className="md:col-span-3 lg:col-span-4">
            <h4 className="text-xs font-bold uppercase tracking-[0.16em] text-slate-200">
              Normativ & Metodologiya
            </h4>
            <ul className="mt-4 space-y-2.5 text-sm text-slate-400">
              <li className="flex gap-2">
                <span className="mt-[7px] h-1 w-1 shrink-0 rounded-full bg-agro-500" />
                VMQ-613 (Yer ijarasi garov tartibi)
              </li>
              <li className="flex gap-2">
                <span className="mt-[7px] h-1 w-1 shrink-0 rounded-full bg-agro-500" />
                PQ-47 (Suv tejovchi texnologiyalar)
              </li>
              <li className="flex gap-2">
                <span className="mt-[7px] h-1 w-1 shrink-0 rounded-full bg-agro-500" />
                PF-103 (Klasterlarni moliyaviy sog'lomlashtirish)
              </li>
              <li className="flex gap-2">
                <span className="mt-[7px] h-1 w-1 shrink-0 rounded-full bg-agro-500" />
                CBU (Markaziy Bank 14% stavka)
              </li>
              <li className="flex gap-2">
                <span className="mt-[7px] h-1 w-1 shrink-0 rounded-full bg-agro-500" />
                Agrobank Pre-Underwriting Funnel
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-3 border-t border-navy-800 pt-6 text-xs text-slate-500 md:flex-row md:items-center md:justify-between">
          <p>© 2026 AgroHisob CFO. Barcha huquqlar himoyalangan.</p>
          <p>AgroHisob CFO — Professional FinTech Platformasi</p>
        </div>
      </div>
    </footer>
  );
}
