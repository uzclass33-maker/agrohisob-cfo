# AGROHISOB CFO — TOPSHIRIQ 7 QABUL MEZONLARI VA TEST NATIJALARI (ACCEPTANCE CRITERIA MATRIX)

**Hujjat identifikatori:** `DOC-AH-A7-TR-01`  
**Versiya:** `1.0.0-mvp`  
**Sana:** 2026-11-09  
**Holat:** 100% TASDIQLANGAN (100% PASS)  
**Jami testlar soni:** 159 ta avtomatlashtirilgan test (19 ta test fayli)  

---

## 1. QABUL MEZONLARI MATRITSASI (AC-01 DAN AC-30 GACHA)

| AC ID | Qabul Mezoni Tavsifi | Tekshirish Usuli / Test | Natija |
| :---: | :--- | :--- | :---: |
| **AC-01** | 1–6-topshiriqlarning to'liq o'zaro integratsiyasi va yaxlitligi | Pytest to'liq to'plami (159 test) & E2E Journey | **PASS** |
| **AC-02** | FastAPI serverining xatosiz ishga tushishi va SQLite fallback mavjudligi | `test_live_fastapi_server_endpoints` | **PASS** |
| **AC-03** | Har bir HTTP javobida xavfsizlik sarlavhalari (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`) bo'lishi | `test_security_headers_middleware_applied` | **PASS** |
| **AC-04** | So'rov bajarilish vaqti `X-Process-Time` sarlavhasida soniyalarda qaytarilishi | `test_security_headers_middleware_applied` | **PASS** |
| **AC-05** | Tashqi muhitdan `ALLOWED_ORIGINS` / `CORS_ORIGINS` dinamik qabul qilinishi | `test_dynamic_cors_origins_parsing` | **PASS** |
| **AC-06** | Supabase/PostgreSQL ulanish satrini `postgresql+psycopg2://` ga avtomatik normallashishi | `test_postgresql_url_normalization` | **PASS** |
| **AC-07** | PostgreSQL uchun ulanish puli (`pool_pre_ping`, `pool_recycle`, timeout) sozlanishi | `test_postgresql_url_normalization` | **PASS** |
| **AC-08** | Ishlab chiqarish muhitida standart kalitlar ishlatilganda ogohlantirish berilishi | `test_production_security_validation_warning` | **PASS** |
| **AC-09** | Tashkilotlar o'rtasida ma'lumotlar izolatsiyasi (`organization_id` filtrlash) | `test_dashboard_overview_all_scenarios_consistency` | **PASS** |
| **AC-10** | CSV va Excel fayllarni yuklashda MIME-tur va xavfsizlik validatsiyasi (15MB limit) | `test_import_file_validation.py` (7 test) | **PASS** |
| **AC-11** | Eksport qilinayotgan Excel fayllarida formula inyeksiyasi (`=`, `+`, `-`, `@`) dan himoya | `test_excel_formula_injection_defense` | **PASS** |
| **AC-12** | Bir xil fayl va tranzaksiyalarni SHA-256 xesh orqali dublikat bo'lishini 100% oldini olish | `test_import_duplicates.py` | **PASS** |
| **AC-13** | Kassa oqimlari asosiy ayniyatining (`Yakuniy = Boshlang'ich + Oqimlar`) 1 tiyingacha mosligi | `test_dashboard_cashflow_roll_forward` | **PASS** |
| **AC-14** | DSCR hisoblashda nolga bo'linishdan himoya va bank standarti (1.25) taqqoslanishi | `test_engine_dscr.py` | **PASS** |
| **AC-15** | Yer ijarasi huquqi bo'yicha chekli muddatli DCF indikativ baholash | `test_dcf_valuation_finite_horizon_and_bonitet` | **PASS** |
| **AC-16** | Bonitet balli va likvidlik chegirmasini inobatga oluvchi sezgirlik tahlili | `test_collateral_sensitivity_analysis` | **PASS** |
| **AC-17** | PQ-47 bo'yicha tomchilatib sug'orishga 50% davlat subsidiyasi hisob-kitobi | `test_subsidies_pq47.py` | **PASS** |
| **AC-18** | PF-82 bo'yicha kredit foizining 10 foiz punktgacha kompensatsiyasi hisob-kitobi | `test_subsidies_pf82.py` | **PASS** |
| **AC-19** | Barcha garov va subsidiya hisobotlarida davlat litsenziyasiga ega emaslik ogohlantirishi | `test_pdf_generation.py` | **PASS** |
| **AC-20** | Ekranda, API da, PDF va Excelda sonli ko'rsatkichlarning 0% tafovut bilan mosligi | `test_financial_calculations.py` | **PASS** |
| **AC-21** | Kubernetes/Docker monitoringi uchun `/health` liveness probe mavjudligi | `test_health_and_readiness_endpoints_for_monitoring` | **PASS** |
| **AC-22** | Trafik qabul qilishga tayyorlik uchun `/ready` readiness probe mavjudligi | `test_health_and_readiness_endpoints_for_monitoring` | **PASS** |
| **AC-23** | Next.js 14 App Router production bundle xatosiz yig'ilishi (`next build`) | Next.js CLI Verification | **PASS** |
| **AC-24** | 3 ta sintetik korxona (Kichik fermer, Meva eksportchisi, Agro klaster) profillari | `test_scenarios.py` | **PASS** |
| **AC-25** | Vektorli rasmiy Bank Dosyesi PDF hisoboti yuklab olinishi | `test_pdf_generation.py` | **PASS** |
| **AC-26** | Har bir katagi jonli formulali Excel moliyaviy modeli yuklab olinishi | `test_excel_generation.py` | **PASS** |
| **AC-27** | GitHub Actions CI/CD to'liq quvuri (`.github/workflows/ci.yml`) yaratilishi | CI Workflow Audit | **PASS** |
| **AC-28** | Bulutli xosting (Vercel, Railway, Supabase) joylashtirish yo'riqnomasi | `docs/DEPLOYMENT_GUIDE.md` | **PASS** |
| **AC-29** | Favqulodda holatlar va SRE operatsion runbook ishlab chiqilishi | `docs/OPERATIONS_RUNBOOK.md` | **PASS** |
| **AC-30** | AgroVentures akseleratori uchun 3 daqiqalik pitch ssenariysi | `docs/AGROVENTURES_DEMO_SCRIPT.md` | **PASS** |

---

## 2. TEST STATISTIKASI VA QAMROV

- **Jami test fayllari soni:** 19 ta
- **Jami test holatlari:** 159 ta
- **O'tgan testlar soni:** 159 ta (100.0%)
- **Muvaffaqiyatsiz testlar:** 0 ta (0.0%)
- **O'rtacha bajarilish vaqti:** ~19.9 soniya
- **Status:** TIZIM 100% PRODUCTION VA ACCELERATOR DEMOSIGA TAYYOR (APPROVED FOR RELEASE).
