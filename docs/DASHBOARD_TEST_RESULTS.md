# AgroHisob CFO — Assignment 4 Test Natijalari

## 1. Testlar Xulosasi

- **Jami testlar soni**: 104 ta
- **O'tgan testlar soni**: 104 ta (100% PASS)
- **Muvaffaqiyatsiz testlar soni**: 0 ta
- **Bajarilish vaqti**: ~8.53 soniya
- **Platforma**: Windows / Python 3.12.14 / pytest 9.2.0

## 2. Assignment 4 Maxsus Test Modullari

| Test Fayli | Qamrov | Natija |
| :--- | :--- | :--- |
| `backend/tests/test_dashboard_overview.py` | 7 ta asosiy KPI, boshlang'ich va yakuniy kassa balanslari, tashkilotlarni almashtirish | **PASSED** (2/2) |
| `backend/tests/test_dashboard_cashflow.py` | 12 oylik roll-forward identity, toifaviy taqsimot rekonsilyatsiyasi | **PASSED** (1/1) |
| `backend/tests/test_dashboard_forecast.py` | 12 oylik agrar prognoz, ekinlar rejasi, eng past kassa nuqtasi | **PASSED** (1/1) |
| `backend/tests/test_dashboard_debt_dscr.py` | Asosiy qarz va foiz to'lovlari, kredit jadvallari, DSCR risk darajalari | **PASSED** (1/1) |
| `backend/tests/test_dashboard_risks.py` | Deterministik xavflar (kassa uzilishi, bufer, qarz bosimi, mavsumiylik) | **PASSED** (1/1) |
| `backend/tests/test_dashboard_scenarios.py` | Backend orqali Optimistik va Pessimistik ssenariylarni to'liq qayta hisoblash | **PASSED** (2/2) |
| `backend/tests/test_ai_insights_engine.py` | Layer A deterministik generatsiya, Layer B da'vo tekshiruvi va fallback | **PASSED** (2/2) |
| `backend/tests/test_e2e_dashboard_journey.py` | Barcha 7 modul bo'yicha to'liq CFO tahlil sayohati | **PASSED** (1/1) |

## 3. Oldingi Topshiriqlar Regressiya Barqarorligi

- Assignment 1 (Arxitektura va sintetik ma'lumotlar): 100% PASSED
- Assignment 2 (Moliyaviy hisoblash dvigateli, amortizatsiya, DSCR): 100% PASSED
- Assignment 3 (Aqlli ma'lumotlar importi, rekonsilyatsiya, lejerlar ajratilishi): 100% PASSED
- Live Audit Server E2E (FastAPI & Next.js): 100% PASSED
