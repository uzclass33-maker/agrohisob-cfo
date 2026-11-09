# AGROHISOB CFO — AGROVENTURES AKSELERATORI ARIZA QORALAMASI (APPLICATION DRAFT)

**Topshirish statusi:** `DRAFT — FOUNDER APPROVAL REQUIRED`  
**Diqqat:** Ushbu ariza loyihasi asoschi tomonidan tasdiqlanmaguncha rasmiy tarzda yuborilmaydi!

---

## 1. UMUMIY MA'LUMOTLAR

* **Startap nomi:** AgroHisob CFO
* **Yuridik nomi:** "AgroHisob FinTech" MCHJ (tashkil etilmoqda / inkubatsiyada)
* **Mahsulot havolasi (Live MVP):** `https://agrohisob-cfo.vercel.app`
* **Backend API havolasi:** `https://agrohisob-backend.onrender.com`
* **Repozitoriy (Open Code):** `https://github.com/uzclass33-maker/agrohisob-cfo`
* **Yo'nalish:** AgriFinTech + B2B SaaS + AI-CFO
* **Joylashuv:** O'zbekiston, Toshkent shahri

---

## 2. MUAMMO (THE PROBLEM)

O'zbekistonda 90,000 dan ortiq fermer xo'jaliklari va 30,000 ta agrobiznes subyektlari mavjud. Ushbu korxonalarning 70% dan ortig'i qishloq xo'jaligining mavsumiy xususiyati (daromad yiliga 1 marta, xarajatlar yil bo'yi) sababli jiddiy kassa uzilishlariga (cash gap) duch keladi.

Mavjud 1C tizimlari faqatgina o'tgan davr hisobini yuritadi, lekin kelgusi 12 oylik likvidlik uzilishlarini bashorat qila olmaydi. Natijada, Agrobankdan aylanma mablag' yoki lizing krediti olish uchun talab etiladigan 12 oylik pul oqimi va DSCR modelini tuzish 5-14 kun vaqt oladi, tashqi konsaltantlarga 2-10 mln so'm to'lanadi va hisobotlarda 15-20% formulaviy xatoliklar uchraydi.

---

## 3. YECHIM VA INNOVATSIYA (THE SOLUTION & INNOVATION)

**AgroHisob CFO** — agrar korxonalar uchun maxsus ishlab chiqilgan birinchi o'zbek tilidagi AI-CFO va kredit anderrayting platformasidir.

Tizim quyidagi asosiy imkoniyatlarni taqdim etadi:
1. **Tezkor import:** 1C, Didox elektron fakturalari va bank ko'chirmalarini (XLSX, CSV) yuklab, xom ma'lumotlarni operatsion va moliyaviy oqimlarga avtomatik ajratadi.
2. **12 oylik mavsumiy kassa prognozi:** Qishloq xo'jaligi hosil yig'imi sikllarini hisobga olgan holda kassa uzilishlarini 12 oy oldin modellashtiradi.
3. **Agrobank andozasidagi DSCR tahlili:** Bank talablariga 100% mos formulalar asosida qarz to'lash qobiliyatini hisoblaydi va stress-ssenariylarni (hosil -15%, narx -20%) simulyatsiya qiladi.
4. **VMQ-613 va PQ-47 integratsiyasi:** Yer ijara huquqi likvidlik diskontlari va tomchilatib sug'orish bo'yicha davlat subsidiyalarini avtomatlashtirilgan tarzda baholaydi.
5. **1 bosishda Kredit Dossieri:** Bank mutaxassisi 2 daqiqada baholashi mumkin bo'lgan rasmiy PDF Kredit Dossieri va dinamik Excel moliyaviy modelini chiqarib beradi.

---

## 4. MVP VA TEXNOLOGIK TAYYORLIK (MVP STATUS)

* **Tayyorlik darajasi:** To'liq ishchi bulut MVP (Production-ready).
* **Texnologik stek:** Next.js 14 (App Router, Tailwind CSS, SWC Minified), Python 3.12 / FastAPI, PostgreSQL (Supabase Cloud) va ReportLab/OpenPyXL generatsiya dvigatellari.
* **Sifat kafolati:** 166/166 ta avtomatlashtirilgan test 100% yashil o'tgan. OWASP Top 10 xavfsizlik sarlavhalari va Excel formula inyektsiyasiga qarshi himoya to'liq joriy etilgan.
* **Sintetik ssenariylar:** Meva eksportyori ("Bog'dor Bog'i"), sabzavotchilik fermasi ("Zarafshon Baraka") va paxta klasteri ("Oq Oltin Agroklaster") uchun to'liq ishchi profillar mavjud.

---

## 5. BOZOR VA MIJOZLAR SEGMENTI (MARKET & CUSTOMERS)

* **TAM (O'zbekiston):** ~$64.8 million / yil (Fermerlar, KO'B lar va klasterlar).
* **SAM:** ~$18.4 million / yil (Bank krediti oluvchi va raqamli 1C/Didox yurituvchi subyektlar).
* **SOM (3 yillik bazaviy maqsad):** $1.23 million / yil (~1,450 ta to'lovchi korxona).
* **Mijozlar bilan aloqa:** 15-20 ta intervyu o'tkazish rejasi tuzilgan; 3-5 ta korxona bilan 4 haftalik bepul pilot dasturi rejalashtirilmoqda. Hozircha real to'lovchi mijozlar mavjud emas (mahsulot pilot bosqichida).

---

## 6. BIZNES MODELI VA MONETIZATSIYA (BUSINESS MODEL)

* **Starter (Fermer):** $29 / oy (~370,000 so'm).
* **Professional (Agri-SME):** $99 / oy (~1,260,000 so'm) — Eng asosiy tarif.
* **Enterprise (Klaster):** $249 / oy (~3,180,000 so'm).
* **One-time Credit Dossier:** $149 / hisobot (bir martalik kredit tayyorgarligi).

---

## 7. AGROBANK EKOTIZIMI VA AGROVENTURES BILAN HAMKORLIK PILOTI

Biz AgroVentures akseleratsiyasi doirasida Agrobank bilan quyidagi **"Pre-underwriting Pilot"** dasturini amalga oshirishni taklif qilamiz:
* Agrobankning tanlangan 10-20 ta agrobiznes mijoziga kredit arizasini tayyorlashda AgroHisob CFO xizmatidan foydalanish imkoniyatini berish.
* Bank ichki tizimlariga (Core Banking) ulanmasdan, faqat mijoz tomonidan shakllantirilgan standartlashtirilgan PDF/Excel kredit paketlarini ko'rib chiqish.
* Natijada: Mijozlar arizasi tayyorlanish vaqti 5-10 kundan <1 kungacha qisqaradi, bank anderrayterlari vaqti tejaladi, kredit xatarlari kamayadi.

---

## 8. INVESTITSIYA SO'ROVI VA FOYDALANISH REJASI (INVESTMENT ASK)

* **So'ralayotgan investitsiya miqdori:** **$35,000 – $50,000** (Akseleratsiya bosqichi uchun).
* **Mablag'larni taqsimlash:**
  - **45% — Mahsulot va Sun'iy Intellekt:** 1C to'g'ridan-to'g'ri integratsiyasi, e-faktura API ulanishlari, AI-tahlil dvigatelini kuchaytirish.
  - **35% — Bozorga chiqish (GTM) va Pilot:** 5 ta viloyatda fermerlar bilan bevosita pilotlar o'tkazish, treninglar va mijozlarni qo'llab-quvvatlash.
  - **20% — Infratuzilma, Yuridik va Xavfsizlik:** Server quvvatlarini oshirish, xavfsizlik auditlari, O'zbekiston standartlari bo'yicha sertifikatlash.
