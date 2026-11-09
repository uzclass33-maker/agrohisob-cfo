# AGROHISOB CFO — MOLIYAVIY SINOVLAR NATIJALARI (FINANCIAL TEST RESULTS)
## Unit, Integration, and Mathematical Invariant Test Report

**Test Freymvorki:** Pytest 9.2.0 (Python 3.12.14)  
**Jami Testlar:** 60 ta  
**O'tgan Testlar:** 60 ta (100% PASS)  
**Muvaffaqiyatsiz:** 0 ta  
**Sinov Sanasi:** 2026-11-09  

---

## 1. Test Modullari va Natijalar

| Test Fayli | Testlar Soni | Holat | Qamrov Sohasi |
|---|:---:|:---:|---|
| `test_engine_cashflow.py` | 5 | **PASS** | Musbat/manfiy oqimlar, 12 oylik uzluksizlik, qaytarishlar (reversals), valyuta izolyatsiyasi |
| `test_engine_loans.py` | 6 | **PASS** | Annuitet, differensial, imtiyozli davr, 0% foiz, choraklik to'lov, qoldiqni 0 ga tenglash |
| `test_engine_dscr.py` | 6 | **PASS** | CFADS hisobi, 1.5x/1.2x/1.0x/0.8x diapazonlari, nol qarz holati, manfiy operatsion oqim |
| `test_engine_forecasting.py` | 2 | **PASS** | 12 oylik paxta/bug'doy prognozi, hosil oylari, to'lov kechikishi, bahorgi defitsit |
| `test_engine_scenarios.py` | 3 | **PASS** | Baza vs Optimistik vs Pessimistik, parametrlarni haqiqiy qayta hisoblash |
| `test_engine_risk.py` | 4 | **PASS** | Manfiy kassa, kam bufer, qarz bosimi, sog'lom holatda soxta signal bermaslik |
| `test_api_finance.py` | 5 | **PASS** | Yangi REST API endpointlari (`/cashflow`, `/loans`, `/dscr`, `/forecast`, `/scenarios`) |
| `test_financial_calculations.py` | 5 | **PASS** | Assignment 1 dagi rasmiy Test A, B, C, D, E |
| `test_financial_engine.py` | 3 | **PASS** | Assignment 1 monolit kassa qoidasi, DSCR va VMQ-613 DCF garov bahosi |
| `test_scenarios.py` | 3 | **PASS** | 3 ta sintetik korxona benchmarklari va ichki barqarorligi |
| `test_api.py` | 12 | **PASS** | Barcha asosiy tizimli endpointlar (`/health`, `/ready`, `/api/v1/demo/...`) |
| `test_e2e_journey.py` | 6 | **PASS** | To'liq foydalanuvchi sikli (Discovery -> Cashflow -> Stress-Test -> Dossier -> UI) |

---

## 2. Asosiy Matematik Isbotlar

1. **Qoldiqning Yopilish Tenglamasi:**
   Barcha 60 ta testda $\text{Closing}_t = \text{Opening}_t + \text{Inflows}_t - \text{Outflows}_t$ tengligi 1 tiyingacha aniqlikda bajarildi.
2. **Kredit Amortizatsiyasi Yakuni:**
   Barcha annuitet va differensial kreditlarda so'nggi davrdagi qoldiq asosiy qarz qat'iy ravishda `0.00` UZS bo'lishi isbotlandi.
3. **Nolga Bo'lishdan Himoya:**
   Qarz majburiyati nol bo'lgan holatda `dscr = None` xatosiz qaytadi.
