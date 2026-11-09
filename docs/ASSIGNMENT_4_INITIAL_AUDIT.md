# AGROHISOB CFO — TOPSHIRIQ 4 OLDIDAN DASTLABKI AUDIT VA TIZIMLI TAHLIL

**Hujjat kodi:** `DOC-AGRO-A4-AUDIT-001`  
**Sana:** 2026-yil 9-noyabr  
**Holat:** TASDIQLANGAN (APPROVED)  
**Auditorlar:** Principal FinTech Software Architect, FP&A Specialist & Senior Full-Stack Engineering Team  

---

## 1. KIRISH VA AUDIT MAQSADI

Ushbu hujjat **AgroHisob CFO** platformasining 4-topshirig'i — **"AI-CFO Dashboard, Financial Intelligence, Risk Monitoring & Interactive Analytics"** (AI-CFO Boshqaruv Paneli, Moliyaviy Tahlil, Xatarlar Monitoringi va Interaktiv Simulyatsiya) amalga oshirilishidan oldingi mavjud kod bazasi, hisob-kitob dvigatellari, import quvurlari va frontend komponentlarini mustaqil auditdan o'tkazish natijalarini jamlaydi.

Audit maqsadi:
1. 1-, 2- va 3-topshiriqlarda yaratilgan komponentlarning to'liq ishlashini tekshirish;
2. Dashboard va AI-CFO tahliliy tizimi uchun zarur bo'lgan orqa (backend) xizmatlar va hisob-kitob dvigatellari bilan bog'lanish nuqtalarini aniqlash;
3. Buxgalteriya va moliya tamoyillariga zid bo'lgan (masalan, frontendda ssenariylarni qo'lda hisoblash kabi) texnik qarzlarni aniqlash va bartaraf etish rejasini tuzish;
4. Ikki qatlamli (Deterministik qoida dvigateli + Ixtiyoriy maxfiy LLM tushuntiruvchisi) AI-CFO arxitekturasining poydevorini belgilash.

---

## 2. MAVJUD KOD BAZASI HOLATI

- **Git ombori:** `master` tarmog'ida, oxirgi commit `29e69a3` (*"docs: finalize universal audit reports for Assignment 3"*). Ishchi daraxt toza.
- **Avtomatlashtirilgan testlar:** `python -m pytest` orqali 93 ta test to'liq muvaffaqiyatli o'tmoqda (**100% PASS**, 0 ta xato).
- **Backend xizmati:** FastAPI (`http://127.0.0.1:8000`) barcha routes bilan faol.
- **Frontend xizmati:** Next.js 14 SSR (`http://localhost:3000`) barcha 6 ta asosiy yo'nalish bo'yicha ishlab turibdi.
- **Mavjud hisob-kitob modullari (`backend/app/financial_engine/`):**
  - `cashflow.py` — oylik kassa oqimlari, sof pul oqimi va kassa qoldiqlari uzluksizligi.
  - `forecasting.py` — 12 oylik mavsumiy agrar prognozlash (g'alla, paxta, bog'dorchilik sikllari).
  - `loans.py` — annuitet va differensial kredit amortizatsiya jadvallari, imtiyozli davrlar.
  - `dscr.py` — CFADS va qarz xizmati qoplash koeffitsienti (DSCR).
  - `risk.py` — likvidlik yetishmovchiligi, manfiy qoldiq va qarz yuki xatarlarini deterministik aniqlash.
  - `scenarios.py` — bazaviy, optimistik, pessimistik va maxsus stress-test hisob-kitoblari.
- **Mavjud import moduli (`backend/app/import_engine/`):**
  - CSV va XLSX ko'p formatli yuklash, 12 ta kanonik ustun xaritalash, 3 bosqichli toifalash va Invoys vs Kassa reestrlari ajratilishi.

---

## 3. ANIQLANGAN CHEKLOVLAR VA TEXNIK QARZLAR (TECHNICAL DEBT)

1. **Frontenddagi ssenariy simulyatsiyasi (Kritik):**
   - Hozirgi `frontend/src/app/dashboard/page.tsx` faylida optimistik va pessimistik variantlar tanlanganda moliya dvigateliga murojaat qilmasdan, frontend ichida `inBump = m.total_inflows * 1.20` kabi arifmetik hisob-kitoblar qilingan. Bu topshiriqning *"All financial values must come from authoritative backend calculations"* qoidasiga ziddir.
   - **Tuzatish:** Barcha ssenariylar va simulyatsiyalar yagona `/api/v1/dashboard/scenarios` backend API orqali amalga oshiriladi.
2. **Yagona konsolidatsiyalangan Dashboard API yo'qligi:**
   - Hozirda dashboard ma'lumotlarni turli tarqoq endpointlardan (`/api/scenarios`, `/api/financials/calculate`, `/api/v1/finance/loans/schedule`) qisman yig'moqda. 7 ta modul uchun to'liq ma'lumot beruvchi yagona `/api/v1/dashboard/*` marshrutlar to'plami talab etiladi.
3. **AI-CFO tahliliy tushuntirish dvigatelining yo'qligi:**
   - 4-topshiriqning asosiy yangiligi — bu hisoblangan ko'rsatkichlarni tahlil qilib, sabab-oqibat bog'lanishlarini o'zbek tilida tushuntirib beruvchi **AI-CFO Financial Insights Engine**. Ushbu modul ikki qatlamli arxitekturada yaratilishi shart.

---

## 4. 4-TOPSHIRIQ REJALASHTIRILGAN ARXITEKTURASI

Quyidagi yangi modullar va komponentlar yaratiladi:

### 4.1. Backend Modullari
1. **`backend/app/financial_engine/insights.py` (AI-CFO Insights Engine):**
   - **Layer A (Deterministik Qoida Dvigateli):** Hisoblangan oylik kassa oqimlari, prognoz kamomadlari, qarz xizmati va likvidlik ko'rsatkichlarini tahlil qilib, strukturalangan faktlar to'plamini (`InsightID`, `severity`, `metric_ref`, `explanation_uz`, `suggested_action_uz`, `evidence_data`) shakllantiradi.
   - **Layer B (Maxfiy LLM Tushuntiruvchisi Adapteri):** Gemini API yordamida faktlarni o'zbek tilida ravon bayon qiladi. Tashqi LLM ulanmagan yoki xato berganda, avtomatik ravishda Layer A ning deterministik tushuntirishlariga o'tadi (Zero-failure fallback).
2. **`backend/app/api/routes_dashboard.py` va `routes_insights.py`:**
   - `GET /api/v1/dashboard/overview` — tashkilot konteksti, asosiy KPIlar.
   - `GET /api/v1/dashboard/cashflow` — tarixiy va kassa oqimlari, toifalar taqsimoti.
   - `GET /api/v1/dashboard/forecast` — 12 oylik prognoz va taxminlar (assumptions) paneli.
   - `GET /api/v1/dashboard/debt` — kredit to'lovlari, foizlar va DSCR.
   - `GET /api/v1/dashboard/risks` — deterministik xatarlar jurnali va tavsiyalar.
   - `POST /api/v1/dashboard/scenarios` — ssenariylarni to'liq qayta hisoblash.
   - `GET /api/v1/insights` — AI-CFO tahliliy xulosalari va dalillar jurnali.
   - `POST /api/v1/insights/explain` — batafsil tushuntirish berish.

### 4.2. Frontend Boshqaruv Paneli (`frontend/src/app/dashboard/page.tsx`)
- 7 ta to'liq integratsiyalangan modul:
  1. Executive Overview & KPI Cards (Inflow, Outflow, Net, Closing, Debt Service, DSCR, Min Projected Balance)
  2. Cash-Flow Intelligence (Interaktiv grafiklar, toifalar va davrlar filtrlari)
  3. Seasonal 12-Month Forecast (Tarix va prognoz chegarasi, tahrirlanuvchi taxminlar paneli)
  4. Debt & DSCR Analytics (Kredit amortizatsiyasi, asosiy qarz vs foiz, DSCR riski)
  5. Financial Risk Monitor (Xatarlar kartalari, og'irlik darajalari: CRITICAL, HIGH, MEDIUM, LOW)
  6. Interactive Scenario Analysis (Slidellar orqali hosil narxi, xarajatlar, kechikishlarni o'zgartirib backendda hisoblash)
  7. AI-CFO Insights Workspace (Moliyaviy salomatlik xulosasi, aniqlangan anomaliyalar, amaliy tavsiyalar, tekshiriluvchi dalillar jadvali)

---

## 5. XULOSA

Dastlabki audit natijasida barcha oldingi komponentlar barqaror ekanligi tasdiqlandi. 4-topshiriqni amalga oshirishga to'liq kirishildi.
