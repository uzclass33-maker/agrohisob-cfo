# AGROHISOB CFO — FILE FORMAT SUPPORT & PARSING SPECIFICATION

**Hujjat kodi:** `DOC-AGRO-A3-FMT-002`  
**Holati:** TASDIQLANGAN (APPROVED)  
**Versiya:** 1.0.0  

---

## 1. QO'LLAB-QUVVATLANADIGAN FAYL FORMATLARI

AgroHisob CFO O'zbekiston agrobiznesida eng ko'p tarqalgan ikki turdagi elektron jadval formatini to'liq qo'llab-quvvatlaydi:

| Format | Kengaytma | MIME-Turi | Maksimal Hajm | Manba Tizimlar |
|---|---|---|---|---|
| Comma/Semicolon Separated Values | `.csv` | `text/csv`, `text/plain` | 10 MB (taxm. 100,000 qator) | Bank mijoz dasturlari (Agrobank, Ipak Yo'li, Kapitalbank), 1C Buxgalteriya eksporti |
| Microsoft Excel OpenXML Spreadsheet | `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | 10 MB (taxm. 50,000 qator) | Soliq.uz E-Faktura tizimi, Didox.uz, F-Box, 1C |

---

## 2. CSV AJRATUVCHILARI (DELIMITERS) VA KODLASHTIRISH (ENCODING)

### 2.1. Avtomatik Ajratuvchi Sniffing
O'zbekistondagi buxgalteriya dasturlari ko'pincha standart vergul (`,`) emas, balki nuqta-vergul (`;`) yoki tabulyatsiya (`\t`) belgilaridan foydalanadi, chunki rus/o'zbek raqam formatlarida vergul kasr ajratuvchi sifatida xizmat qiladi.
Tizim dastlabki 15 qatordan namuna olib, Python'ning `csv.Sniffer` mexanizmi va chastotali evristika yordamida ajratuvchini avtomatik aniqlaydi:
- Nuqta-vergul (`;`) — 1C va O'zbekiston banklari standarti
- Vergul (`,`) — xalqaro CSV standarti
- Tabulyatsiya (`\t`) — matnli eksportlar
- Vertikal chiziq (`|`) — maxsus reestrlar

### 2.2. Kodlashtirishni (Encoding) Aniqlash
1C va eski bank tizimlari ko'pincha kirillcha `Windows-1251` (CP1251) yoki `UTF-8 with BOM` kodlashida fayl shakllantiradi.
Tizim quyidagi ketma-ketlikda kodlashni aniqlaydi:
1. `b"\xef\xbb\xbf"` bayt belgisi bo'yicha `utf-8-sig`
2. Qat'iy `utf-8` dekodlash sinovi
3. Kirillcha `cp1251` dekodlash sinovi
4. Yo'qotishsiz `latin-1` zaxira varianti

---

## 3. EXCEL (.XLSX) ISHLOV BERISH QOIDALARI

1. **Konteyner yaxlitligi:** `PK\x03\x04` ZIP magic baytlari orqali tekshiriladi.
2. **Makroslarni bloklash:** Konteyner ichida `xl/vbaProject.bin` fayli mavjud bo'lsa, xavfsizlik nuqtai nazaridan import darhol rad etiladi (`FileValidationError: MACRO_CONTAINED`).
3. **Data-Only Rejimi:** `openpyxl.load_workbook(..., data_only=True, read_only=True)` yordamida o'qiladi. Bu katakchalardagi formulalarni emas, balki oxirgi hisoblangan raqamli qiymatlarni o'qishni ta'minlaydi.
4. **Sarlavhalar satrini avtomatik topish:** Excel fayllarida sarlavha har doim ham 1-satrda bo'lmaydi (ko'pincha dastlabki qatorlarda korxona nomi yoki bo'sh joylar bo'ladi). Parser kamida 2 ta matnli ustunga ega bo'lgan birinchi to'liq satrni sarlavha sifatida avtomatik aniqlaydi.

---

## 4. XAVFSIZLIK VA FORMULA INYEKTSIYASI (CSV INJECTION) HIMOYaSI

Foydalanuvchi yuklagan matnli ustunlar (`counterparty_name`, `purpose`, `document_number`) kelgusida Excel orqali eksport qilinganda zararli buyruqlar bajarilishining oldini olish uchun quyidagi belgilar bilan boshlanuvchi matnlar xavfsiz holatga keltiriladi:
- `=`, `+`, `-`, `@`, `\t`, `\r`
Bunday katakchalar matn sifatida saqlanib, bajariluvchi formula sifatida talqin etilmaydi.
