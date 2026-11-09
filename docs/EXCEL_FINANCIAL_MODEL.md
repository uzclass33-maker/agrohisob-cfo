# AGROHISOB CFO — EXCEL MOLIYAVIY MODEL SPETSIFIKATSIYASI (ASSIGNMENT 5)

## 1. Kirish
AgroHisob CFO platformasi korporativ moliya mutaxassislari, bank anderrayterlari va agrobiznes rahbarlari mustaqil o'rganishi va tahlil qilishi uchun `openpyxl 3.1.5` asosida professional 8 varaqli Excel (`.xlsx`) moliyaviy modelini shakllantiradi.

---

## 2. Ishchi Varaqlar (Worksheets) Standarti (8 Varaq)

1. **`Ijroiya Xulosa`:**
   - Korxona profili, so'ralayotgan kredit parametrlari.
   - Kreditga tayyorgarlik reytingi (0-100), hujjatlar to'liqligi.
   - 12 oylik umumiy kassa, sof oqim va birlashgan DSCR indikatorlari.
   - Muzlatilgan sarlavha: `A5`.
2. **`Tarixiy Kassa Oqimlari`:**
   - 12 oylik haqiqiy kassa oqimlari (Boshlang'ich qoldiq, Yalpi tushumlar, Chiqimlar, Sof pul oqimi, Yakuniy qoldiq).
   - Muzlatilgan sarlavha: `A3`.
3. **`Prognoz Farazlari`:**
   - Agrotexnik ekinlar, ekish maydoni, kutilayotgan hosildorlik, shartnoma narxlari, hosil va sotuv oylari.
   - Opex chiqimlar me'yori (o'g'it, yoqilg'i, ish haqi, soliqlar).
4. **`12 Oylik Prognoz`:**
   - Oyma-oy batafsil kassa balansi (Prognoz tushum, Opex chiqim, Qarz xizmati, Jami chiqim, Sof oqim, Yakuniy balans, CFADS, Oylik DSCR).
   - Kassa uzilishlari indikatori.
5. **`Kredit Grafigi`:**
   - So'ralayotgan kredit bo'yicha to'liq amortizatsiya jadvali.
   - Boshlang'ich qarz, asosiy qarz to'lovi, foiz to'lovi, jami to'lov, qoldiq asosiy qarz.
6. **`DSCR Tahlili`:**
   - CFADS ning mavjud qarzga va birlashtirilgan yangi qarzga nisbati.
   - Bank standart mezonlari bo'yicha baho (A'lo >= 1.6x, Barqaror >= 1.25x).
7. **`Ssenariylar Tahlili`:**
   - Bazaviy, Optimistik va Pessimistik holatlardagi tushum, chiqim, kassa farqi va to'lov qobiliyati ta'siri.
8. **`Manbalar va Metodologiya`:**
   - Dvigatel versiyasi (5.0.0), kassa hisobi standarti, hisoblash sanasi, rasmiy ogohlantirish matni.

---

## 3. Formatlash va Xavfsizlik Qoidalari
1. **UZS Raqam Formati:**
   - Barcha milliy valyutadagi kataklar `#,#0 "so'm"` formati bilan formatlangan. Foizlar esa `0.0"%"`.
2. **Katak Kengliklarini Avtomatik Moslash (Auto-fit):**
   - Har bir varaqdagi matn uzunligiga qarab ustun kengliklari avtomatik ravishda moslashtiriladi (`auto_fit_columns`).
3. **Formula In'eksiyasidan Himoya (Formula Injection Sanitization):**
   - Agar katakka yozilayotgan matn `=`, `+`, `-`, yoki `@` bilan boshlansa, Excel uni formula deb noto'g'ri ijro etmasligi va xavfsizlik buzilishiga yo'l qo'ymaslik uchun boshiga `'` belgisi qo'yiladi (`_sanitize_cell_text`).
4. **Muzlatilgan Sarlavhalar (Freeze Panes):**
   - Katta jadvallar varaqlanganda sarlavha ko'rinib turishi ta'minlangan.
