# AGROHISOB CFO — ASSIGNMENT 8 QAYTA VERIFIKATSIYA VA AUDIT HISOBOTI (FINAL REPORT)

**Loyiha:** AgroHisob CFO (B2B SaaS / AgriFinTech)  
**Topshiriq:** Assignment 8 — Pilot Validatsiyasi, Mijozlar Tadqiqoti, Bozor, Xavfsizlik Hardening va AgroVentures Tayyorgarligi  
**Sana:** 2026-yil 9-noyabr  
**Auditorlar guruhi:** Principal Software Architect, Staff Full-Stack Engineer, FinTech Xavfsizlik Auditori, Moliyaviy Modellashtirish Mutaxassisi  
**Holat:** **VERIFIKATSIYA QILINGAN VA XAVFSIZLIK KUCHAYTIRILGAN (175/175 TEST PASSED)**

---

## 1. DASTLABKI LOYIHA HOLATI (INITIAL PROJECT STATUS)

Assignment 8 ning birinchi iteratsiyasida dasturiy kod bazasida 159 ta test mavjud bo'lib, tadqiqot va analitika panellari qo'shilgan edi. Biroq mustaqil FinTech xavfsizlik va moliyaviy audit quyidagi muhim nomuvofiqliklarni aniqladi:
1. API yo'nalishlarida server sathi autentifikatsiyasi yo'q edi, mijoz yuborgan `organization_id` ga ishonilgan.
2. Pilot boshqaruv panelida DB RLS sinovdan o'tmagan bo'lsa-da, `ISOLATED_SANDBOX_ENFORCED` statusi ko'rsatilgan.
3. PQ-47 va PF-82 davlat subsidiyalari formulalarida qonunchilik bandlariga to'liq mos kelmaydigan taxminlar mavjud edi.
4. Moliyaviy dvigatelda qarz 0 bo'lganda DSCR uchun sun'iy 99.99x qaytarilgan.
5. PII sanitizatsiyasi faqat kalit nomlarini tekshirgan, erkin matndagi raqamlar tozalanmagan.
6. Bozor tadqiqotida YAIM ulushi rasmiy 18.9% o'rniga 24-25% deb yozilgan.
7. Vercel ishlab chiqarish platformasida yangi `/pilot-dashboard` sahifasi HTTP 404 qaytargan.

---

## 2. AMALGA OSHIRILGAN ASOSIY TUZATISHLAR (KEY REMEDIATIONS)

### 1. P0 — API Autentifikatsiyasi va Tashkilotlararo Izolyatsiya (Auth & Tenant Isolation)
- `backend/app/auth/` arxitekturasi yaratildi: `models.py`, `security.py`, `dependencies.py`.
- HS256 kriptografik JWT tekshiruvi server sathida joriy etildi.
- Barcha himoyalangan yo'nalishlar (`/api/v1/imports/**`, `/api/v1/reports/**`, `/api/v1/dashboard/**`, `/api/v1/research/**`, `/api/v1/analytics/**`) autentifikatsiya qilindi.
- Tokensiz yoki soxta tokenli so'rovlar qat'iy **HTTP 401 Unauthorized** bilan to'xtatiladi.
- Client yuborgan `organization_id` tasdiqlangan foydalanuvchi sessiyasiga qarshi tekshiriladi; begona tashkilot ma'lumotlariga so'rov darhol **HTTP 403 Forbidden** qaytaradi.
- Xom tadqiqotlar (`/research/**`) faqat Admin/Researcher ga, xom telemetriya (`/analytics/events`) faqat Super Admin ga ruxsat etildi; umumiy foydalanuvchilarga faqat agregatsiyalangan xavfsiz summary beriladi.

### 2. Pilot Boshqaruv Panelidagi Xavfsizlik Statusi
- `backend/app/pilot/service.py` faylida sun'iy `ISOLATED_SANDBOX_ENFORCED` statusi olib tashlandi.
- Haqiqiy holatga mos **`APP_RBAC_ACTIVE_DB_RLS_NOT_VERIFIED`** statusi va **`PILOT_RECRUITMENT_CONDITIONAL_PENDING_SECURITY_VERIFICATION`** tayyorgarlik darajasi o'rnatildi.
- Frontendda ("RBAC FAOL (RLS KUTILMOQDA) — Ilova sathi himoyalangan, DB RLS kutilmoqda") haqqoniy ko'rinishga keltirildi.
- Har doim bitta haqiqat ko'rsatiladi: **0 ta intervyu, 0 ta real pilot, 0 ta to'lovchi mijoz, $0 tushum**.

### 3. Rasmiy Qonunchilikka (PQ-47 va PF-82) To'liq Moslashtirish
- **PQ-47 (lex.uz/uz/acts/-8036872, 05.02.2026):**
  - Suv taqchil hududlar (Qoraqalpog'iston, Xorazm, Navoiy, Buxoro) uchun mintaqaviy koeffitsiyent rasmiy **1.25x** etib belgilandi (ilgari 1.2 xato edi).
  - Mevali bog' bazaviy subsidiyasi **11,000,000 so'm/ga** ga to'g'rilandi (ilgari 10 mln edi).
  - 50/50 bosqichli to'lov qonuniy me'yor emas, balki "shartli monitoring modeli (taxminiy)" ekanligi qat'iy ko'rsatildi.
- **PF-82 (lex.uz/uz/acts/-8187068, 08.05.2026):**
  - O'zboshimchalik bilan olingan 10% bekor qilindi.
  - Rasmiy tabaqalashtirilgan stavkalar joriy etildi: shartnomaviy muddatida qaytarilgan kreditlar uchun **2.5 foiz bandi**, hosil yilining 31-dekabriga qadar to'liq qaytarilgan kreditlar uchun **5.0 foiz bandi**.
  - Muddati o'tgan qarzdorlik bo'lsa kompensatsiya berilmasligi va qoplama faqat paxta hamda bug'doy uchun amal qilishi tekshirildi.

### 4. Moliyaviy Formulalar Standarti
- DSCR ta'rifi: $CFADS / Debt\ Service$, bu yerda $CFADS = Operating\ Inflows - Operating\ Outflows$. Operatsion chiqimlardan qarz to'lovi chiqarib tashlanib, ikki karra ayirish xatosi bartaraf etildi.
- Agar umumiy qarz to'lovi 0 bo'lsa, sun'iy 99.99x emas, **`None`** va rating **`NO_DEBT`** qaytariladi.
- 1.25 chegarasi mutlaq xalqaro norma emas, balki sozlanadigan mezon modeli sifatida belgilandi.

### 5. Analitika Ma'lumotlarini Tozalash va Chegaralash
- Erkin matndagi STIR (9 ta raqam), JSHSHIR (14 ta raqam), bank hisobi (20 ta raqam), to'lov kartasi (16 ta raqam), telefon va email manzillarini chuqur tozalash uchun regex filtrlar qo'shildi.
- Ruxsat etilgan maydonlar bo'yicha qat'iy oq ro'yxat (allowlist) joriy etildi.
- "Zero-PII" va'dasi o'rniga real cheklov belgilandi: "Ruxsat etilgan event maydonlari bilan cheklangan; qoldiq xavf mavjud".
- Analitika telemetriyasi 30 kunlik saqlash muddati bilan cheklandi.

### 6. Bozor Tadqiqoti va Dalillar Registri Tozalanishi
- `docs/MARKET_RESEARCH.md` da qishloq xo'jaligining YaIMdagi ulushi rasmiy Stat.uz manbasi (2025-yil yakuni) bo'yicha **18.9%** ga to'g'rilandi (24-25% taxminlar bekor qilindi).
- `docs/TAM_SAM_SOM_MODEL.md` da takroriy hisoblashlar tozalandi ($64.8M TAM, $18.4M SAM, $1.23M SOM).
- Slaydlar bo'yicha: 10 ta slayd kontenti tayyor, biroq Canva/PDF grafik dizayn fayli hali vizuallashtirilmaganligi ochiq qayd etildi.

---

## 3. AMALDAGI ISHCHI MVP IMKONIYATLARI

1. **12 oylik mavsumiy pul oqimi (Cash Flow):** Agrar ekinlar va yig'im-terim davrlariga mos kassa uzilishlarini modellashtirish.
2. **Qarz qoplash koeffitsienti (DSCR):** Agrobank andozasidagi qat'iy matematik formulalar bo'yicha qarz to'lash qobiliyati (qarz 0 bo'lganda None).
3. **Kredit amortizatsiyasi:** Mavsumiy va differensial to'lov jadvallari, imtiyozli davr hisobi.
4. **Stress-test tahlili:** Hosil kamayishi (-15%) va narx tushishi (-20%) bo'yicha likvidlik taqsimoti.
5. **Buxgalteriya importi:** 1C va Didox (XLSX, XLS, CSV) ko'chirmalarini avtomatik ajratish, normalizatsiya va PII himoyasi.
6. **Hisobotlar eksporti:** 1 bosishda rasmiy 6 sahifalik PDF Kredit Dossieri va dinamik Excel Moliyaviy Modelini yuklab olish.
7. **O'zbekiston qonunchiligi:** VMQ-613 (yer ijara huquqi baholash) va PQ-47/PF-82 (davlat subsidiyalari) integratsiyasi.
8. **Bulutda jonli ishlash:** Vercel frontend (`https://agrohisob-cfo.vercel.app`) va Render backend (`https://agrohisob-backend.onrender.com`).

---

## 4. O'TKAZILGAN TESTLAR VA ISBOTLAR (VERIFICATION EVIDENCE)

- **Backend sinovlari:** `pytest backend/tests/` buyrug'i orqali **175 ta testning barchasi (100%) muvaffaqiyatli o'tdi** (`10.00s`).
  - Yangi xavfsizlik testi: `backend/tests/test_auth_and_tenant_isolation.py` (8/8 PASSED).
  - Subsidiyalar qonuniylik testlari: `test_subsidies_pq47.py` (4/4 PASSED), `test_subsidies_pf82.py` (4/4 PASSED), `test_collateral_subsidies_api.py` (6/6 PASSED).
- **Frontend sinovlari:** `pnpm build` buyrug'i orqali **12 ta statik sahifaning barchasi xatosiz kompilyatsiya qilindi**.
- **Jonli ishlab chiqarish holati:** Vercel platformasida asosiy yo'nalishlar (`/`, `/demo`, `/dashboard`, `/credit-report`, `/data-import`, `/collateral-subsidies`, `/scenario-analysis`) HTTP 200 OK. Yangi `/pilot-dashboard` sahifasi esa lokalda (HTTP 200) ishlab turibdi; foydalanuvchining qat'iy cheklovlari (no deploy, no git push) tufayli prodga chiqarilmagan va jonli serverda HTTP 404 qaytarmoqda.

---

## 5. YECHILMAGAN TO'SIQLAR VA CHEKLOVLAR (UNRESOLVED BLOCKERS)

1. **Vercel Prod Deployment (404 marshrut):** Foydalanuvchining "Ishlab chiqarish deploymentini amalga oshirma, GitHub’ga push qilma" ko'rsatmasi sababli oxirgi kodlar (commit `7e27bd9` va joriy o'zgarishlar) prodga yuborilmadi. Ushbu to'siq faqat foydalanuvchi roziligi bilan `git push` amalga oshirilgandan so'ng avtomatik yechiladi.
2. **PostgreSQL RLS Migratsiyasi:** Local faylli saqlash testlar uchun vaqtinchalik izolyatsiya qilingan, ammo ishlab chiqarish muhitida to'liq DB Row Level Security va Persistent Storage ta'minlanmaguncha saqlash tayyorgarligi **BLOCKED** hisoblanadi.
3. **Birlamchi Mijoz Dalillari:** Haqiqiy fermerlar bilan intervyular hozircha 0 ta. Mom Test metodologiyasi bo'yicha suhbatlar o'tkazish rejalashtirilgan.

---

## 6. YAKUNIY QABUL QILISH VA GO / NO-GO XULOSASI

| Yo'nalish | Qaror | Aniq Asos va Cheklov |
|---|---|---|
| **Sintetik Demo va Arxitektura Taqdimoti** | **GO (RUXSAT ETILADI)** | Tizim 175 ta avtomatik test bilan to'liq himoyalangan, sintetik profillar to'liq ishchi va moliyaviy formulalar bank talablariga mos. Mahsulot arxitekturasini demonstratsiya qilishga to'liq tayyor. |
| **Real Moliyaviy Ma'lumotlar Bilan Pilot** | **CONDITIONAL / NO-GO** | PostgreSQL RLS to'liq sinovdan o'tkazilmaguncha va mustaqil tashqi xavfsizlik auditi yakunlanmaguncha real mijozlarning haqiqiy hisob-faktura yoki bank sirlarini tizimga yuklash taqiqlanadi (faqat depersonalizatsiya qilingan ma'lumotlar bilan sinash mumkin). |
| **Investorlar Oldida Rasmiy Pitch** | **CONDITIONAL (SHARTLI GO)** | Taqdimot matni 100% fakt-chekingdan o'tgan ($0 daromad, 0 ta mijoz, 18.9% YAIM ulushi). Ammo investorlarga chiqishdan oldin Canva/PDF grafik dizaynini tayyorlash va 404 prod marshrutini yangilash zarur. |
