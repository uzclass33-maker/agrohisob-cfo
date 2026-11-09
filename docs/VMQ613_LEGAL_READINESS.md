# VMQ-613 Huquqiy Tayyorgarlik Mezonlari va Qoidalar Tahlili

## 1. Huquqiy Asos va Manba
- **Hujjat:** O'zbekiston Respublikasi Vazirlar Mahkamasining 2025-yil 30-sentabrdagi 613-son qarori
- **Nomi:** «Qishloq xo'jaligiga mo'ljallangan yer uchastkalarini ijaraga berish huquqini kredit ta'minoti sifatida garovga qo'yish tartibi to'g'risida»
- **Rasmiy Lex.uz havolasi:** [https://lex.uz/uz/docs/-7750301](https://lex.uz/uz/docs/-7750301)
- **Kuchga kirish sanasi:** 2025-yil 30-sentabr
- **Status:** `VERIFIED_ACTIVE` (Rasmiy amalda)

---

## 2. Asosiy Qoidalar va Dasturiy Implementatsiya

### A. 5 Yillik Post-Kredit Bufer Qoidasi (8-band)
- **Qonun talabi:** Yer ijara shartnomasining qolgan muddati kreditni qaytarish muddatidan kamida 5 (besh) yil ko'p bo'lishi shart.
- **Dasturiy yechim (`eligibility.py`):**
  Oddiy `365 * 5` kun qo'shish usuli kalendar siljishlari va kabisa yillari tufayli xatolik keltirib chiqarishi mumkin. Shuning uchun `_add_years_calendar_aware(loan_maturity, 5)` funksiyasi joriy etildi:
  - Masalan, agar kredit muddati 2028-yil 1-martda tugasa, bufer talab sanasi: 2033-yil 1-mart.
  - Kabisa yili (29-fevral) holatida kabisa bo'lmagan yilning 28-fevraliga xavfsiz o'tkaziladi.
  - Agar `lease_expiration_date < buffer_required_date` bo'lsa, `is_eligible = False` belgilanadi va nuqson sifatida `defects` ro'yxatiga qayd etiladi.

### B. Davlat Ro'yxatidan O'tganlik Talabi (5-band)
- **Qonun talabi:** Yer uchastkasiga bo'lgan ijara huquqi Davlat kadastrlari palatasida belgilangan tartibda ro'yxatdan o'tkazilgan bo'lishi shart.
- **Dasturiy yechim:**
  `is_registered_in_cadastre` flagi va `registration_number` mavjudligi tekshiriladi. Ro'yxatdan o'tmagan bo'lsa, ariza rad etiladi yoki tekshiruvga yuboriladi.

### C. Taqiqlar, Arest va Sud Nizolari Yo'qligi (12-band)
- **Qonun talabi:** Yer uchastkasi bo'yicha taqiq (arest), xatlov, boshqa garov majburiyati, sud nizosi yoki ijara shartnomasini bekor qilish to'g'risida da'vo bo'lmasligi shart.
- **Dasturiy yechim:**
  `has_legal_restrictions`, `is_disputed`, va `is_terminated` parametrlari bo'yicha qat'iy mantiqiy filtratsiyani amalga oshiradi. Har qanday cheklov aniqlanganda `overall_status = APPARENT_RESTRICTION_IDENTIFIED` belgilanadi.

### D. Ikkilamchi Ijara (Sub-lease) Talabi (14-band)
- **Qonun talabi:** Ikkilamchi ijara (sub-lease) huquqi asosiy ijaraga beruvchi davlat organining (hokimlik / vazirlik) yozma ruxsatisiz garovga qo'yilishi mumkin emas.
- **Dasturiy yechim:**
  Agar `is_secondary_lease == True` bo'lsa, `has_sublease_authority_permission == True` bo'lishi shart. Aks holda `is_eligible = False` qaytariladi.

### E. Litsenziyali Mustaqil Baholash Talabi (15-band)
- **Qonun talabi:** Garovga qo'yiladigan yer ijara huquqining bozor qiymati qonunchilikda belgilangan tartibda litsenziyaga ega mustaqil baholovchi tashkilot tomonidan baholanadi.
- **Dasturiy yechim:**
  Platforma hisoblagan DCF qiymati faqat indikativ ko'rinishda ekanligi va bank kredit qo'mitasi mustaqil baholovchi hisobotini talab qilishi aniq ko'rsatiladi.

---

## 3. Screening Natijalari Matritsasi

| Tekshiruv Nomi | Normativ Asos | Muvaffaqiyatli Shart | Muvaffaqiyatsiz Holat Oqibati |
|---|---|---|---|
| 5 yillik bufer | VMQ-613, 8-band | `lease_exp >= loan_mat + 5 yil` | Rad etiladi (`is_eligible = False`) |
| Davlat ro'yxati | VMQ-613, 5-band | `is_registered == True` & `reg_no` mavjud | Hujjat talab etiladi |
| Taqiq va xatlov | VMQ-613, 12-band | `has_restrictions == False` | Rad etiladi |
| Sud nizosi | VMQ-613, 12-band | `is_disputed == False` | Rad etiladi |
| Sub-ijara roziligi | VMQ-613, 14-band | `has_sublease_perm == True` | Rad etiladi |
| Mustaqil baholash | VMQ-613, 15-band | `has_appraisal == True` | Shartli ruxsat (baholovchi talab) |
