# AGROHISOB CFO — MAHSULOT NAMOYISHI SSENARIYLARI (DEMO SCRIPTS)

**Sana:** 2026-yil 9-noyabr  
**Format:** A (30s Elevator Pitch), B (60s Pitch), C (3 daqiqalik jonli mahsulot namoyishi)  
**Qoida:** Har bir qadam haqiqiy ishlab turgan jonli ekranga (`https://agrohisob-cfo.vercel.app`) asoslangan.

---

## 1. 30 SONIYALIK ELEVATOR PITCH

> *"O'zbekistonda 90,000 dan ortiq fermer mavjud, ammo ularning 70% dan ortig'i bahorgi kassa uzilishiga duch keladi va bankdan kredit olish uchun talab qilinadigan 12 oylik pul oqimi hisobotini tayyorlashga haftalab vaqt sarflaydi.  
AgroHisob CFO — bu agrobiznesning 1C va bank ko'chirmalarini bir necha daqiqada Agrobank andozasidagi tayyor kredit tahliliga va 12 oylik kassa prognoziga aylantirib beruvchi birinchi o'zbek tilidagi AI-CFO platformasidir. Mahsulotimiz bulutda jonli ishlamoqda!"*

---

## 2. 60 SONIYALIK INVESTOR PITCH

> *"Har yili O'zbekiston banklari agrar sohaga 30 trillion so'mdan ortiq kredit ajratadi. Ammo fermer va bank o'rtasida katta uzilish bor: fermer 12 oylik pul oqimi va DSCR modelini tuza olmaydi, bank anderrayterlari esa xom va xatolarga to'la hisobotlarni ko'rib chiqishga haftalab vaqt yo'qotadi.  
Biz AgroHisob CFO platformasini qurdik. Tizimimiz Didox elektron fakturalari va 1C ko'chirmalarini qabul qiladi, mavsumiy pul oqimlarini avtomatik modellashtiradi, VMQ-613 bo'yicha yer garovi likvidligini baholaydi va 1 bosishda rasmiy PDF Kredit Dossierini shakllantiradi.  
Biz allaqachon to'liq ishchi MVP ni ishlab chiqdik va O'zbekiston agrar bozoridagi $18.4 millionlik manzilga ega bozorga (SAM) chiqish uchun AgroVentures akseleratsiyasi doirasida 3-5 ta agrobiznes bilan pilot loyihasini boshlamoqdamiz."*

---

## 3. 3 DAQIQALIK JONLI MAHSULOT NAMOYISHI (LIVE DEMO SCRIPT)

### 0:00 - 0:40 | 1-Qadam: Tizimga kirish va Demo Ssenariyni tanlash
* **Ekran:** `https://agrohisob-cfo.vercel.app/demo`
* **Harakat:** Foydalanuvchi "Demo Ssenariylar" sahifasini ochadi va **"Bog'dor Bog'i MCHJ (Meva eksportyori)"** profilini tanlaydi.
* **Kutilayotgan natija:** 3.8 mlrd so'mlik eksport aylanmasi, intensiv olma bog'i va 1.2 mlrd so'mlik yangi kredit talabi yuklanadi.
* **Biznes nuqtasi:** "Fermer yoki eksportyor tizimga o'z 1C faylini yuklaganda ham xuddi shunday toza tahlil paydo bo'ladi."
* *Fallback:* Agar backend sekinlashsa, `/dashboard` sahifasidagi kesh ma'lumotlari ko'rsatiladi.

### 0:40 - 1:20 | 2-Qadam: 12 Oylik Kassa Prognozi va Kassa Uzilishi (Cash Gap)
* **Ekran:** `https://agrohisob-cfo.vercel.app/dashboard`
* **Harakat:** 12 oylik "Mavsumiy Pul Oqimi" grafigi va "Kassa balansi" dinamikasini ko'rsatish.
* **Kutilayotgan natija:** Mart-may oylaridagi xarajatlar cho'qqisi va avgust-noyabrdagi eksport tushumlari o'rtasidagi kassa balansi aniq ko'rinadi.
* **Biznes nuqtasi:** "Oddiy 1C faqat o'tgan yilni ko'rsatadi, AgroHisob CFO esa kelgusi yilning qaysi oyida pul yetishmasligini oldindan ko'rsatib, fermerga kredit miqdorini aniq rejalashtirishga yordam beradi."

### 1:20 - 2:00 | 3-Qadam: DSCR, Stress-Test va Garov Baholash
* **Ekran:** `https://agrohisob-cfo.vercel.app/scenario-analysis` va `/collateral-subsidies`
* **Harakat:** Stress-test slayderini surish (Hosildorlik -15%, Narx -20%) va VMQ-613 bo'yicha sug'oriladigan yer ijara huquqi bahosini ko'rsatish.
* **Kutilayotgan natija:** DSCR 1.42 dan 1.18 ga tushadi, tizim kredit riskini sariq rangda ogohlantiradi va garov qoplamini 145% deb hisoblaydi.
* **Biznes nuqtasi:** "Bu Agrobank kredit qo'mitasi talab qiladigan eng muhim kovenant hisoblanadi."

### 2:00 - 3:00 | 4-Qadam: 1 Bosishda Kredit Dossieri (PDF & Excel) Yuklab Olish
* **Ekran:** `https://agrohisob-cfo.vercel.app/credit-report`
* **Harakat:** "Bank uchun PDF Dossier Yuklab Olish" va "Excel Moliyaviy Model" tugmalarini bosish.
* **Kutilayotgan natija:** 2-3 sekundda brauzerga professional 6 sahifalik PDF fayl va dinamik formulali Excel model yuklab olinadi.
* **Xulosa gapi:** *"Konsaltantlar 10 kunda va 5 million so'mga tayyorlaydigan bank hujjatini AgroHisob CFO atigi 15 daqiqada xatosiz chiqarib beradi. Tizimimiz to'liq ishchi holatda!"*
