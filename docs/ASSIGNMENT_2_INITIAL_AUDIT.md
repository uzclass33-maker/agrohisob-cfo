# AGROHISOB CFO — 2-TOPSHIRIQ BOSHLANG'ICH AUDITI VA REJA
## Assignment 2: Financial Calculation Engine, Seasonal Cash-Flow Forecasting & Debt Risk Analytics

**Audit Sanasi:** 2026-11-09  
**Holati:** Dastlabki audit yakunlandi, poydevor 100% barqaror (29/29 testlar o'tgan)  
**Auditorlar:** Principal FinTech Software Engineer, Quantitative Financial Analyst, Python Backend Architect  

---

## 1. Mavjud Funksionallik (Existing Functionality)

1. **Hisoblash Dvigateli (Assignment 1):**
   - `backend/app/services/financial_engine.py` mavjud bo'lib, u 12 oylik kassa balansi rekonsilyatsiyasi ($Closing = Opening + Inflows - Outflows$, $Opening_{t+1} = Closing_t$), umumiy DSCR hisobi hamda VMQ-613 qishloq xo'jaligi yer ijara huquqini DCF usulida baholashni amalga oshiradi.
   - `backend/app/services/synthetic_data.py` da 3 ta to'liq kalibrlangan sintetik korxona benchmarki mavjud:
     - Kichik Fermer (Andijon, 65 ga, paxta va sabzavot)
     - Eksportyor (Samarqand, 120 ga, intensiv bog' va sovutgich)
     - Agro-Klaster (Qashqadaryo, 2500 ga, vertikal integratsiyalashgan)
   - `backend/app/services/scenario_engine.py` oddiy foizli shoklarni (yield, price, cost) hisoblaydi.
2. **API Endpointlari:**
   - `/health`, `/ready`, `/api/v1/demo/organizations`, `/api/v1/demo/organizations/{id}/cashflow`, `/api/financials/calculate`, `/api/financials/stress-test`, `/api/reports/credit-readiness/{id}`.
3. **Frontend Dashboard:**
   - Next.js 14 App Router da KPI kartalari, Recharts kassa grafigi, 12 oylik jadval va sezgirlik slayderlari mavjud.

---

## 2. Qayta Ishlatiladigan Komponentlar (Reusable Components)

- **Matematik Invariantlar:** Oylik uzluksizlik va kassa balansi tenglamasi qoidalari to'liq saqlanadi.
- **Sintetik Korxonalar:** 3 ta agrobiznes ssenariysi yangi kengaytirilgan dvigatel uchun to'liq mos keladi.
- **UI Komponentlar:** Next.js dagi `CashFlowChart.tsx`, layout va formatters kutubxonalari kengaytiriladi.

---

## 3. Yetishmayotgan Imkoniyatlar va Yangi Talablar (Missing Capabilities for Assignment 2)

Hozirgi `financial_engine.py` yaxlit (monolit) bitta faylda bo'lib, 2-topshiriq talab qilgan chuqur modullilikka ega emas:
1. **Modulli Arxitektura:**
   - `backend/app/financial_engine/` paketi talab etiladi:
     - `cashflow.py` (tarixiy kassa oqimlarini qayta ishlash, tranzaksiyalar bo'yicha agregatsiya, qaytarishlar va valyuta yaxlitligi)
     - `forecasting.py` (12 oylik mavsumiy deterministik prognozlash, hosil yig'imi va to'lov tushumlari kechikishlari, ekin turlari taqvimi)
     - `loans.py` (annuitet va teng asosiy qarz/differensial to'lov grafiklari, foizlar hisobi, yaxlitlash qoldiqlari nazorati)
     - `dscr.py` (CFADS aniqligi, oylik va yillik DSCR, nol qarz va manfiy operatsion oqim holatlarini to'g'ri qayta ishlash, tushunarli indikatorlar)
     - `scenarios.py` (baza, optimistik, pessimistik va maxsus ssenariylarni chuqur qayta hisoblash)
     - `risk.py` (aniq ogohlantirishlar: manfiy kassa, likvidlik buferi taqchilligi, qarz bosimi, mavsumiy kassa uzilishi)
     - `schemas.py` (kiruvchi va chiquvchi Pydantic v2 sxemalari)
     - `exceptions.py` (moliyaviy xatoliklar va chegaraviy holatlar boshqaruvi)
2. **Yangi Versiyalangan API Endpointlar:**
   - `POST /api/v1/finance/cashflow/analyze`
   - `POST /api/v1/finance/forecast`
   - `POST /api/v1/finance/loans/schedule`
   - `POST /api/v1/finance/dscr/calculate`
   - `POST /api/v1/finance/scenarios/analyze`
3. **Frontend Boshqaruv Panelini Kengaytirish:**
   - Haqiqiy kredit to'lov jadvali ko'rinishi
   - DSCR tahlili va tushuntirish paneli
   - 4 xil ssenariy (Baza, Optimistik, Pessimistik, Maxsus) selektori
   - Likvidlik xatarlari va ogohlantirishlar paneli

---

## 4. Rejalashtirilgan Bosqichlar (Execution Plan)

1. **1-Qadam:** `backend/app/financial_engine/` paketini yaratish (`schemas.py`, `exceptions.py`, `cashflow.py`, `loans.py`, `dscr.py`, `forecasting.py`, `scenarios.py`, `risk.py`).
2. **2-Qadam:** Barcha hisoblash formulalarini `Decimal` aniqligi bilan mustaqil funksiyalar sifatida ishlab chiqish.
3. **3-Qadam:** Yangi REST API routerlarini (`backend/app/api/routes_finance.py`) yaratish va `app/main.py` ga ulash.
4. **4-Qadam:** Qamrovli moliyaviy unit testlar to'plamini (`test_cashflow.py`, `test_loans.py`, `test_dscr.py`, `test_forecasting.py`, `test_scenarios_advanced.py`, `test_risk.py`) yozish.
5. **5-Qadam:** Frontendni yangi hisoblash imkoniyatlari bilan boyitish (`dashboard`, `scenario-analysis`, `credit-report`).
6. **6-Qadam:** Barcha 18 ta qabul qilish mezoni (AC-01 .. AC-18) bo'yicha to'liq verifikatsiya va hujjatlashtirishni yakunlash.
