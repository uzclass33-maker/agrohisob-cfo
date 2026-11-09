# AGROHISOB CFO — PDF HISOBOT SPETSIFIKATSIYASI (ASSIGNMENT 5)

## 1. Kirish va Vizual Standart
AgroHisob CFO platformasi professional bank kredit anderraytingi uchun yuqori darajadagi, chop etishga tayyor (print-ready) A4 formatdagi PDF hisobotlarni Python `reportlab 4.4.9` kutubxonasi orqali shakllantiradi.

---

## 2. Dizayn va Tipografiya Standartlari
- **Sahifa O'lchami:** Standard A4 (210 x 297 mm, 595.27 x 841.89 pt).
- **Hoshiyalar (Margins):** Chap: 36 pt, O'ng: 36 pt, Yuqori: 45 pt, Quyi: 45 pt. Bosma kengligi: 523 pt.
- **Ranglar Palitrasi:**
  - Asosiy to'q ko'k (Primary Navy): `#0f172a` (Sarlavhalar, jadval shapkalari).
  - Zumrad yashil (Emerald Accent): `#059669` (Ijobiy oqimlar, barqarorlik ko'rsatkichlari, muvaffaqiyat ramzlari).
  - Neytral fon: `#f8fafc` va `#f1f5f9` (Kataklar foni, almashinuvchi satrlar).
  - Ogohlantirish qizil/sariq: `#dc2626` / `#d97706` (Xatarlar, kassa uzilishi).
- **Tipografiya:**
  - Asosiy matn: Helvetica 9pt / 12pt leading.
  - Sarlavha 1 (H1): Helvetica-Bold 14pt / 18pt leading.
  - Sarlavha 2 (H2): Helvetica-Bold 11pt / 14pt leading.
  - Muqova sarlavhasi: Helvetica-Bold 22pt / 26pt leading.

---

## 3. Ikki Bosqichli Dinamik Sahifa Raqamlash (NumberedCanvas)
`pdf_generator.py` da maxsus `NumberedCanvas` sinfi yaratilgan:
- **1-bosqich:** Sahifalar generatsiya qilinadi va ularning holati `_saved_page_states` ro'yxatida xotirada saqlanadi.
- **2-bosqich:** Umumiy sahifalar soni aniqlangach, har bir sahifaga qayta murojaat qilinadi va muqova (1-sahifa) dan tashqari barcha sahifalarga:
  - Yuqori kolontitul (Running Header): «AgroHisob CFO — Bank Kreditga Tayyorgarlik Dosyesi va Moliyaviy Modeli».
  - Quyi kolontitul (Running Footer): «Maxfiy axborot — Faqat vakolatli kredit anderraytingi uchun».
  - Dinamik sahifa hisobi: «Sahifa X / Y» (masalan: `Sahifa 2 / 5`, `Sahifa 5 / 5`).

---

## 4. Dosye Bo'limlari Tuzilishi (8 Bo'lim)
1. **Muqova Sahifasi (Cover Page):** Korxona nomi, STIR, tashkiliy shakli, so'ralayotgan kredit summasi, muddati, foizi, tayyorgarlik bahosi (0-100), maxfiylik tamg'asi.
2. **Ijroiya Xulosa va Reyting (Executive Summary):** 0-100 skoring natijasi, kuchli tomonlar, aniqlangan xatarlar, 12 oylik yuqori darajadagi moliyaviy jadval.
3. **Tarixiy Moliyaviy Ko'rsatkichlar (Historical Cash Flow):** 12 oylik haqiqiy kassa aylanmasi, oylik tushumlar, opex va sof kassa qoldiqlari.
4. **12 Oylik Mavsumiy Kassa Prognozi (Seasonal Forecast):** Agrotexnik ekinlar bo'yicha tushumlar, operatsion chiqimlar, kassa taqchilligi (deficit) nuqtalari.
5. **Qarz Yuklamasi va DSCR Tahlili (Debt & DSCR):** So'ralayotgan kredit amortizatsiya jadvali (boshlang'ich, asosiy qarz, foiz, yakuniy qoldiq), mavjud va yangi qarz yuki, birlashtirilgan DSCR.
6. **Xatarlar va Ssenariylar Tahlili (Scenarios):** Bazaviy, optimistik va pessimistik (stress) tahlil jadvali.
7. **Hujjatlar Nazorati (Checklist):** 5 toifadagi 12 ta hujjat holati (`AVAILABLE`, `MISSING`, `NEEDS_REVIEW`).
8. **Rasmiy Huquqiy Cheklov (Statutory Disclaimer):** Bank kredit qo'mitasi mustaqil qarori ekanligi to'g'risidagi qonuniy ogohlantirish.
