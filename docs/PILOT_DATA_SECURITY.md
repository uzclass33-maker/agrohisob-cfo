# AGROHISOB CFO — PILOT MA'LUMOTLAR XAVFSIZLIGI VA MAXFIYLIK REGLAMENTI (PILOT DATA SECURITY)

**Sana:** 2026-yil 9-noyabr  
**Standart:** O'zbekiston Respublikasining "Shaxsga doir ma'lumotlar to'g'risida"gi Qonuni va FinTech AppSec qoidalari

---

## 1. ASOSIY XAVFSIZLIK TAMOYILLARI

1. **Tashkilotlararo to'liq izolyatsiya (Tenant Isolation):**
   - Har bir pilot ishtirokchisining barcha tranzaksiyalari, hisob-kitoblari va hujjatlari qat'iy `organization_id` orqali ajratiladi.
   - Bitta fermerning ma'lumotlarini boshqa foydalanuvchi ko'rishi texnik jihatdan imkonsiz (Supabase Row-Level Security va FastAPI sessiya tekshiruvi).

2. **Zero-PII Analitika Siyosati:**
   - Mahsulot analitikasi (`/api/v1/analytics/events`) hech qachon bank hisob raqamlari, karta raqamlari, STIR (INN), JShShIR (PINFL), korxona nomi yoki moliyaviy summalarni qayd etmaydi.
   - Har qanday nozik kalitlar avtomatik ravishda `[REDACTED_PII]` bilan almashtiriladi.

3. **Shifrlash (Encryption in Transit & at Rest):**
   - Barcha tarmoq trafigi faqat TLS 1.3 / HTTPS orqali shifrlanadi.
   - Supabase bulut ma'lumotlar bazasi AES-256 shifrlash standarti bilan himoyalangan.

4. **Ma'lumotlarni saqlash va o'chirish (Data Retention & Deletion):**
   - Pilot yakunlangandan so'ng, agar korxona pullik obunani davom ettirishni xohlamasa, uning barcha yuklangan xom fayllari va hisob-kitoblari 14 kun ichida serverdan butunlay o'chiriladi.
   - Mijoz istalgan vaqtda o'z ma'lumotlarini to'liq o'chirib tashlashni talab qilish huquqiga ega.

5. **Hodisalarga javob berish rejasi (Incident Response Procedure):**
   - Xavfsizlik shubhasi yuzaga kelganda, mas'ul xavfsizlik muhandisi 1 soat ichida tizimga kirishni vaqtincha to'xtatadi, audit loglarini tahlil qiladi va korxona rahbarini darhol xabardor qiladi.
