# AGROHISOB CFO — DASTURIY TA'MINOT XAVFSIZLIGI AUDITI VA STANDARTLARGA MOSLIK (SECURITY AUDIT)

**Hujjat identifikatori:** `DOC-AH-SEC-01`  
**Sana:** 2026-11-09  
**Holat:** TASDIQLANGAN (APPROVED)  
**Tadqiqotchi guruh:** FinTech Application Security Engineer, Lead Pentester  

---

## 1. IJROIY XULOSA VA XAVFSIZLIK YONDASHUVI

AgroHisob CFO platformasi qishloq xo'jaligi korxonalarining maxfiy moliyaviy ma'lumotlari, bank hisobvaraqlaridan ko'chirmalar va yer kadastr hujjatlarini qayta ishlaydi. Shu sababli tizim OWASP Top 10 va FinTech xavfsizlik standartlari asosida to'liq auditdan o'tkazildi va himoyalash choralari joriy etildi.

---

## 2. OWASP TOP 10 FINTECH NAZORAT NATIJALARI

| OWASP Zaiflik Kategoriya | Xavf Darajasi | AgroHisob CFO Himoya Mexanizmi | Holat |
| :--- | :--- | :--- | :--- |
| **A01: Broken Access Control** | Yuqori | Multi-tenant tashkilot darajasidagi ma'lumotlar izolatsiyasi (`organization_id`). Har bir so'rovda korxona chegaralari qat'iy tekshiriladi. | Himoyalangan |
| **A02: Cryptographic Failures**| Yuqori | Tranzitdagi barcha ma'lumotlar HTTPS/TLS 1.3 orqali uzatiladi. `SECRET_KEY` kamida 256-bit entropiyaga ega. Fayllar SHA-256 bilan tamg'alanadi. | Himoyalangan |
| **A03: Injection (SQL & Formula)**| O'ta Yuqori | SQLAlchemy 2.0 ORM orqali barcha SQL so'rovlari parametrlashtirilgan. Excel fayllarga yozishda formula inyeksiyasi (`=`, `+`, `-`, `@`) belgilari zararsizlantiriladi. | Himoyalangan |
| **A04: Insecure Design** | O'rta | Deterministic moliyaviy qoidalar arxitekturasi; AI xulosalari faqat qat'iy tekshirilgan sonli faktlarga tayanadi. | Himoyalangan |
| **A05: Security Misconfiguration**| O'rta | Dinamik CORS oq ro'yxati (`ALLOWED_ORIGINS`), barcha javoblarda korporativ xavfsizlik sarlavhalari (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`). | Himoyalangan |
| **A06: Vulnerable Components** | O'rta | Barcha Python va Node paketlari yangi barqaror versiyalarda (`requirements.txt`, `package.json`). | Himoyalangan |
| **A07: Identification Failures**| Yuqori | JWT tokenlar, qisqa muddatli sessiyalar, parollar xeshlash algoritmlari (Bcrypt). | Himoyalangan |
| **A08: Software Data Integrity**| Yuqori | Yuklanayotgan 1C/Bank fayllari hajmi (15MB), MIME turi va zip/macro imzolarga qarshi tekshiriladi. | Himoyalangan |
| **A09: Logging & Monitoring** | O'rta | So'rovlar bajarilish vaqti (`X-Process-Time`), xatoliklar va audit loglari markazlashgan tizimda yoziladi. | Himoyalangan |
| **A10: SSRF** | Past | Tashqi so'rovlar faqat ichki tasdiqlangan davlat me'yoriy registrlari bilan cheklangan. | Himoyalangan |

---

## 3. FAYL YUKLASH VA EXCEL FORMULA INYEKTSIYASIDAN HIMOYA (CSV/XLSX SECURITY)

1. **Fayl Hajmi va Format Cheklovi:**
   - Maksimal ruxsat etilgan hajm: 15 MB.
   - Formatlar: faqat `.csv`, `.xlsx`, `.xls`.
   - Barcha yuklanayotgan fayllar kontenti (magic bytes) tekshiriladi, zararli VBA makroslari (`xl/vbaProject.bin`) mavjud bo'lsa darhol rad etiladi (`HTTP 400`).
2. **Formula Injection (CSV/Excel Formula Injection):**
   - Eksport qilinadigan Excel fayllaridagi matnli yozuvlar (kontragent nomi, to'lov maqsadi) agar `=`, `+`, `-`, `@` belgilari bilan boshlansa, oldiga avtomatik ravishda `'` (apostrof) belgisi qo'shiladi. Bu Microsoft Excel yoki LibreOffice da ixtiyoriy tashqi dasturlarni ishga tushirish (DDE hujumi) xavfini butunlay bartaraf etadi.
3. **Dublikat Tranzaksiyalarni Filtrlash:**
   - Har bir tranzaksiya satri uchun `sha256(sana + summa + kontragent + maqsad)` xeshi hisoblanadi va bitta fayl yoki bir xil davr ichida ikki marta hisobga olinmaydi.

---

## 4. HTTP XAVFSIZLIK SARLAVHALARI (SECURITY HEADERS) TEKSHIRUVI

`backend/app/main.py` dagi `SecurityHeadersMiddleware` orqali har bir javobga quyidagi sarlavhalar qo'shiladi:
- `X-Content-Type-Options: nosniff` — Brauzerlarning MIME-turini noqonuniy o'zgartirishiga yo'l qo'ymaydi.
- `X-Frame-Options: DENY` — Clickjacking hujumlariga qarshi saytni boshqa sahifa iframe larida ochilishini bloklaydi.
- `X-XSS-Protection: 1; mode=block` — Brauzerning XSS filtrini majburiy yoqadi.
- `Referrer-Policy: strict-origin-when-cross-origin` — Havola orqali o'tganda sirlarni sizib chiqishini oldini oladi.
- `Permissions-Policy: geolocation=(), microphone=(), camera=()` — Keraksiz brauzer ruxsatlarini bloklaydi.
- `X-Process-Time: 0.001234s` — Har bir API chaqiruvining hisoblash unumdorligini nazorat qiladi.

---

## 5. SIRLAR VA KALITLAR GIGIYENASI (SECRETS HYGIENE)

- Repozitoriyda ishlab chiqarish (production) kalitlari mavjud emasligi avtomatlashtirilgan CI/CD skripti orqali tasdiqlangan.
- Barcha ishlab chiqarish o'zgaruvchilari xavfsiz muhit menejeri (Vercel & Railway Environment Secrets) orqali kiritiladi.
- Dastur ishga tushganda production muhitida birlamchi dev kaliti ishlatilayotgan bo'lsa, xavfsizlik ogohlantirishi beriladi.
