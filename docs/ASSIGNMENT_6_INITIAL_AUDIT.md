# AGROHISOB CFO — TOPSHIRIQ 6 DASTLABKI AUDITI (ASSIGNMENT 6 INITIAL AUDIT)

## 1. Audit Maqsadi va Ko'lami
Ushbu audit AgroHisob CFO loyihasining **6-topshirig'i** («Qishloq xo'jaligi yer ijarasi garovi intellekti, subsidiya huquqi, indikativ baholash va me'yoriy moliyaviy tahlil») bo'yicha ishlab chiqishdan oldingi texnik, me'yoriy va moliyaviy holatni mustaqil baholash uchun o'tkazildi.

---

## 2. Mavjud Tizim va Resurslar Holati (Assignments 1–5 Verification)

| Modul / Komponent | Holati | Sinovdan O'tganligi | Reusability (Qayta foydalanish) |
| :--- | :--- | :--- | :--- |
| **Financial Engine (v5.0.0)** | Barqaror | 15 ta test PASSED | Kassa balansi, amortizatsiya, DSCR va ssenariylar dvigateli to'liq ishchi holatda |
| **Smart Import Engine** | Barqaror | 25 ta test PASSED | 12 oylik bank ko'chirmalari, Soliq e-fakturalari, rekonsiliatsiya va buxgalteriya registri |
| **AI-CFO Dashboard** | Barqaror | 18 ta test PASSED | 5 ta KPI kartasi, oylik kassa grafiklari, qarz tahlili va deterministik risk monitori |
| **Credit Dossier & Reports** | Barqaror | 15 ta test PASSED | Kanonik `CreditDossierData` shartnomasi, ReportLab PDF generatori, 8 varaqli Excel modeli |
| **FastAPI Backend** | Faol | HTTP 200 OK | `http://127.0.0.1:8000` da uvicorn daemon ishlamoqda |
| **Next.js Frontend** | Faol | HTTP 200 OK | `http://localhost:3000` da production build ishlamoqda |
| **Umumiy Test Qamrovi** | 124 / 124 PASSED | 100% Yashil | Regressiyasiz to'liq barqaror holat |

---

## 3. Topshiriq 6 Doirasida Talab Qilinuvchi Yangi Funksionallik

### MODULE A: Qishloq Xo'jaligi Yer Ijarasi Garovi Intellekti (Land Lease Collateral Intelligence)
1. **Yer ijarasi profili (Land Lease Profile):** Kadastr ma'lumotlari, yer maydoni (ga), ijara boshlanish/tugash sanasi, cheklovlar, garov va nizolar holati, so'ralayotgan kredit muddati.
2. **VMQ-613 Huquqiy Tayyorgarlik Dvigateli:**
   - Qat'iy taqvimiy sana arifmetikasi: Ijara muddati kredit so'ndirish sanasidan kamida 5 (besh) yil keyin tugashi shart (`Lease Expiration Date >= Loan Maturity Date + 5 years`).
   - Davlat ro'yxatidan o'tganlik, taqiqlar, ikkilamchi ijara (sub-lease) bo'yicha ruxsatnomalar tekshiruvi.
   - Skoring statuslari: `PRELIMINARY_CONDITIONS_MET`, `ADDITIONAL_VERIFICATION_REQUIRED`, `APPARENT_RESTRICTION_IDENTIFIED`, `INSUFFICIENT_INFORMATION`.
3. **Indikativ DCF Baholash Modeli (Indicative Financial Valuation):**
   - $PV = \sum \frac{CF_t}{(1 + r)^t}$ formulasi bo'yicha yer ijarasi huquqiga taalluqli sof iqtisodiy foydani diskontlash.
   - Hech qanday asossiz terminal qiymatsiz (ijara muddati bilan qat'iy cheklangan).
   - O'zgaruvchan diskont stavkalari (12% - 24%), tushum va opex farazlari.
   - Sezgirlik tahlili (Sensitivity Analysis: Bazaviy, Optimistik, Pessimistik).
   - Ixtiyoriy LTV (Loan-to-Value) illyustratsiyasi (60-70%), qat'iy ogohlantirish: *Ushbu baholash rasmiy mustaqil baholovchi hisoboti yoki bank kredit qarori emas, indikativ tahlildir*.
4. **Garov Hujjatlari Nazorat Ro'yxati (Collateral Document Checklist):**
   - Ijara shartnomasi, davlat ro'yxati guvohnomasi, kadastr pasporti, taqiq yo'qligi ma'lumotnomasi, mustaqil baholash hisoboti.

### MODULE B: Qishloq Xo'jaligi Subsidiyalari Intellekti (Agricultural Subsidy Intelligence)
1. **Versiyalangan Subsidiyalar Registri (`SubsidyProgram`):**
   - Dastur nomi, vakolatli organ, me'yoriy hujjat (`lex.uz` havolasi), amal qilish muddati, verifikatsiya holati (`VERIFIED`, `UNVERIFIED`).
2. **PQ-47 Suv Tejovchi Texnologiyalarni Qo'llab-quvvatlash Kalkulyatori:**
   - Tomchilatib, yomg'irlatib sug'orish.
   - Ekin turlari (paxta, sabzavot, meva/bog'lar, uzum) bo'yicha tabaqalashgan stavkalar (gektariga 6 mln dan 10 mln so'mgacha, hududiy koeffitsientlar).
   - Bosqichli to'lov (Phased disbursement): 50% dastlabki, 50% samaradorlik tasdiqlangach.
   - Imtiyozli kredit foiz stavkasi kompensatsiyasi (foiz punktlari hisobi).
3. **PF-82 Paxta va G'alla Moliyaviy Yordam Kalkulyatori:**
   - Intizomli to'lovchilar uchun foiz xarajatlarini davlat hisobidan kompensatsiya qilish qoidalari.
   - Qoldiq asosiy qarz va to'langan davrga qarab foiz bandi bo'yicha kompensatsiya hisobi.
4. **Subsidiya Muvofiqlik Dvigateli (Eligibility Engine):**
   - Statuslar: `POTENTIALLY_ELIGIBLE`, `NOT_ELIGIBLE_UNDER_VERIFIED_RULE`, `MORE_INFORMATION_REQUIRED`, `RULE_NOT_VERIFIED`, `OUTSIDE_EFFECTIVE_PERIOD`.
5. **Moliyaviy Dvigatel va Hisobotlar Integratsiyasi:**
   - Subsidiyalar avtomatik ravishda o'tgan davr kassa tushumiga aylanmaydi (qat'iy kassa ajratilishi).
   - Prognozlarda kutilayotgan shartli subsidiya sifatida alohida satrda aks etadi.
   - AI-CFO boshqaruv paneli va Kredit Dosyesiga indikativ subsidiya va garov tayyorgarligi bo'limlari kiritiladi.

---

## 4. Xavflar va Cheklovlar
1. **Me'yoriy Huquqiy Aniqlik:** Qonunchilik normalari `lex.uz` rasmiy portali bilan solishtirilib, faqat tasdiqlangan qoidalar kiritilishi shart. Noaniq hollarda "Qo'shimcha inson tekshiruvi talab etiladi" (Manual verification required) holati beriladi.
2. **Moliyaviy Integritet:** Yer ijara huquqi qiymati korxona umumiy qiymati yoki kelgusi hosil daromadi bilan aralashtirib yuborilmasligi shart.
3. **LTV va Garov Kafolati:** Avtomatlashtirilgan ko'rsatkichlar bank kredit kafolati deb da'vo qilinmasligi shart.

---

## 5. Amalga Oshirish Rejasi (Implementation Checklist)
- [x] Pre-implementation audit va me'yoriy manbalar tahlili (`docs/REGULATORY_SOURCE_REGISTER.md`, `docs/LEGAL_RULES_VERIFICATION.md`).
- [ ] Backend me'yoriy va qonunchilik registri (`backend/app/regulatory/`).
- [ ] Backend yer ijarasi garovi intellekti moduli (`backend/app/collateral/`).
- [ ] Backend subsidiyalar intellekti moduli (`backend/app/subsidies/`).
- [ ] SQLAlchemy ma'lumotlar bazasi modellari (`backend/app/models/collateral_subsidies.py`).
- [ ] REST API marshrutlari (`routes_collateral.py`, `routes_subsidies.py`, `routes_regulatory.py`).
- [ ] Financial Engine, Dashboard va Credit Dossier integratsiyasi.
- [ ] Frontend Next.js sahifalari va komponentlari (`frontend/src/app/collateral-subsidies/`).
- [ ] Avtomatlashtirilgan testlar (Unit, Regulatory, Financial DCF, API, E2E).
- [ ] Hujjatlashtirish va yakuniy audit hisoboti.
