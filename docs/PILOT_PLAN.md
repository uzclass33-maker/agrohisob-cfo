# AGROHISOB CFO — 4 HAFTALIK PILOT DASTURI REJASI (PILOT PLAN)

**Sana:** 2026-yil 9-noyabr  
**Versiya:** 1.0  
**Maqsad:** 3-5 ta agrar korxona ishtirokida AgroHisob CFO platformasining qiymati, vaqt tejalishi va hisobot aniqligini amalda tekshirish.  
**Eslatma:** Ushbu reja nishon ko'rsatkich hisoblanadi. Ishtirokchilar korxona rahbari ruxsatisiz va NDA imzolanmasdan jalb qilinmaydi.

---

## 1. PILOT MAQSADI VA KO'LAMI (PILOT SCOPE)

Pilot faqatgina 3 ta asosiy ish oqimiga (core workflows) qaratiladi:
1. **Moliyaviy hujjatlar importi:** 1C aylanma vedomostlari, Didox elektron fakturalari va bank ko'chirmalari (XLSX, CSV).
2. **Pul oqimi va kassa prognozi:** Tarixiy pul harakati, kelgusi 12 oylik mavsumiy kassa uzilishlari va DSCR tahlili.
3. **Kreditga tayyorgarlik hisoboti:** Agrobank andozasiga mos tayyor PDF Kredit Dossieri va dinamik Excel moliyaviy modeli.

---

## 2. PILOT BOSQICHLARI VA HAFTALIK REJA

```mermaid
flowchart LR
    W1["1-Hafta:<br/>Onboarding & Baseline"] --> W2["2-Hafta:<br/>Data Import & Normalization"]
    W2 --> W3["3-Hafta:<br/>Cash Flow, DSCR & Reports"]
    W3 --> W4["4-Hafta:<br/>Review & Commercial Offer"]
```

### 1-Hafta: Saralash, Onboarding va Dastlabki O'lchov (Baseline Measurement)
- **Vazifalar:**
  - 3-5 ta korxona (1 ta eksportyor, 2 ta fermer, 1 ta qayta ishlovchi SME) bilan tanishuv uchrashuvi.
  - Ma'lumotlar maxfiyligi shartnomasi (NDA) va pilot reglamentini imzolash.
  - Korxonaning mavjud hisobot tayyorlash vaqtini xronometraj qilish ($T_{baseline}$).
- **Kutilayotgan natija:** Imzolangan NDA, to'ldirilgan `Baseline Measurement Form`.

### 2-Hafta: Buxgalteriya Ma'lumotlarini Yuklash va Tekshirish
- **Vazifalar:**
  - Oxirgi 12 oylik real yoki anonimlashtirilgan bank ko'chirmalari va hisob-fakturalarni import qilish.
  - Avtomatlashtirilgan tasniflash (classification) va duplikatlarni aniqlash natijalarini buxgalter bilan solishtirish.
- **Kutilayotgan natija:** To'liq yuklangan va xatoliklardan tozalangan tranzaksiyalar registri.

### 3-Hafta: 12 Oylik Prognoz, DSCR va Kredit Hujjatlarini Chiqarish
- **Vazifalar:**
  - 12 oylik pul oqimi va stress-ssenariylar (hosil -15%, narx -20%) hisob-kitobini o'tkazish.
  - Agrobank talabidagi DSCR va garov likvidligini (VMQ-613) baholash.
  - 1 bosishda PDF Kredit Dossieri va Excel modelini generatsiya qilish.
- **Kutilayotgan natija:** Korxona rahbari va bank mutaxassisi ko'rib chiqishi uchun tayyor kredit paketi.

### 4-Hafta: Natijalar, Foydalanuvchi Bahosi va Tijorat Taklifi
- **Vazifalar:**
  - Tejalgan vaqtni hisoblash: $Time\ Saved = (T_{baseline} - T_{product}) / T_{baseline} \times 100\%$.
  - Foydalanuvchi qoniqishi bo'yicha so'rovnoma (CSAT / NPS) o'tkazish.
  - Korxonaga doimiy B2B SaaS obunasiga o'tish bo'yicha tijorat taklifini (Commercial Offer) taqdim etish.
- **Kutilayotgan natija:** Rasmiy pilot hisoboti, foydalanuvchi xulosasi, obunaga rozi bo'lgan birinchi mijozlar.

---

## 3. PILOTDAN CHIQISH MEZONLARI (EXIT CRITERIA)

Pilot muvaffaqiyatli yakunlangan deb hisoblanadi, agar:
1. Ishtirokchi korxonalarning kamida 80% qismi barcha 3 ta ish oqimini to'liq yakunlasa.
2. Moliyaviy hisobot tayyorlash vaqti kamida 60% ga qisqarganligi o'lchov orqali tasdiqlansa.
3. Hisobotlar buxgalter tomonidan 0% matematik xatolik bilan qabul qilinsa.
4. Kamida 2 ta korxona pullik obunaga qiziqish bildirsa yoki niyat xati (LOI) imzolasa.
