# AGROHISOB CFO — FINANCIAL DATA IMPORT SECURITY & REGULATORY COMPLIANCE

**Hujjat kodi:** `DOC-AGRO-A3-SEC-007`  
**Holati:** TASDIQLANGAN (APPROVED)  
**Versiya:** 1.0.0  

---

## 1. ME'YORIY-HUQUQIY ASOSLAR (UZBEKISTAN REGULATORY COMPLIANCE)

AgroHisob CFO platformasining ma'lumotlar import moduli O'zbekiston Respublikasining quyidagi qonun hujjatlariga to'liq mos holda loyihalashtirilgan:
1. **O'zbekiston Respublikasining "Shaxsga doir ma'lumotlar to'g'risida"gi Qonuni (O'RQ-547):**
   - Fermerlar va yuridik shaxslarning moliyaviy ma'lumotlari faqat belgilangan qonuniy maqsadlarda qayta ishlanadi.
   - Barcha ma'lumotlar bazalari O'zbekiston hududida lokal joylashadi.
2. **"Bank siri to'g'risida"gi Qonun (O'RQ-530):**
   - Bank hisobvaraqlarining ko'chirmalari va o'tkazmalari tijorat siri sifatida himoyalanadi.
   - Hech qanday bank hisobvaraq ma'lumotlari uchinchi tomon yoki xalqaro LLM APIlariga (OpenAI, Anthropic va boshqalar) uzatilmaydi.
3. **Davlat Soliq Qo'mitasining Elektron Hujjatlar Almashinuvi Talablari:**
   - E-fakturalar bilan ishlashda STIR, MXIK va QQS hisoblari soliq qonunchiligi talablariga mos yuritiladi.

---

## 2. TEXNIK XAVFSIZLIK MEXANIZMLARI

### 2.1. Fayllarni Tekshirish va DoS Hujumlaridan Himoya
- **O'lcham chegarasi:** Ruxsat etilgan maksimal fayl hajmi qat'iy ravishda 10 MB (10,485,760 bayt) qilib belgilangan. Kattaroq fayllar `FileSizeLimitExceededError` (HTTP 413) bilan qaytariladi.
- **Qatorlar va ustunlar cheklovi:** DoS va xotira to'lib ketishini oldini olish uchun har bir faylda maksimal 10,000 qator va 100 ustunga ruxsat beriladi.
- **Magic Bytes tekshiruvi:** Fayl kengaytmasini o'zgartirib yuborilgan zararli fayllar (masalan, `.exe` faylni `.xlsx` deb nomlash) faylning dastlabki baytlari orqali aniqlanadi va bloklanadi.

### 2.2. Excel Makroslari (VBA Payloads) Blokirovkasi
Excel formatidagi fayllar o'qilishidan oldin ZIP konteyneri ichidagi fayllar ro'yxati skaner qilinadi. Agar konteyner ichida `vbaProject.bin` yoki `.vba` fayllari aniqlansa, fayl bajariluvchi makroslarga ega deb hisoblanadi va import taqiqlanadi (`FileValidationError: MACRO_CONTAINED`).

### 2.3. Formula Inyeksiyasi (CSV / Formula Injection) Zararsizlantirilishi
Jadval katakchalari matn ko'rinishida saqlanadi. Katakcha boshida `=`, `+`, `-`, `@` kabi dinamik formula boshlovchi belgilar mavjud bo'lsa, ular zararsizlantirilib, matn sifatida qabul qilinadi. Bu eksport qilinganda buxgalter kompyuterida ixtiyoriy buyruqlar bajarilishini (DDE / Command Execution) oldini oladi.

### 2.4. Zero-Retention Rejimi
Foydalanuvchi interfeysidagi "Zero-Retention Rejimi" faollashtirilganda, import qilingan xom fayllar server diskida saqlanmaydi, faqat tezkor xotirada tahlil qilinib, kerakli buxgalteriya yozuvlari kiritilgandan so'ng kesh tozalanadi.

---

## 3. KRIPTOGRAFIK DUBLIKAT NAZORATI

1. **Fayl darajasida:** Har bir yuklangan faylning SHA-256 xesh summasi hisoblanadi. Tashkilot ilgari ushbu xeshga ega faylni yuklagan bo'lsa, tizim HTTP 409 Conflict qaytaradi.
2. **Tranzaksiya darajasida:** Har bir qator uchun kanonik barmoq izi shakllantiriladi:
   $$\text{Fingerprint} = \text{SHA256}(\text{org\_id} \parallel \text{date} \parallel \text{amount} \parallel \text{direction} \parallel \text{counterparty} \parallel \text{doc\_number})$$
   Bu qoida bir partiya ichidagi yoki oldingi oylar bilan tasodifan ikki marta kiritilgan takroriy to'lovlarni 100% aniqlikda ushlaydi.
