import Link from 'next/link';
import { 
  Sprout, TrendingUp, ShieldCheck, ArrowRight, BarChart3, 
  FileText, CheckCircle2, AlertTriangle, Layers, DollarSign 
} from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="bg-slate-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28 bg-gradient-to-b from-white to-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-agro-50 border border-agro-200 text-agro-800 text-xs font-semibold mb-6">
              <span className="w-2 h-2 rounded-full bg-agro-600 animate-pulse"></span>
              <span>AgroVentures 2026 Seleksiyasi: Mutlaq G'olib G'oya (91.5 Ball)</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
              O'zbekiston agrobiznesi uchun{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-agro-600 to-emerald-700">
                AI-CFO va Kredit Dosyesi
              </span>
            </h1>

            <p className="mt-6 text-lg sm:text-xl text-slate-600 leading-relaxed">
              Soliq E-faktura va bank aylanmalarini <span className="font-semibold text-slate-900">3 daqiqada</span> 12 oylik mavsumiy pul oqimi prognozi, DSCR kredit riski, VMQ-613 yer ijarasi garov bahosi va tayyor bank kredit dosyesiga aylantiring.
            </p>

            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/demo"
                className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 border border-transparent rounded-xl text-base font-semibold text-white bg-agro-600 hover:bg-agro-700 shadow-md hover:shadow-lg transition-all"
              >
                <span>Demo Ssenariyni Sinab Ko'rish</span>
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
              <Link
                href="/dashboard"
                className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 border border-slate-300 rounded-xl text-base font-semibold text-slate-700 bg-white hover:bg-slate-50 shadow-sm transition-all"
              >
                <BarChart3 className="w-5 h-5 mr-2 text-slate-500" />
                <span>Jonli Moliya Paneliga O'tish</span>
              </Link>
            </div>
          </div>

          {/* Uzbekistan Agri Market Realities / Statistics Bar */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm text-center">
              <div className="text-2xl font-black text-slate-900">91 775+</div>
              <div className="text-xs text-slate-500 mt-1">Fermer xo'jaligi va 633 klaster</div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm text-center">
              <div className="text-2xl font-black text-agro-600">56.2 trln so'm</div>
              <div className="text-xs text-slate-500 mt-1">Agrobank 2026 kredit rejasi</div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm text-center">
              <div className="text-2xl font-black text-rose-600">19 ta klaster</div>
              <div className="text-xs text-slate-500 mt-1">Kassa uzilishi sababli bankrotlik</div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm text-center">
              <div className="text-2xl font-black text-sky-600">VMQ-613</div>
              <div className="text-xs text-slate-500 mt-1">Yer ijara huquqini garovga qo'yish</div>
            </div>
          </div>
        </div>
      </section>

      {/* Core Problem & Value Proposition */}
      <section className="py-16 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl font-bold text-slate-900">
              Agrobiznes Nima Uchun Kassa Uzilishiga Duch Keladi?
            </h2>
            <p className="mt-3 text-slate-600 text-sm sm:text-base">
              O'zbekistonda buxgalteriya faqat o'tgan davr solig'i uchun yuritiladi. Kelgusi mavsum xarajatlari bilan pul tushumi o'rtasida uzilish yuzaga keladi.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200">
              <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center text-amber-700 mb-4">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Mavsumiy Kassa Uzilishi (Cash-Flow Gap)</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Bahorgi ekishda urug', yoqilg'i va o'g'it uchun xarajatlar cho'qqiga chiqadi, daromad esa 5-6 oydan keyin keladi. Natijada ish haqi va kredit to'lovlari uziladi.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200">
              <div className="w-12 h-12 rounded-xl bg-sky-100 flex items-center justify-center text-sky-700 mb-4">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Garov Yetishmovchiligi va VMQ-613</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Agrobank kreditlarining 57% garovi shahar ko'chmas mulkiga bog'langan. VMQ-613 asosida qishloq yer ijara huquqini avtomatik DCF baholash tizimi yo'q edi.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-700 mb-4">
                <FileText className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Kredit Dosyesi Tayyorlashdagi Qiyinchilik</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Fermer yoki agro-KOB bankdan kredit olish uchun tashqi konsaltingga $500–$3 000 to'laydi va 3-6 hafta vaqt yo'qotadi. AgroHisob buni 3 daqiqada bajaradi.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Product Architecture & Capabilities */}
      <section className="py-16 bg-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-wider text-agro-600">MVP Arxitekturasi</span>
            <h2 className="text-3xl font-bold text-slate-900 mt-1">
              AgroHisob CFO Imkoniyatlari
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Link href="/demo" className="block p-6 rounded-xl bg-white border border-slate-200 hover:border-agro-500 hover:shadow-md transition">
              <Layers className="w-8 h-8 text-agro-600 mb-3" />
              <h4 className="font-bold text-slate-900 mb-1">3 ta Real Ssenariy</h4>
              <p className="text-xs text-slate-500">Kichik fermer (65 ga), Eksportyor (120 ga) va Klaster (2500 ga) sintetik modellari.</p>
            </Link>

            <Link href="/dashboard" className="block p-6 rounded-xl bg-white border border-slate-200 hover:border-agro-500 hover:shadow-md transition">
              <TrendingUp className="w-8 h-8 text-emerald-600 mb-3" />
              <h4 className="font-bold text-slate-900 mb-1">12 Oylik Kassa Oqimi</h4>
              <p className="text-xs text-slate-500">Deterministik arifmetika: Yakuniy qoldiq = Boshlang'ich + Tushum - Xarajat.</p>
            </Link>

            <Link href="/scenario-analysis" className="block p-6 rounded-xl bg-white border border-slate-200 hover:border-agro-500 hover:shadow-md transition">
              <BarChart3 className="w-8 h-8 text-sky-600 mb-3" />
              <h4 className="font-bold text-slate-900 mb-1">Hosil & Narx Stress-Test</h4>
              <p className="text-xs text-slate-500">Hosil va narx ±20% o'zgarganda DSCR va kassa defitsitini qayta hisoblash.</p>
            </Link>

            <Link href="/credit-report" className="block p-6 rounded-xl bg-white border border-slate-200 hover:border-agro-500 hover:shadow-md transition">
              <ShieldCheck className="w-8 h-8 text-indigo-600 mb-3" />
              <h4 className="font-bold text-slate-900 mb-1">Kreditga Tayyorgarlik</h4>
              <p className="text-xs text-slate-500">Agrobank anderrayting talablariga mos DSCR, qarz sig'imi va VMQ-613 garov bahosi.</p>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Box */}
      <section className="py-12 bg-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-r from-agro-900 to-emerald-900 text-white rounded-2xl p-8 sm:p-12 shadow-xl flex flex-col md:flex-row items-center justify-between gap-6">
            <div>
              <h3 className="text-2xl font-bold">Assignment 1 To'liq Vertikal Slayz Tayyor</h3>
              <p className="text-slate-300 text-sm mt-2 max-w-xl">
                Sintetik fermer xo'jaligi ma'lumotlarini yuklang, real Python/FastAPI moliyaviy yadrosida hisoblang va interaktiv grafikda kassa uzilishini ko'ring.
              </p>
            </div>
            <Link
              href="/demo"
              className="inline-flex items-center px-6 py-3 rounded-xl bg-agro-500 hover:bg-agro-400 text-white font-bold text-sm shadow-md transition whitespace-nowrap"
            >
              Demo Tanlagichga O'tish
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
