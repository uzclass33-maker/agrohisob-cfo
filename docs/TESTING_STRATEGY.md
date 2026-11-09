# AGROHISOB CFO — SINOV STRATEGIYASI VA SIFAT KAFOLATI
## Comprehensive QA & Mathematical Verification Strategy

---

## 1. Sinov Falsafasi va Piramidasi

AgriFinTech dasturiy ta'minotida har qanday hisoblash xatosi bank kreditining rad etilishiga yoki fermerning noto'g'ri moliyaviy qaror qabul qilishiga olib kelishi mumkin. Shu sababli, AgroHisob CFO platformasida **qattiq deterministik sinov piramidasi** amalga oshirilgan:

1. **Birlik Sinovlari (Unit Tests):**
   - Moliyaviy dvigatel arifmetikasi, `Decimal` aniqligi, DSCR koeffitsienti, VMQ-613 yer ijara huquqi baholash formulalari.
2. **Integratsion Sinovlar (Integration Tests):**
   - REST API endpointlari (`/health`, `/ready`, `/api/v1/demo/...`, `/api/financials/...`).
   - SQLite / PostgreSQL bazasiga ma'lumotlarni yozish va qayta o'qish.
3. **Deterministik Matematik Invariant Sinovlari (Test A, B, C, D, E):**
   - Oylik kassa qoldiqlarining uzluksizligi va balans tenglamasining qat'iy bajarilishi.
4. **Foydalanuvchi Interfeysi Sinovlari (Frontend Route Verification):**
   - Next.js 14 App Router sahifalarining statik va dinamik renderlanishi, `<Suspense>` chegaralari, API rewrites orqali integratsiyasi.

---

## 2. Rasmiy Matematik Sinovlar (Test A dan E gacha)

### Test A: Musbat Kassa Oqimi (Positive Cash Flow)
- **Shart:** Boshlang'ich qoldiq = 10,000,000 UZS. Tushumlar = 8,000,000 UZS. Xarajatlar = 5,000,000 UZS.
- **Kutilgan Natija:** Sof kassa oqimi = +3,000,000 UZS. Yakuniy qoldiq = 13,000,000 UZS.
- **Tekshiruv:** $13,000,000 == 10,000,000 + 8,000,000 - 5,000,000$.
- **Holat:** `PASSED` (`test_financial_calculation_test_a_positive_cash_flow`).

### Test B: Manfiy Kassa Oqimi (Negative Cash Flow / Deficit)
- **Shart:** Boshlang'ich qoldiq = 10,000,000 UZS. Tushumlar = 2,000,000 UZS. Xarajatlar = 7,000,000 UZS.
- **Kutilgan Natija:** Sof kassa oqimi = -5,000,000 UZS. Yakuniy qoldiq = 5,000,000 UZS.
- **Tekshiruv:** $5,000,000 == 10,000,000 + 2,000,000 - 7,000,000$.
- **Holat:** `PASSED` (`test_financial_calculation_test_b_negative_cash_flow`).

### Test C: Nol Faollik (Zero Activity Invariant)
- **Shart:** Boshlang'ich qoldiq = 10,000,000 UZS. Tushumlar = 0 UZS. Xarajatlar = 0 UZS.
- **Kutilgan Natija:** Barcha 12 oy davomida qoldiq 10,000,000 UZS bo'lib qoladi.
- **Tekshiruv:** $10,000,000 == 10,000,000 + 0 - 0$.
- **Holat:** `PASSED` (`test_financial_calculation_test_c_zero_activity`).

### Test D: O'nlik Kasr Aniqligi (Decimal Precision & Float Invariance)
- **Shart:** Standart suzuvchi nuqta (IEEE 754 binary float) xatoliklarini yo'q qilish.
- **Tekshiruv:** Boshlang'ich qoldiq 100,000,000.45 UZS, kasrli tushum va xarajatlar summasi oxirgi tiyinigacha aniq hisoblanishi.
- **Holat:** `PASSED` (`test_financial_calculation_test_d_decimal_precision`).

### Test E: Oylik Uzluksizlik (Monthly Continuity Roll-Forward)
- **Shart:** Har bir $N$ oy uchun ($1 \le N \le 11$):
  $$\text{Opening Balance}_{N+1} \equiv \text{Closing Balance}_N$$
  $$\text{Closing Balance}_N \equiv \text{Opening Balance}_N + \text{Inflows}_N - \text{Outflows}_N$$
- **Holat:** `PASSED` (`test_financial_calculation_test_e_monthly_continuity`).

---

## 3. Avtomatlashtirilgan Sinov Natijalari

Backend test to'plami `pytest` yordamida ishga tushirildi:
- **Jami testlar:** 23 ta
- **Muvaffaqiyatli o'tganlar:** 23 ta (100%)
- **Muvaffaqiyatsiz testlar:** 0 ta
- **Bajarilish vaqti:** ~3.0 soniya

```
backend/tests/test_api.py::test_api_health PASSED
backend/tests/test_api.py::test_api_readiness PASSED
backend/tests/test_api.py::test_v1_demo_organizations PASSED
backend/tests/test_api.py::test_v1_demo_organization_details PASSED
backend/tests/test_api.py::test_v1_demo_organization_cashflow PASSED
backend/tests/test_api.py::test_list_scenarios_api PASSED
backend/tests/test_api.py::test_get_scenario_details_api PASSED
backend/tests/test_api.py::test_get_nonexistent_scenario_404 PASSED
backend/tests/test_api.py::test_calculate_financials_api PASSED
backend/tests/test_api.py::test_calculate_invalid_request_422 PASSED
backend/tests/test_api.py::test_stress_test_api PASSED
backend/tests/test_api.py::test_credit_readiness_report_api PASSED
backend/tests/test_financial_calculations.py::test_financial_calculation_test_a_positive_cash_flow PASSED
backend/tests/test_financial_calculations.py::test_financial_calculation_test_b_negative_cash_flow PASSED
backend/tests/test_financial_calculations.py::test_financial_calculation_test_c_zero_activity PASSED
backend/tests/test_financial_calculations.py::test_financial_calculation_test_d_decimal_precision PASSED
backend/tests/test_financial_calculations.py::test_financial_calculation_test_e_monthly_continuity PASSED
backend/tests/test_financial_engine.py::test_monthly_cash_flow_identity_rule PASSED
backend/tests/test_financial_engine.py::test_dscr_calculation_and_benchmarks PASSED
backend/tests/test_financial_engine.py::test_vmq613_valuation_formula PASSED
backend/tests/test_scenarios.py::test_three_synthetic_scenarios_exist_and_labeled PASSED
backend/tests/test_scenarios.py::test_all_scenarios_internal_consistency PASSED
backend/tests/test_scenarios.py::test_small_farmer_seasonality_and_deficit_detection PASSED
```

---

## 4. Frontend Marshrutlarining Tekshiruvi

Next.js 14 ishlab chiqarish serveri (`http://localhost:3000`) orqali barcha 6 ta asosiy sahifa tekshirildi:
1. `GET /` -> `200 OK` (Bosh sahifa, makroiqtisodiy ko'rsatkichlar)
2. `GET /demo` -> `200 OK` (3 ta sintetik korxona tanlovi)
3. `GET /dashboard` -> `200 OK` (KPI kartalar, kassa grafigi, 12 oylik jadval)
4. `GET /data-import` -> `200 OK` (E-faktura va bank ko'chirmasi importi)
5. `GET /scenario-analysis` -> `200 OK` (Sezgirlik slayderlari va stress-test)
6. `GET /credit-report` -> `200 OK` (Bank anderrayting dosyesi va VMQ-613 garov qiymati)
