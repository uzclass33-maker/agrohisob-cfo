# AGROHISOB CFO — XAVFSIZLIK MODELI VA MA'LUMOTLAR MAXFIYLIGI
## Security Architecture, Multi-Tenancy & Regulatory Compliance (O'zbekiston Qonunchiligi)

---

## 1. Me'yoriy-Huquqiy Asoslar

AgroHisob CFO platformasi O'zbekiston Respublikasining quyidagi qonunchilik hujjatlariga qat'iy muvofiq tarzda loyihalashtirilgan:
1. **O'zbekiston Respublikasining «Shaxsga doir ma'lumotlar to'g'risida»gi Qonuni (O'RQ-547, 02.07.2019):**
   - O'zbekiston rezidentlarining shaxsga doir ma'lumotlari jismoniy jihatdan O'zbekiston Respublikasi hududida joylashgan serverlarda saqlanishi va ishlanishi shart (27-1-modda).
   - Moliyaviy va shaxsiy ma'lumotlar qat'iy maqsadli ishlatiladi va ruxsatsiz uchinchi shaxslarga uzatilmaydi.
2. **O'zbekiston Respublikasining «Bank siri to'g'risida»gi Qonuni:**
   - Tijorat banklaridagi hisobvaraqlar va operatsiyalar ma'lumotlari bank siri hisoblanadi. AgroHisob CFO foydalanuvchining bevosita roziligisiz yoki maxfiy kalitlarsiz bank hisoblariga to'g'ridan-to'g'ri noqonuniy ulanishni amalga oshirmaydi.
3. **O'zbekiston Respublikasi Vazirlar Mahkamasining 613-sonli Qarori (VMQ-613, 30.09.2025):**
   - Qishloq xo'jaligi yer uchastkalariga bo'lgan ijara huquqini baholash va garovga qo'yish jarayonida kadastr va bonitet ma'lumotlarini qonuniy qayta ishlash.

---

## 2. Multi-Tenancy va Tashkilotlararo Izolyatsiya

### 2.1. Ma'lumotlar Bazasi Darajasidagi Ajratish
- Barcha moliyaviy ma'lumotlar jadvallari (`financial_periods`, `transactions`, `imported_files`, `debt_schedules`, `financial_forecasts`, `generated_reports`) majburiy ravishda `organization_id` ustuniga ega.
- Tashkilotlararo ma'lumotlar oqishi (cross-tenant data leakage)ni oldini olish uchun PostgreSQL darajasida **Row Level Security (RLS)** qo'llaniladi:
  ```sql
  ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
  
  CREATE POLICY tenant_isolation_policy ON transactions
    USING (organization_id = CURRENT_SETTING('app.current_organization_id')::UUID);
  ```
- Har bir API so'rovida foydalanuvchining autentifikatsiya qilingan JWT tokeni orqali uning tegishli tashkiloti aniqlanadi va sessiyaga kiritiladi.

### 2.2. Foydalanuvchilar va Tashkilot A'zoligi (RBAC)
Tizimda 5 ta rol darajasi belgilangan:
1. **SUPER_ADMIN:** Platforma infratuzilmasi va xavfsizlik ma'muri (mijozlarning maxfiy moliyaviy ma'lumotlarini ko'rish huquqiga ega emas).
2. **CFO (Bosh moliyaviy direktor):** Tashkilotning barcha moliyaviy hisobotlari, kredit dosyelari va ssenariylarini to'liq boshqarish.
3. **CHIEF_ACCOUNTANT (Bosh buxgalter):** E-faktura va bank ko'chirmalarini yuklash, birlamchi provodkalarni tekshirish va tasdiqlash.
4. **FINANCIAL_ANALYST (Moliyaviy tahlilchi):** Faqat tahlil va ssenariy modellashtirish rejimida o'qish (read-only).
5. **BANK_AUDITOR (Bank anderrayteri/auditor):** Faqat belgilangan kredit arizasi doirasida generatsiya qilingan kredit dosyesini tekshirish huquqi.

---

## 3. «Zero-Retention» (Ma'lumotlarni Saqlamaslik) Rejimi

AgroHisob CFO fermer va eksportyorlarning nozik tijorat ma'lumotlarini himoya qilish uchun maxsus **«Zero-Retention»** rejimini qo'llab-quvvatlaydi:
- **Xotirada Qayta Ishlash (In-Memory Processing):**
  - Foydalanuvchi Soliq E-faktura (Excel/XML) yoki Bank ko'chirmasi (CSV/PDF) faylini yuklaganda, fayl diskda doimiy saqlanmaydi.
  - Ma'lumotlar bevosita server operativ xotirasida (RAM) tahlil qilinadi, faqat jamlangan (aggregatsiyalangan) kassa oqimlari bazaga yoziladi va birlamchi fayl darhol xotiradan to'liq tozalanadi.
- **SHA-256 Nazorat Summasi:**
  - Bir xil faylni takroran yuklashning oldini olish uchun faylning faqat 64 belgili SHA-256 hesh qiymati saqlanadi, asl hujjat tarkibi esa saqlanmaydi.

---

## 4. Xavfsiz Audit va Log Yuritish (Sanitized Logging)

Tizim jurnallari (logs)da quyidagi shaxsiy va moliyaviy ma'lumotlarni ochiq holda yozish qat'iyan man etiladi:
- Jismoniy shaxsning JShShIR va pasport ma'lumotlari.
- Fermer yoki ta'sischining shaxsiy telefon raqamlari.
- Kontragentlarning to'liq 20 xonali bank hisob raqamlari (faqat oxirgi 4 ta raqam ko'rinishi mumkin: `**** **** 4092`).
- E-faktura yoki bank tizimlari API kalitlari va JWT bearer tokenlari.

---

## 5. Sun'iy Intellekt va LLM Xavfsizligi

1. **Maxfiy Ma'lumotlarni Tashqi Modellar bilan Bo'lishmaslik:**
   - Foydalanuvchining real kassa ma'lumotlari, STIR raqamlari yoki soliq hisobotlari hech qanday ochiq tashqi LLM API'lariga (masalan, OpenAI, tashqi bulutli ochiq modellar) yuborilmaydi.
2. **Deterministik Hisoblash Ustuvorligi:**
   - Barcha kassa qoldiqlari, DSCR, LTV va kredit skoringi sun'iy intellekt matn generatori orqali EMAS, balki Python `Decimal` deterministik matematik dvigateli orqali hisoblanadi. Sun'iy intellekt faqat hisoblangan raqamlar asosida standart tavsiyalar matnini tuzish uchun cheklangan kontekstda ishlatiladi.
