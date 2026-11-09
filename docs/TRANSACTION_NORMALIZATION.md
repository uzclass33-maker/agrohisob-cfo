# AGROHISOB CFO — TRANSACTION DATA NORMALIZATION ENGINE

**Hujjat kodi:** `DOC-AGRO-A3-NORM-004`  
**Holati:** TASDIQLANGAN (APPROVED)  
**Versiya:** 1.0.0  

---

## 1. MOLIYAVIY RAQAMLARNI NORMALIZATSIYA QILISH

O'zbekistonda moliyaviy dasturlarda raqamlar quyidagi ko'rinishlarda yoziladi:
- `1 250 000,50` (bo'shliq minglik ajratuvchi, vergul kasr)
- `1 250 000,50 so'm` yoki `1250000 сум` (valyuta suffiksi bilan)
- `1,250,000.50` (inglizcha standart: vergul minglik, nuqta kasr)
- `1.250.000,50` (yevropacha standart: nuqta minglik, vergul kasr)
- `(45 000,00)` (buxgalteriyada qavs ichidagi raqam manfiy chiqimni bildiradi)
- `-15 000.00` (standart manfiy son)

### 1.1. Normalizatsiya Algoritmi
1. Matndagi barcha ko'rinmas va tor bo'shliqlar (`\xa0`, `\u2000-\u200b`, `\u202f`) standart bo'shliqqa aylantiriladi.
2. Manfiylik tekshiriladi: qavs `(...)` yoki oldidagi minus `-` aniqlanib, flag o'rnatiladi.
3. Valyuta qo'shimchalari (`so'm`, `som`, `сум`, `uzs`, `usd`, `%`) o'chiriladi.
4. Barcha bo'shliqlar olib tashlanadi.
5. Bir vaqtda vergul va nuqta uchrasa, oxirgi belgining o'rni orqali kasr ajratuvchisi aniqlanadi.
6. Natija Python'ning `Decimal` sinfiga o'tkaziladi va `0.01` aniqlikda yaxlitlanadi (`ROUND_HALF_UP`).
7. Nol, bo'sh satr yoki chiziqcha (`"-"`, `""`, `None`) holatlarida mos ravishda `Decimal("0.00")` yoki `None` qaytariladi.

---

## 2. SANALARNI NORMALIZATSIYA QILISH

Sanalarni o'qishda quyidagi 3 toifa to'liq qamrab olingan:
1. **Standart matnli sanalar:**
   - ISO formati: `YYYY-MM-DD`, `YYYY/MM/DD`, `YYYY.MM.DD`
   - O'zbekiston/MDH formati: `DD.MM.YYYY`, `DD/MM/YYYY`, `DD-MM-YYYY`
   - Vaqt bilan kelgan formatlar: `DD.MM.YYYY HH:MM:SS` (vaqt qismi ajratilib, faqat sana olinadi).
2. **Excel Seriya Raqamlari (Serial Dates):**
   - Excel dasturi 1900-yil 1-yanvardan boshlab o'tgan kunlar sonini butun yoki kasr son ko'rinishida saqlaydi (masalan, `45350` -> `2024-02-29`).
   - Algoritm Excelning mashhur 1900-yil kabisa xatosini (leap year bug) inobatga olgan holda to'g'ri `datetime.date` obyektini hosil qiladi.
3. **Mantiqiy Chegara Tekshiruvi:**
   - Hozirgi kundan 365 kundan ortiq kelajakdagi sanalar `WARNING` maqomi bilan belgilanadi.

---

## 3. IDENTIFIKATORLARNI STANDARTLASHTIRISH

- **STIR / INN:** Barcha raqam bo'lmagan belgilar tozalanadi. O'zbekiston soliq to'lovchisi identifikatori aniq 9 ta raqamdan iborat bo'lishi kerak.
- **MXIK (IKPU):** Mahsulot va xizmatlarning yagona elektron klassifikatori kodi. 17 xonali raqamlar yoki nuqta bilan ajratilgan ko'rinishda saqlanadi.
- **Bank hisob raqami:** 20 xonali milliy bank hisobvarag'i raqami shakliga keltiriladi.
