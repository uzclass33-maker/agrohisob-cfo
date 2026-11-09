# AGROHISOB CFO — SMART DATA IMPORT & CLASSIFICATION ARCHITECTURE

**Hujjat kodi:** `DOC-AGRO-A3-ARCH-001`  
**Holati:** TASDIQLANGAN (APPROVED)  
**Versiya:** 1.0.0  
**Mualliflar:** Principal FinTech Software Architect & Data Engineering Team  

---

## 1. TIZIM KONSEPSIYASI VA MAQSADI

AgroHisob CFO platformasining **Smart Financial Data Import System** (Aqlli moliyaviy ma'lumotlar import tizimi) O'zbekiston agrar korxonalari, fermer xo'jaliklari va agrosanoat klasterlarining heterogen buxgalteriya ma'lumotlarini (Soliq.uz E-fakturalari, bank hisobvaraqlarining ko'chirmalari, 1C eksportlari) xavfsiz qabul qilish, tozalash, avtomatlashtirilgan tarzda toifalash va moliya dvigateliga kiritish uchun ishlab chiqilgan.

Tizim quyidagi fundamental talablarga javob beradi:
1. **Deterministik va Shaffof Tahlil:** Moliyaviy va soliq sirlarini o'z ichiga olgan ma'lumotlar tashqi uchinchi tomon LLM APIlariga yuborilmaydi; tahlil to'liq platformaning o'zida qat'iy matematik va klassifikatsion qoidalar asosida bajariladi.
2. **Qat'iy Buxgalteriya Izolyatsiyasi (Ledger Separation):** Invoys reestri (E-faktura majburiyatlari) va Kassa reestri (Real bank pul oqimlari) bir-biridan mustaqil yuritiladi. Invoys mavjudligi bank kassa balansini oshirib ko'rsatishiga yo'l qo'yilmaydi.
3. **Ko'p Tilli va Lokal Moslashuvchanlik:** O'zbek lotin, o'zbek kirill va rus tillaridagi ustun sarlavhalari hamda to'lov maqsadlarini bir xilda aniq taniydi.
4. **Kriptografik Takrorlanishdan Himoya:** Har bir fayl SHA-256 xesh summasi va har bir tranzaksiya kanonik barmoq izi (fingerprint) bilan ikki bosqichli dublikat nazoratidan o'tadi.

---

## 2. DASTURIY ARXITEKTURA VA QUVUR TUZILISHI (PIPELINE)

Import arxitekturasi quyidagi qatlamlardan iborat:

```
[Mijoz / Brauzer (.csv, .xlsx)]
           │
           ▼
[1. FileValidator] ───► Hajm (<10MB), Magic Bytes, Kengaytma, VBA Makros Tekshiruvi
           │
           ▼
[2. DuplicateDetector (File)] ───► SHA-256 xesh bo'yicha takroriy fayllarni aniqlash
           │
           ▼
[3. SpreadsheetParser] ───► openpyxl (data_only) / CSV Sniffer, formula inyeksiyasidan tozalash
           │
           ▼
[4. ColumnMapper] ───► Ko'p tilli sinonimlar lug'ati (Sana, Summa, Kontragent, MXIK, h.k.)
           │
           ▼
[5. Normalizer] ───► O'zbek raqam formatlari (1 250 000,50 -> Decimal), Sanalar, INN/STIR
           │
           ▼
[6. TransactionValidator] ───► Yo'nalish (Debet/Kredit), musbat summa, QQS balansi tekshiruvi
           │
           ▼
[7. Classifier (3-Tier)] ───► Tier 1 (MXIK) -> Tier 2 (Kalit so'z) -> Tier 3 (Kontragent)
           │
           ▼
[8. DuplicateDetector (Row)] ───► Qator barmoq izi (SHA-256) bo'yicha takroriy tranzaksiyalar
           │
           ▼
[9. Interactive Staging Preview] ───► Foydalanuvchi ko'rib chiqishi va toifalarni o'zgartirishi
           │
           ▼
[10. Reconciliation & Ledgers] ───► E-FAKTURA -> Invoice Ledger | BANK -> Cash Ledger & DSCR
```

---

## 3. MODUL CHEGARALARI VA VAZIFALARI

1. **`app.import_engine.file_validator`:**
   - Fayl kengaytmalari (`.csv`, `.xlsx`) va o'lchamini (maksimal 10 MB) tekshirish.
   - Excel ZIP konteynerlarida zararli VBA makroslari (`vbaProject.bin`) mavjudligini aniqlash va bloklash.
   - Matn kodlashini aniqlash (`UTF-8`, `UTF-8-BOM`, `CP1251`, `Windows-1251`).
2. **`app.import_engine.spreadsheet_parser`:**
   - CSV delimiter sniffing (nuqta-vergul `;`, vergul `,`, tab `\t`).
   - Excel fayllarini faqat hisoblangan qiymatlar rejimida (`data_only=True`) ochish.
   - Katakchalar boshidagi xavfli belgilarni zararsizlantirish (formula inyeksiyasini bartaraf etish).
3. **`app.import_engine.column_mapper`:**
   - O'zbekiston moliyaviy amaliyotidagi 12 ta tizimli ustun bo'yicha 100 dan ortiq sinonimlarni o'z ichiga olgan lug'at.
   - 60% dan yuqori ishonchlilik ko'rsatkichiga ega ustunlarni avtomatik biriktirish.
4. **`app.import_engine.normalizer`:**
   - Mahalliy raqam formatlarini (`1 250 000,50 so'm`, `(50 000.00)`, `-`) `Decimal(0.01)` formatiga o'tkazish.
   - ISO, CIS (DD.MM.YYYY) va Excel seriya raqamli (masalan, 45350) sanalarni `datetime.date` obyektiga aylantirish.
   - O'zbekistonning 9 xonali STIR/INN raqamlarini tozalash va tekshirish.
5. **`app.import_engine.classifier`:**
   - Davlat Soliq Qo'mitasining MXIK kodlari prefikslari (01.11, 01.16, 20.15, 19.20 va h.k.) bo'yicha 95-98% ishonchlilikdagi 1-bosqich tasniflash.
   - To'lov maqsadi matnidagi kalit so'zlar bo'yicha 2-bosqich tahlil.
   - Yirik monopolistlar va ta'minotchilar bo'yicha 3-bosqich tahlil.
6. **`app.import_engine.reconciliation`:**
   - Invoyslar reestri va Bank kassa reestri o'rtasidagi qat'iy chegarani himoya qilish.
   - Ochiq hisobvaraq-fakturalarni to'langan bank o'tkazmalari bilan INN, summa va sanalar bo'yicha avtomatik o'zaro bog'lash (reconciliation).
7. **`app.import_engine.import_service`:**
   - Fasad servis; sessiyalarni boshqaradi, oraliq qoralama (staging) holatini saqlaydi, foydalanuvchi tahrirlarini qabul qiladi va ma'lumotlarni moliya dvigateliga muvofiqlashtiradi.
