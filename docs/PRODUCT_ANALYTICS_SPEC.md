# AGROHISOB CFO — ICHKI MAHSULOT ANALITIKASI SPETSIFIKATSIYASI (PRODUCT ANALYTICS SPEC)

**Sana:** 2026-yil 9-noyabr  
**Tamoyil:** Privacy-by-Design, Zero-PII, Minimal Overhead

---

## 1. HODISALAR TAKSONOMIYASI (EVENT TAXONOMY)

Tizim quyidagi 10 ta standart hodisani anonim tarzda qayd etadi:

1. `demo_started` — Foydalanuvchi sintetik demo ssenariylaridan birini ochdi.
2. `import_started` — Buxgalteriya faylini yuklash boshlandi.
3. `import_completed` — Tranzaksiyalar muvaffaqiyatli normalizatsiya qilindi.
4. `import_failed` — Fayl noto'g'ri format yoki zararlangan sababli rad etildi.
5. `dashboard_viewed` — 12 oylik moliya paneli ko'rildi.
6. `forecast_generated` — Yangi kassa prognozi hisoblandi.
7. `scenario_calculated` — Stress-test (narx, hosil, tannarx) hisoblandi.
8. `report_generated` — PDF yoki Excel hisoboti shakllantirildi.
9. `report_downloaded` — Mijoz hisobot faylini yuklab oldi.
10. `feedback_submitted` — Foydalanuvchi baho yoki izoh qoldirdi.

---

## 2. XAVFSIZLIK VA PII SANITIZATSIYASI

Quyidagi maydonlar tushgan zahoti avtomatik ravishda `[REDACTED_PII]` bilan almashtiriladi:
- `inn`, `tin`, `tax_id`, `pinfl`
- `bank_account`, `card_number`
- `password`, `token`, `secret`, `auth`
- `amount_uzs`, `balance`
- `phone`, `email`

Faqatgina anonimlashtirilgan `session_id`, `organization_id`, hodisa turi, davomiylik vaqti (ms) hamda xatolik kategoriyasi saqlanadi.
Tizim tashqi uchinchi tomon pullik analitika xizmatlariga ulanmasdan, to'liq o'z serverida xavfsiz ishlaydi.
