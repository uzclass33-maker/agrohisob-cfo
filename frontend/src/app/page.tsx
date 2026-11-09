import Link from 'next/link';
import {
  ArrowRight,
  AlertTriangle,
  ShieldCheck,
  FileText,
  FileSpreadsheet,
  CalendarClock,
  Gauge,
  FileCheck2,
  Wheat,
  Truck,
  Building2,
  BarChart3,
  TrendingUp,
  Layers,
  BrainCircuit,
  Landmark,
  ShieldAlert,
  DollarSign,
  Sliders,
  Sparkles,
  CheckCircle2,
  Activity,
} from 'lucide-react';
import Reveal from '@/components/Reveal';

const MARKET_STATS = [
  { value: '91 775+', label: "Fermer xo'jaligi va 633 klaster", accent: 'text-navy-900' },
  { value: '56,2 trln so\'m', label: 'Agrobank 2026 kredit rejasi', accent: 'text-agro-700' },
  { value: '19 ta klaster', label: 'Kassa uzilishi sababli bankrotlik', accent: 'text-rose-600' },
  { value: 'VMQ-613', label: "Yer ijara huquqini garovga qo'yish", accent: 'text-harvest-600' },
];

const CORE_CAPABILITIES = [
  {
    href: '/dashboard?tab=cashflow',
    icon: TrendingUp,
    badge: 'Kassa Tahlili',
    title: '12 Oylik Kassa Oqimi',
    text: "Deterministik oylik pul kirimi, chiqimi, operatsion kassa oqimi va yakuniy kassa balansi tahlili.",
    color: 'text-agro-700 bg-agro-50 border-agro-200',
  },
  {
    href: '/dashboard?tab=forecast',
    icon: CalendarClock,
    badge: 'Prognozlash',
    title: 'Mavsumiy Pul Oqimi Prognozi',
    text: "Bahorgi ekish va kuzgi yig'im davrida kassa uzilishi (defitsit oylar) va eng past likvidlik nuqtasini aniqlash.",
    color: 'text-sky-700 bg-sky-50 border-sky-200',
  },
  {
    href: '/dashboard?tab=debt',
    icon: Gauge,
    badge: 'Anderrayting',
    title: 'DSCR & Qarz Qoplami',
    text: "Yillik CFADS va kredit to'lovlari mutanosibligi, bank talablariga muvofiqlik darajasi monitoringi.",
    color: 'text-indigo-700 bg-indigo-50 border-indigo-200',
  },
  {
    href: '/dashboard?tab=risks',
    icon: ShieldAlert,
    badge: 'Monitoring',
    title: 'Moliyaviy Xavflar Monitori',
    text: "Likvidlik taqchilligi, minimal bufer xatari va daromad mavsumiy konsentratsiyasi bo'yicha erta ogohlantirish.",
    color: 'text-rose-700 bg-rose-50 border-rose-200',
  },
  {
    href: '/scenario-analysis',
    icon: Sliders,
    badge: 'Simulyatsiya',
    title: 'Hosil & Narx Stress-Testi',
    text: "Hosil va narx ±20% o'zgarganda kassa holati, kassa teshigi va DSCR barqarorligini backend simulyatsiyasi.",
    color: 'text-amber-700 bg-amber-50 border-amber-200',
  },
  {
    href: '/dashboard?tab=ai_cfo',
    icon: BrainCircuit,
    badge: 'Tahliliy Aql',
    title: 'AI-CFO Moliyaviy Xulosalari',
    text: "Deterministik moliya qoidalari va maxfiylikni ta'minlovchi tushunarli tahliliy tavsiyalar.",
    color: 'text-purple-700 bg-purple-50 border-purple-200',
  },
  {
    href: '/credit-report',
    icon: ShieldCheck,
    badge: 'Bank Hujjati',
    title: 'Bank Kredit Dosyesi (PDF & Excel)',
    text: "Agrobank anderrayting talablariga 100% mos 8-sahifali rasmiy kredit paketi va formulali moliyaviy model.",
    color: 'text-emerald-700 bg-emerald-50 border-emerald-200',
  },
  {
    href: '/collateral-subsidies',
    icon: Landmark,
    badge: 'VMQ-613',
    title: 'Yer Ijarasi Garov Bahosi',
    text: "Yer ijara huquqini bonitet bali, maydon va qolgan ijara muddati asosida DCF usulida garovga baholash.",
    color: 'text-harvest-700 bg-harvest-50 border-harvest-200',
  },
  {
    href: '/collateral-subsidies',
    icon: DollarSign,
    badge: 'PQ-47 / PF-82',
    title: 'Davlat Subsidiyalari',
    text: "Tomchilatib sug'orish va imtiyozli agrokredit foiz stavkasini davlat tomonidan kompensatsiya qilish hisobi.",
    color: 'text-teal-700 bg-teal-50 border-teal-200',
  },
  {
    href: '/data-import',
    icon: FileSpreadsheet,
    badge: 'Smart Import',
    title: 'Soliq E-Faktura & Bank Importi',
    text: "Soliq Didox E-fakturalari (XML/Excel) va bank ko'chirmalarini (1C/txt) 3 daqiqada yuklash va solishtirish.",
    color: 'text-blue-700 bg-blue-50 border-blue-200',
  },
];

const PROCESS_STEPS = [
  {
    icon: FileSpreadsheet,
    title: "Ma'lumot yuklash",
    text: "Soliq E-faktura va bank ko'chirmalari tizimga yuklanadi va avtomatik tasniflanadi.",
  },
  {
    icon: CalendarClock,
    title: '12 oylik prognoz',
    text: "Mavsumiy pul oqimi aniqlanadi: kassa uzilish oylari va eng past qoldiq nuqtasi topiladi.",
  },
  {
    icon: Gauge,
    title: 'DSCR va stress-test',
    text: "Kredit to'lash qobiliyati hisoblanadi, hosil va narx shoklari ostida sinovdan o'tkaziladi.",
  },
  {
    icon: FileCheck2,
    title: 'Tayyor kredit dosyesi',
    text: 'Bank anderrayting talablariga mos paket — hisob-kitoblar, grafiklar va garov bahosi bilan.',
  },
];

const FEATURES = [
  {
    href: '/demo',
    icon: Layers,
    title: '3 ta Real Ssenariy',
    text: 'Kichik fermer (65 ga), Eksportyor (120 ga) va Klaster (2500 ga) sintetik modellari.',
  },
  {
    href: '/dashboard',
    icon: TrendingUp,
    title: '12 Oylik Kassa Oqimi',
    text: "Deterministik arifmetika: Yakuniy qoldiq = Boshlang'ich + Tushum - Xarajat.",
  },
  {
    href: '/scenario-analysis',
    icon: BarChart3,
    title: 'Hosil & Narx Stress-Test',
    text: 'Hosil va narx ±20% o\'zgarganda DSCR va kassa defitsitini qayta hisoblash.',
  },
  {
    href: '/credit-report',
    icon: ShieldCheck,
    title: 'Kreditga Tayyorgarlik',
    text: "Agrobank anderrayting talablariga mos DSCR, qarz sig'imi va VMQ-613 garov bahosi.",
  },
];

const SEGMENTS = [
  {
    href: '/dashboard?scenario=scenario-small-farmer',
    icon: Wheat,
    title: 'Tijoriy Fermer',
    meta: '65 gektar',
    text: 'Kichik fermer xo\'jaliklari uchun mavsumiy kassa uzilishini oldindan aniqlash va kredit paketini tayyorlash.',
  },
  {
    href: '/dashboard?scenario=scenario-exporter',
    icon: Truck,
    title: 'Meva-Sabzavot Eksportyori',
    meta: '120 gektar',
    text: 'Eksport kontraktlari va hosil tsikli asosida aylanma mablag\'larni rejalashtirish va DSCR kuzatuvi.',
  },
  {
    href: '/dashboard?scenario=scenario-cluster',
    icon: Building2,
    title: 'Agro-Klaster',
    meta: '2 500 gektar',
    text: 'Paxta-g\'alla klasterlari uchun katta hajmdagi pul oqimlarini boshqarish va bank kredit dosyesini shakllantirish.',
  },
];

export default function LandingPage() {
  return (
    <div className="bg-canvas">
      {/* ============================== HERO ============================== */}
      <section className="relative overflow-hidden border-b border-slate-200/70">
        {/* Quiet ledger-grid backdrop */}
        <div className="bg-grid mask-fade-b pointer-events-none absolute inset-0" aria-hidden="true" />
        <div
          className="pointer-events-none absolute -top-32 right-[-160px] h-[480px] w-[480px] rounded-full bg-agro-100/60 blur-3xl"
          aria-hidden="true"
        />

        <div className="container-x relative">
          <div className="grid grid-cols-1 items-center gap-12 pb-16 pt-14 lg:grid-cols-12 lg:gap-8 lg:pb-24 lg:pt-20">
            {/* Left — message */}
            <div className="hero-stagger lg:col-span-6">
              <div className="eyebrow text-agro-700">
                <span className="h-2 w-2 rounded-full bg-agro-600" />
                B2B AgriFinTech Platformasi
              </div>

              <h1 className="mt-5 max-w-xl text-4xl font-bold leading-[1.08] tracking-tight text-navy-950 sm:text-5xl lg:text-[56px]">
                O'zbekiston agrobiznesi uchun{' '}
                <span className="text-agro-700">AI-CFO</span> va{' '}
                <span className="text-agro-700">kredit dosyesi</span>
              </h1>

              <p className="mt-6 max-w-xl text-lg leading-relaxed text-slate-600">
                Soliq E-faktura va bank aylanmalarini <strong className="font-semibold text-navy-900">3 daqiqada</strong>{' '}
                12 oylik mavsumiy pul oqimi prognozi, DSCR kredit riski, VMQ-613 yer ijarasi garov bahosi va
                tayyor bank kredit dosyesiga aylantiring.
              </p>

              <div className="mt-9 flex flex-col gap-3 sm:flex-row">
                <Link href="/demo" className="btn-primary px-6 py-3.5 text-base">
                  Demo ssenariyni sinab ko'rish
                  <ArrowRight className="h-5 w-5" />
                </Link>
                <Link href="/dashboard" className="btn-secondary px-6 py-3.5 text-base">
                  <BarChart3 className="h-5 w-5 text-slate-500" />
                  Moliya paneli
                </Link>
              </div>

              {/* Instant 3-Company Demo Explorer Strip */}
              <div className="mt-8 rounded-2xl border border-agro-200/90 bg-white/90 p-4 shadow-sm backdrop-blur-sm">
                <div className="flex items-center justify-between gap-2 mb-2.5">
                  <span className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-navy-950">
                    <Sparkles className="h-4 w-4 text-agro-700" />
                    Ro'yxatdan o'tmasdan 3 ta demo korxonani ko'ring:
                  </span>
                  <span className="text-[10px] font-semibold text-agro-700 bg-agro-50 border border-agro-200 px-2 py-0.5 rounded-full">
                    Ochiq sinov
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <Link
                    href="/dashboard?scenario=scenario-small-farmer"
                    className="p-2.5 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-agro-50/60 hover:border-agro-400 transition group text-left"
                  >
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-1.5 text-xs font-bold text-navy-900 group-hover:text-agro-800">
                        <Wheat className="w-3.5 h-3.5 text-harvest-600" />
                        Andijon Baraka
                      </span>
                      <span className="text-[10px] font-semibold text-slate-500">65 ga</span>
                    </div>
                    <span className="block text-[11px] text-slate-500 mt-1 line-clamp-1">Kichik fermer (May kassa uzilishi)</span>
                  </Link>
                  <Link
                    href="/dashboard?scenario=scenario-exporter"
                    className="p-2.5 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-agro-50/60 hover:border-agro-400 transition group text-left"
                  >
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-1.5 text-xs font-bold text-navy-900 group-hover:text-agro-800">
                        <Truck className="w-3.5 h-3.5 text-sky-600" />
                        Samarqand Eksport
                      </span>
                      <span className="text-[10px] font-semibold text-slate-500">120 ga</span>
                    </div>
                    <span className="block text-[11px] text-slate-500 mt-1 line-clamp-1">Meva eksportyori (DSCR 1.82x)</span>
                  </Link>
                  <Link
                    href="/dashboard?scenario=scenario-cluster"
                    className="p-2.5 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-agro-50/60 hover:border-agro-400 transition group text-left"
                  >
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-1.5 text-xs font-bold text-navy-900 group-hover:text-agro-800">
                        <Building2 className="w-3.5 h-3.5 text-agro-700" />
                        Qashqadaryo Klaster
                      </span>
                      <span className="text-[10px] font-semibold text-slate-500">2 500 ga</span>
                    </div>
                    <span className="block text-[11px] text-slate-500 mt-1 line-clamp-1">Yirik klaster (19.8 mlrd qarz)</span>
                  </Link>
                </div>
              </div>

              {/* Trust stats */}
              <dl className="mt-12 grid grid-cols-2 gap-x-6 gap-y-7 border-t border-slate-200/80 pt-7 sm:grid-cols-4">
                {MARKET_STATS.map((s) => (
                  <div key={s.label}>
                    <dt className="sr-only">{s.label}</dt>
                    <dd className={`num text-xl font-bold tracking-tight sm:text-[22px] ${s.accent}`}>{s.value}</dd>
                    <dd className="mt-1.5 text-xs leading-snug text-slate-500">{s.label}</dd>
                  </div>
                ))}
              </dl>
            </div>

            {/* Right — how it works panel */}
            <div className="hero-stagger lg:col-span-6">
              <div className="card overflow-hidden p-6 sm:p-8 lg:ml-6">
                <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                  <span className="eyebrow text-slate-500">Ish jarayoni</span>
                  <Link
                    href="/demo"
                    className="inline-flex items-center gap-1 text-xs font-semibold text-agro-700 transition-colors hover:text-agro-800"
                  >
                    Demo ochish
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </div>

                <ol className="mt-5 space-y-0">
                  {PROCESS_STEPS.map((step, i) => {
                    const Icon = step.icon;
                    return (
                      <li key={step.title} className="relative flex gap-4 pb-6 last:pb-0">
                        {/* connector line */}
                        {i < PROCESS_STEPS.length - 1 && (
                          <span
                            className="absolute left-[21px] top-11 h-[calc(100%-2.5rem)] w-px bg-slate-200"
                            aria-hidden="true"
                          />
                        )}
                        <span className="relative flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-agro-100 bg-agro-50 text-agro-700">
                          <Icon className="h-5 w-5" />
                        </span>
                        <div className="pt-0.5">
                          <div className="flex items-baseline gap-2">
                            <span className="num text-[11px] font-bold text-slate-400">
                              {String(i + 1).padStart(2, '0')}
                            </span>
                            <h3 className="text-[15px] font-semibold text-navy-900">{step.title}</h3>
                          </div>
                          <p className="mt-1 text-sm leading-relaxed text-slate-500">{step.text}</p>
                        </div>
                      </li>
                    );
                  })}
                </ol>

                <div className="mt-6 rounded-lg border border-slate-200/80 bg-slate-50/80 px-4 py-3 text-xs text-slate-500">
                  Barcha hisob-kitoblar deterministik moliyaviy dvigatelda bajariladi — klient tomonda
                  hisoblash yo'q.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================== CORE FEATURES & CAPABILITIES ============================== */}
      <section className="border-b border-slate-200/70 bg-gradient-to-b from-white to-slate-50/60 py-12 lg:py-16">
        <div className="container-x">
          <Reveal>
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
              <div>
                <div className="eyebrow text-agro-700">
                  <span className="h-2 w-2 rounded-full bg-agro-600" />
                  Platformaning Asosiy Imkoniyatlari
                </div>
                <h2 className="mt-2 text-2xl font-bold tracking-tight text-navy-950 sm:text-3xl">
                  Barcha Moliya va Kredit Modullari
                </h2>
                <p className="mt-2 text-sm text-slate-600 max-w-2xl">
                  Menyuni qidirmasdan, quyidagi 10 ta asosiy modulning istalganiga bitta bosish orqali to'g'ridan-to'g'ri o'ting:
                </p>
              </div>
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-1.5 text-xs font-bold text-agro-700 hover:text-agro-800 transition shrink-0"
              >
                Boshqaruv panelini ochish
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </Reveal>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
            {CORE_CAPABILITIES.map((cap, i) => {
              const Icon = cap.icon;
              return (
                <Reveal key={cap.title} delay={i * 40}>
                  <Link
                    href={cap.href}
                    className="group flex flex-col justify-between h-full p-4 rounded-xl border border-slate-200/90 bg-white shadow-sm hover:border-agro-400 hover:shadow-md transition-all duration-200"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <span className={`p-2 rounded-lg border ${cap.color}`}>
                          <Icon className="h-4 w-4" />
                        </span>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                          {cap.badge}
                        </span>
                      </div>
                      <h3 className="text-sm font-bold text-navy-900 group-hover:text-agro-700 transition-colors leading-snug">
                        {cap.title}
                      </h3>
                      <p className="mt-1.5 text-xs text-slate-500 leading-relaxed">
                        {cap.text}
                      </p>
                    </div>
                    <div className="mt-4 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-agro-700">
                      <span>Modulga o'tish</span>
                      <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </div>
                  </Link>
                </Reveal>
              );
            })}
          </div>
        </div>
      </section>

      {/* ============================== PROBLEM ============================== */}
      <section className="border-b border-slate-200/70 bg-white">
        <div className="container-x py-16 lg:py-24">
          <Reveal>
            <div className="mx-auto max-w-2xl text-center">
              <span className="eyebrow justify-center text-agro-700">Muammo</span>
              <h2 className="mt-4 text-3xl font-bold tracking-tight text-navy-950 sm:text-4xl">
                Agrobiznes nima uchun kassa uzilishiga duch keladi?
              </h2>
              <p className="mt-4 text-base leading-relaxed text-slate-600">
                O'zbekistonda buxgalteriya faqat o'tgan davr solig'i uchun yuritiladi. Kelgusi mavsum
                xarajatlari bilan pul tushumi o'rtasida uzilish yuzaga keladi.
              </p>
            </div>
          </Reveal>

          <div className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-3 lg:mt-16">
            {[
              {
                icon: AlertTriangle,
                tone: 'bg-harvest-50 text-harvest-600 border-harvest-100',
                title: 'Mavsumiy Kassa Uzilishi (Cash-Flow Gap)',
                text: "Bahorgi ekishda urug', yoqilg'i va o'g'it uchun xarajatlar cho'qqiga chiqadi, daromad esa 5-6 oydan keyin keladi. Natijada ish haqi va kredit to'lovlari uziladi.",
              },
              {
                icon: ShieldCheck,
                tone: 'bg-sky-50 text-sky-700 border-sky-100',
                title: 'Garov Yetishmovchiligi va VMQ-613',
                text: "Agrobank kreditlarining 57% garovi shahar ko'chmas mulkiga bog'langan. VMQ-613 asosida qishloq yer ijara huquqini avtomatik DCF baholash tizimi yo'q edi.",
              },
              {
                icon: FileText,
                tone: 'bg-agro-50 text-agro-700 border-agro-100',
                title: 'Kredit Dosyesi Tayyorlashdagi Qiyinchilik',
                text: "Fermer yoki agro-KOB bankdan kredit olish uchun tashqi konsaltingga $500–$3 000 to'laydi va 3-6 hafta vaqt yo'qotadi. AgroHisob buni 3 daqiqada bajaradi.",
              },
            ].map((card, i) => {
              const Icon = card.icon;
              return (
                <Reveal key={card.title} delay={i * 90}>
                  <div className="card card-hover h-full p-7">
                    <div className={`flex h-12 w-12 items-center justify-center rounded-xl border ${card.tone}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <h3 className="mt-5 text-lg font-semibold tracking-tight text-navy-950">{card.title}</h3>
                    <p className="mt-3 text-sm leading-relaxed text-slate-600">{card.text}</p>
                  </div>
                </Reveal>
              );
            })}
          </div>
        </div>
      </section>

      {/* ============================== PROCESS ============================== */}
      <section className="border-b border-slate-200/70">
        <div className="container-x py-16 lg:py-24">
          <Reveal>
            <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
              <div className="max-w-xl">
                <span className="eyebrow text-agro-700">Qanday ishlaydi</span>
                <h2 className="mt-4 text-3xl font-bold tracking-tight text-navy-950 sm:text-4xl">
                  Xom ma'lumotdan bank kredit dosyesigacha
                </h2>
              </div>
              <Link
                href="/demo"
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-agro-700 transition-colors hover:text-agro-800"
              >
                Amalda ko'rish
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </Reveal>

          <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:mt-16 lg:grid-cols-4">
            {PROCESS_STEPS.map((step, i) => {
              const Icon = step.icon;
              return (
                <Reveal key={step.title} delay={i * 90}>
                  <div className="relative h-full">
                    <div className="flex h-full flex-col rounded-xl border border-slate-200/80 bg-white p-6 shadow-card">
                      <div className="flex items-center justify-between">
                        <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-navy-900 text-white">
                          <Icon className="h-5 w-5" />
                        </span>
                        <span className="num text-2xl font-bold text-slate-200">
                          {String(i + 1).padStart(2, '0')}
                        </span>
                      </div>
                      <h3 className="mt-5 text-base font-semibold tracking-tight text-navy-950">{step.title}</h3>
                      <p className="mt-2 text-sm leading-relaxed text-slate-600">{step.text}</p>
                    </div>
                  </div>
                </Reveal>
              );
            })}
          </div>
        </div>
      </section>

      {/* ============================== FEATURES ============================== */}
      <section className="border-b border-slate-200/70 bg-white">
        <div className="container-x py-16 lg:py-24">
          <Reveal>
            <div className="mx-auto max-w-2xl text-center">
              <span className="eyebrow justify-center text-agro-700">Imkoniyatlar</span>
              <h2 className="mt-4 text-3xl font-bold tracking-tight text-navy-950 sm:text-4xl">
                AgroHisob CFO imkoniyatlari
              </h2>
            </div>
          </Reveal>

          <div className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-2 lg:mt-16 lg:grid-cols-4">
            {FEATURES.map((f, i) => {
              const Icon = f.icon;
              return (
                <Reveal key={f.title} delay={i * 80}>
                  <Link
                    href={f.href}
                    className="card card-hover group flex h-full flex-col p-6"
                  >
                    <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-agro-50 text-agro-700 transition-colors duration-300 group-hover:bg-agro-700 group-hover:text-white">
                      <Icon className="h-5 w-5" />
                    </span>
                    <h3 className="mt-4 text-base font-semibold tracking-tight text-navy-950">{f.title}</h3>
                    <p className="mt-2 text-[13px] leading-relaxed text-slate-500">{f.text}</p>
                    <span className="mt-auto inline-flex items-center gap-1 pt-4 text-xs font-semibold text-agro-700 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                      O'tish
                      <ArrowRight className="h-3.5 w-3.5" />
                    </span>
                  </Link>
                </Reveal>
              );
            })}
          </div>
        </div>
      </section>

      {/* ============================== SEGMENTS ============================== */}
      <section className="border-b border-slate-200/70">
        <div className="container-x py-16 lg:py-24">
          <Reveal>
            <div className="mx-auto max-w-2xl text-center">
              <span className="eyebrow justify-center text-harvest-600">Kimlar uchun</span>
              <h2 className="mt-4 text-3xl font-bold tracking-tight text-navy-950 sm:text-4xl">
                Har bir agrobiznes turi uchun tayyor model
              </h2>
            </div>
          </Reveal>

          <div className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-3 lg:mt-16">
            {SEGMENTS.map((seg, i) => {
              const Icon = seg.icon;
              return (
                <Reveal key={seg.title} delay={i * 90}>
                  <Link
                    href={seg.href}
                    className="card card-hover group flex h-full flex-col p-7"
                  >
                    <div className="flex items-center justify-between">
                      <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-navy-900 text-white">
                        <Icon className="h-6 w-6" />
                      </span>
                      <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-[11px] font-bold text-slate-500">
                        {seg.meta}
                      </span>
                    </div>
                    <h3 className="mt-5 text-lg font-semibold tracking-tight text-navy-950">{seg.title}</h3>
                    <p className="mt-2.5 text-sm leading-relaxed text-slate-600">{seg.text}</p>
                    <span className="mt-auto inline-flex items-center gap-1.5 pt-5 text-sm font-semibold text-agro-700 transition-colors group-hover:text-agro-800">
                      Demo ssenariyni ochish
                      <ArrowRight className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-0.5" />
                    </span>
                  </Link>
                </Reveal>
              );
            })}
          </div>
        </div>
      </section>

      {/* ============================== CTA ============================== */}
      <section className="py-16 lg:py-24">
        <div className="container-x">
          <Reveal>
            <div className="relative overflow-hidden rounded-2xl bg-navy-950 px-8 py-14 sm:px-12 lg:px-16">
              <div className="bg-grid-light mask-fade-b pointer-events-none absolute inset-0" aria-hidden="true" />
              <div
                className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-agro-600/20 blur-3xl"
                aria-hidden="true"
              />
              <div className="relative flex flex-col items-start justify-between gap-8 lg:flex-row lg:items-center">
                <div className="max-w-2xl">
                  <span className="eyebrow text-agro-300">Amalda sinab ko'ring</span>
                  <h3 className="mt-4 text-2xl font-bold tracking-tight text-white sm:text-3xl">
                    Interaktiv moliyaviy tahlil dvigateli tayyor
                  </h3>
                  <p className="mt-3 text-sm leading-relaxed text-slate-300 sm:text-base">
                    Sintetik fermer xo'jaligi ma'lumotlarini yuklang, real Python/FastAPI moliyaviy yadrosida
                    hisoblang va interaktiv grafikda kassa uzilishini ko'ring.
                  </p>
                </div>
                <div className="flex w-full shrink-0 flex-col gap-3 sm:w-auto sm:flex-row">
                  <Link
                    href="/demo"
                    className="inline-flex items-center justify-center gap-2 rounded-lg bg-agro-500 px-6 py-3.5 text-sm font-bold text-white shadow-md transition-all duration-200 hover:bg-agro-400 active:translate-y-px"
                  >
                    Demo tanlagichga o'tish
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                  <Link
                    href="/dashboard"
                    className="inline-flex items-center justify-center rounded-lg border border-navy-700 bg-navy-900/60 px-6 py-3.5 text-sm font-semibold text-slate-200 transition-all duration-200 hover:border-navy-600 hover:text-white active:translate-y-px"
                  >
                    Moliya paneli
                  </Link>
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </section>
    </div>
  );
}
