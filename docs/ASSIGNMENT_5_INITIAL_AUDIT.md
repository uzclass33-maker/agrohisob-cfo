# AgroHisob CFO — Assignment 5 Boshlang'ich Auditi (Pre-Implementation Audit)

## 1. Loyihaning Joriy Holati
- **Loyiha nomi:** AgroHisob CFO (AgriFinTech B2B SaaS platformasi)
- **Hozirgi bosqich:** Assignment 5 — Credit Readiness Assessment, Professional Bank Dossier, PDF Reporting & Excel Financial Model Generation
- **Oldingi topshiriqlar holati:**
  - Assignment 1 (Tizim arxitekturasi va sintetik demo korxonalar): Muvaffaqiyatli yakunlangan.
  - Assignment 2 (Moliyaviy dvigatel, qarz amortizatsiyasi, DSCR, 12 oylik mavsumiy prognoz): Muvaffaqiyatli yakunlangan.
  - Assignment 3 (Aqlli moliyaviy ma'lumotlar importi, rekonsilyatsiya, lejerlar ajratilishi): Muvaffaqiyatli yakunlangan.
  - Assignment 4 (AI-CFO Dashboard, moliyaviy intellekt, xavflar monitori, interaktiv ssenariylar): Muvaffaqiyatli yakunlangan (104/104 test PASS).

## 2. Mavjud Dvigatellar va Qayta Ishlatiladigan Komponentlar
- `backend/app/financial_engine/`:
  - `process_historical_cashflow`: Tarixiy pul oqimlarini hisoblash va toifalash.
  - `calculate_seasonal_forecast`: 12 oylik mavsumiy agrar prognoz.
  - `calculate_loan_schedule`: Annuitet va differensial kredit amortizatsiyasi.
  - `calculate_dscr`: CFADS va qarzga xizmat ko'rsatish qoplash koeffitsienti.
  - `run_scenario_analysis`: Baza, Optimistik, Pessimistik ssenariylar tahlili.
  - `detect_monthly_liquidity_risks`: Kassa uzilishi va likvidlik xavflari.
- `backend/app/api/routes_dashboard.py`:
  - `_get_org_data`, `_build_forecast_request`: Sintetik benchmarklar va haqiqiy lejer ma'lumotlari.

## 3. Assignment 5 Bo'yicha Kiritiladigan Yangi Modullar
1. `backend/app/reporting/report_schemas.py`: Canonical `CreditDossierData`, `CreditProfile`, `DocumentReadinessChecklist`, `FinancialReadinessAssessment`.
2. `backend/app/reporting/credit_profile.py`: Kredit arizasi profili va moliyalashtirish so'rovi tekshiruvi.
3. `backend/app/reporting/readiness_assessment.py`: Hujjatlar to'liqligi nazorat ro'yxati va deterministik tayyorgarlik darajasi.
4. `backend/app/reporting/dossier_builder.py`: 8 ta bo'limdan iborat to'liq bank dosyesi ma'lumotlar to'plamini shakllantiruvchi yagona manba.
5. `backend/app/reporting/pdf_generator.py`: ReportLab asosidagi professional, bosmaga tayyor, A4 formatdagi PDF generatsiyasi.
6. `backend/app/reporting/excel_generator.py`: OpenPyXL asosidagi 8 varaqli, to'liq formatlangan Excel moliyaviy modeli eksporti (formula inyeksiyasidan himoyalangan).
7. `backend/app/reporting/report_repository.py`: Generatsiya qilingan hisobotlar tarixi, xesh va fayl ombori.
8. `backend/app/api/routes_reports.py`: Yangilangan va kengaytirilgan REST API endpointlari (`/profile`, `/validate`, `/preview`, `/generate`, `/download/pdf`, `/download/xlsx`, `/history`).
9. `frontend/src/app/credit-report/page.tsx`: Foydalanuvchi kredit profili shakli, hujjatlar nazorat ro'yxati, dosye ko'rinishi va real yuklab olish tugmalari.

## 4. Xavflar va Ehtiyot Choralari
- **Moliya ma'lumotlari izchilligi (Data Consistency):** Dashboard, PDF va Excel barcha joyda aynan bir xil yakuniy raqamlarni ko'rsatishi shart. Hech qanday hisob-kitob PDF yoki Excel shablonlari ichida mustaqil bajarilmaydi; yagona `CreditDossierData` orqali ta'minlanadi.
- **Formula inyeksiyasi (Spreadsheet Injection):** Foydalanuvchi kiritgan matnlarda `=, +, -, @` belgilari bo'lsa, Excel formulasi sifatida bajarilishiga yo'l qo'yilmaydi.
- **Maxfiylik va Regulyator Kafolatlari:** Hisobot rasmiy bank ma'qullashi yoki litsenziyalangan auditorlik xulosasi emasligi, balki taqdim etilgan ma'lumotlar asosidagi tahliliy dosye ekanligi qat'iy ko'rsatiladi.
