# AGROHISOB CFO — TOPSHIRIQ 3 OLDIDAN DASTLABKI AUDIT VA TIZIMLI TAHLIL

**Hujjat ID:** `DOC-AGRO-A3-AUDIT-001`  
**Sana:** 2026-yil 9-noyabr  
**Holat:** TASDIQLANGAN (APPROVED)  
**Muallif:** AgroHisob CFO Principal FinTech Software Architect & Data Engineering Team  

---

## 1. KIRISH VA AUDIT MAQSADI

Ushbu audit hujjati **AgroHisob CFO** platformasining 3-topshirig'i — **"Smart Financial Data Import, Validation, Classification & Financial Engine Integration"** (Aqlli moliyaviy ma'lumotlar importi, validatsiya, avtomatik toifalash va moliya dvigateli integratsiyasi) arxitekturasini ishlab chiqishdan oldingi mavjud kod bazasi, infratuzilma va hisob-kitob dvigatelining tayyorgarlik holatini to'liq tekshirish natijalarini jamlaydi.

Audit maqsadi:
1. 1- va 2-topshiriqlarda yaratilgan moliyaviy hisob-kitob dvigateli (`backend/app/financial_engine/`) bilan yangi import tizimining o'zaro bog'liqligini aniqlash;
2. O'zbekiston agrar korxonalari va fermer xo'jaliklarining real buxgalteriya amaliyotini (Soliq.uz E-faktura, 1C eksporti, bank ko'chirmalari) tahlil qilish;
3. Buxgalteriyaning fundamental tamoyili — **Invoys reestri (Majburiyatlar)** va **Bank kassa reestri (Real naqd pul oqimi)** o'rtasidagi qat'iy chegarani (Ledger Separation) ta'minlash choralarini belgilash;
4. Xavfsiz, deterministik va yuqori samaradorlikka ega ma'lumotlar quvuri (Data Pipeline) arxitekturasini loyihalashtirish.

---

## 2. MAVJUD TIZIM HOLATI VA TEST NATIJALARI

Oldingi topshiriqlarda amalga oshirilgan barcha modullar to'liq auditdan o'tkazildi:
- **Pytest sinovlari:** 60/60 testlar muvaffaqiyatli o'tmoqda (`100% pass`).
- **Backend xizmati:** FastAPI (`http://127.0.0.1:8000`) barqaror holatda ishlab turibdi.
- **Frontend xizmati:** Next.js 14 SSR (`http://localhost:3000`) barcha yo'nalishlar bo'yicha ishlab turibdi.
- **Mavjud ma'lumotlar bazasi va modellar:** `Scenario`, `FinancialEngineInput`, `MonthlyFinancialMetrics`, `LoanScheduleRequest`, `DSCRBenchmark` to'liq Pydantic v2 va SQLAlchemy modellariga ega.

---

## 3. IDENTIFIKATSIYA QILINGAN TALABLAR VA AGRO-FINTECH TALABLARI

### 3.1. Hujjatlar oilasi va formatlar
O'zbekiston agrar sektorida 2 ta asosiy birlamchi moliyaviy manba mavjud:
1. **Soliq E-Faktura (Elektron hisobvaraq-faktura):**
   - Formatlar: `.xlsx`, `.csv`.
   - O'z ichiga oladi: Faktura raqami va sanasi, Yetkazib beruvchi (INN/STIR, nomi), Xaridor (INN/STIR, nomi), MXIK (IKPU) tovar/xizmat kodi (17 xonali yoki nuqtali format), Tovar nomi, O'lchov birligi, Miqdor, Narx, Yetkazib berish qiymati, QQS stavkasi va summasi, Jami qiymat.
   - **Buxgalteriya qoidasi:** Fakturaning mavjudligi korxona hisob raqamida pul ko'payganini yoki kamayganini anglatmaydi. Bu xaridor yoki sotuvchining majburiyatidir (Debitorlik/Kreditorlik).
2. **Bank hisobvaraqlari ko'chirmasi (Bank Statement):**
   - Formatlar: `.xlsx`, `.csv` (Agrobank, Xalq Banki, Ipak Yo'li, Kapitalbank va boshqalar).
   - O'z ichiga oladi: O'tkazma sanasi, Debet (Chiqim) / Kredit (Kirim), Kontragent nomi, Kontragent INN, Kontragent hisob raqami (20 xonali), To'lov maqsadi (Назначение платежа).
   - **Buxgalteriya qoidasi:** Bank ko'chirmasidagi har bir tasdiqlangan tranzaksiya korxonaning kassa/bank qoldig'iga to'g'ridan-to'g'ri ta'sir qiladi va Cash Flow (pul oqimlari) reestriga yoziladi.

### 3.2. MXIK (IKPU) va Semantik toifalash zarurati
Fermerlar hisob-kitoblarida to'lov maqsadi ko'pincha erkin matnda yoziladi ("o'g'it uchun to'lov", "solyarka", "paxta xomashyosi avansi").
Shu sababli tizim 3 bosqichli deterministik klassifikatsiyaga ega bo'lishi shart:
1. **1-bosqich: MXIK (IKPU) kodi bo'yicha qat'iy xaritalash:** O'zbekiston Soliq qo'mitasi klassifikatoridagi agro kodlar (01.11, 01.16, 20.15, 19.20 va h.k.).
2. **2-bosqich: Kalit so'zlar va regex qoidalari (O'zbek lotin, kirill, rus):** Matn semantikasi bo'yicha qishloq xo'jaligi xarajat/daromad moddalariga ajratish.
3. **3-bosqich: Kontragent profili bo'yicha toifalash:** Maxsus ta'minotchilar (Farg'onaAzot, NavoiyAzot, YoQSh, MTP, suv ta'minoti va banklar).

---

## 4. YANGI IMPORT ENGINE ARXITEKTURASI

Quyidagi yangi paket to'liq ajratilgan holda yaratiladi:
`backend/app/import_engine/`
- `exceptions.py` — barcha ixtisoslashgan xatolik turlari.
- `schemas.py` — Pydantic v2 sxemalari, hujjat turlari, qator holatlari va javob modellari.
- `file_validator.py` — xavfsizlik, hajm, kengaytma, bayt imzosi va kodlashni tekshirish.
- `spreadsheet_parser.py` — CSV va XLSX fayllarni formula inyeksiyalarisiz xavfsiz o'qish.
- `column_mapper.py` — ko'p tilli sinonimlar lug'ati va ustunlarni avtomatik aniqlash.
- `normalizer.py` — o'zbek/rus raqam formatlari (`1 250 000,00`) va sanalarni standartlashtirish.
- `transaction_validator.py` — har bir qatorning yaxlitligi, INN va yo'nalish tekshiruvi.
- `duplicate_detector.py` — SHA-256 fayl va qator barmoq izi (fingerprint) orqali takrorlanishlarni aniqlash.
- `classification_rules.py` va `classifier.py` — 3 bosqichli deterministik toifalash.
- `reconciliation.py` — Invoys va Bank reestrlari ajratilishi va o'zaro solishtiruvi.
- `import_service.py` — barcha jarayonlarni boshqaruvchi fasad servis.

---

## 5. XULOSA VA KEYINGI BOSQICHLAR

Barcha zaruriy infratuzilma tayyor. Ushbu audit xulosasiga binoan, modul-ma-modul amalga oshirish, har bir modulni qat'iy birlik (unit) testlar bilan qoplash va Next.js interfeysi bilan to'liq integratsiya qilish tasdiqlandi.
