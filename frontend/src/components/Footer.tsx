import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 py-12 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-3">
              <span className="text-xl font-bold text-white">AgroHisob</span>
              <span className="text-xl font-semibold text-agro-400">CFO</span>
            </div>
            <p className="text-sm text-slate-400 max-w-md mb-4 leading-relaxed">
              O'zbekiston agro-klasterlari, meva-sabzavot eksportyorlari va tijoriy fermer xo'jaliklari uchun 
              Soliq E-faktura va bank aylanmalarini avtomatik tahlil qilib, 12 oylik mavsumiy Cash-Flow, 
              DSCR kredit riski va VMQ-613 bo'yicha yer ijarasi garov bahosini tayyorlab beruvchi B2B FinTech tizimi.
            </p>
            <div className="text-xs text-slate-500">
              AgroVentures 2026 Korporativ Akseleratori (#1 Mutlaq G'olib G'oya) loyihasi asosida yaratilgan.
            </div>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white tracking-wider uppercase mb-3">Mahsulot Bo'limlari</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/demo" className="hover:text-white transition">Sintetik Demo Ssenariylar</Link></li>
              <li><Link href="/dashboard" className="hover:text-white transition">Moliya & Kassa Paneli</Link></li>
              <li><Link href="/data-import" className="hover:text-white transition">Soliq E-Faktura & Bank Yuklash</Link></li>
              <li><Link href="/scenario-analysis" className="hover:text-white transition">Hosil & Narx Stress-Testi</Link></li>
              <li><Link href="/credit-report" className="hover:text-white transition">Kreditga Tayyorgarlik Dosyesi</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white tracking-wider uppercase mb-3">Normativ & Metodologiya</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li>VMQ-613 (Yer ijarasi garov tartibi)</li>
              <li>PQ-47 (Suv tejovchi texnologiyalar)</li>
              <li>PF-103 (Klasterlarni moliyaviy sog'lomlashtirish)</li>
              <li>CBU (Markaziy Bank 14% stavka)</li>
              <li>Agrobank Pre-Underwriting Funnel</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-6 flex flex-col md:flex-row justify-between items-center text-xs text-slate-500">
          <p>© 2026 AgroHisob CFO. Barcha huquqlar himoyalangan. Barcha namoyish ma'lumotlari sintetik va gipotetik xarakterga ega.</p>
          <p className="mt-2 md:mt-0">Assignment 1 — Product Foundation & Architecture MVP</p>
        </div>
      </div>
    </footer>
  );
}
