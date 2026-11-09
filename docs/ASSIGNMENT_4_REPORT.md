# AGROHISOB CFO — ASSIGNMENT 4 YAKUNIY HISOBOTI

## 1. Topshiriqning Asosiy Vazifasi

Assignment 4 ning asosiy maqsadi — AgroHisob CFO platformasida agrobiznes korxonalari uchun zamonaviy, interaktiv va deterministik moliyaviy hisob-kitob dvigateliga to'liq bog'langan **AI-CFO Financial Intelligence Dashboard** tizimini yaratish, sinovdan o'tkazish va hujjatlashtirishdan iborat bo'lgan.

## 2. Amalga Oshirilgan 7 ta Modul

1. **Executive Financial Overview (Ijroiya Xulosa)**:
   - 7 ta backend tomonidan hisoblangan asosiy KPI kartalari: Yalpi Tushum, Jami Chiqim, Sof Kassa Oqimi, Yakuniy Kassa, Operatsion Kassa Oqimi, Yillik Qarz Xizmati, DSCR Koeffitsienti.
   - Boshlang'ich kassa, eng past kassa nuqtasi va kassa uzilishi oylari monitoringi.

2. **Cash-Flow Intelligence (Kassa Oqimlari Tahlili)**:
   - 12 oylik interaktiv kassa oqimlari grafigi (Recharts).
   - Tushumlar va chiqimlarning toifaviy taqsimoti (urug'lik, o'g'it, yoqilg'i, ish haqi, lizing, subsidiyalar).
   - Oylik batafsil roll-forward rekonsilyatsiya jadvali (`Opening + In - Out = Closing`).

3. **Twelve-Month Seasonal Forecasting Dashboard (12 Oylik Mavsumiy Prognoz)**:
   - Tarixiy va prognoz qilinayotgan agrar tsikl chegarasi.
   - Hosildorlik, ekin maydonlari va narxlar farazlari paneli (Assumptions Panel).
   - Bahorgi ekin ekish davridagi kassa uzilishi va kuzgi hosil tushumlari vizualizatsiyasi.

4. **Debt & DSCR Analytics (Qarz & DSCR Ko'rsatkichlari)**:
   - Asosiy qarz va foiz to'lovlari mutanosibligi.
   - Bank standartlari bo'yicha DSCR risk darajalari (<1.0x Kritik, 1.0-1.2x Cheklangan, 1.2-1.5x Mo'tadil, >=1.5x Mustahkam).
   - Amaldagi kredit shartnomalari, stavkalar, grafiklar va garov ta'minoti reyestri.

5. **Financial Risk Monitoring (Moliyaviy Xavflar Monitori)**:
   - Deterministik risk qoidalari: Kassa taqchilligi, Past likvidlik buferi, Qarz xizmati bosimi, Mavsumiy konsentratsiya.
   - Xavflilik darajasi: CRITICAL, HIGH, MEDIUM, LOW.
   - Har bir xavf uchun tushuntirish va amaliy biznes boshqaruv tavsiyalari.

6. **Interactive Scenario Analysis (Interaktiv Ssenariylar Simulyatsiyasi)**:
   - Ssenariy turlari: Baza (0%), Optimistik (+20%/-10%), Pessimistik (-20%/+15%), Maxsus (Custom).
   - 4 ta real-vaqt slayderi: Tushum o'zgarishi, Xarajatlar o'zgarishi, To'lov kechikishi, Foiz stavkasi delta.
   - **Backend recalculation**: Hech qanday frontend hisob-kitobisiz, to'liq Financial Engine qayta chaqiruvi.
   - Baza va Stressed ssenariylar o'rtasidagi farqlar (Variance) tahlili.

7. **AI-CFO Financial Insights Engine (AI-CFO Xulosalar Dvigateli)**:
   - Ikki qatlamli (Two-Layer) arxitektura:
     - Layer A: 100% deterministik, lokal qoidalar dvigateli.
     - Layer B: Maxfiylik kafolatlangan LLM tushuntirishi (hech qanday STIR yoki bank hisob raqami yuborilmaydi).
   - Factual Numerical Claim Validation: Sun'iy sonlar yoki soxta regulyator da'volari rad etiladi va xatoliksiz Layer A ga qaytiladi.

## 3. Sifat va Test Ko'rsatkichlari

- **Jami testlar**: 104/104 PASSED (100%)
- **Next.js Production Build**: 100% muvaffaqiyatli (`pnpm build` exit 0, barcha sahifalar statik va optimallashgan)
- **FastAPI Uvicorn**: `http://127.0.0.1:8000` da barcha REST endpointlar 200 OK qaytarmoqda.
- **Frontend Server**: `http://localhost:3000` da ishlab turibdi.
