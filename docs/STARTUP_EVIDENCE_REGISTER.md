# AGROHISOB CFO — DALILLAR VA DA'VOLAR REGISTRI (STARTUP EVIDENCE REGISTER)

**Sana:** 2026-yil 9-noyabr  
**Maqsad:** Investorlar taqdimoti, akselerator arizalari va ommaviy bayonotlarda ishlatiladigan har bir raqam va da'voning haqqoniyligini ta'minlash.  
**Qat'iy qoida:** Tasdiqlanmagan faktlar hech qachon "tasdiqlangan haqiqat" sifatida taqdim etilmaydi!

---

## 1. ASOSIY DA'VOLAR VA ULARNING VERIFIKATSIYA MATRITSASI

| Da'vo ID | Da'vo Matni | Birlamchi Manba | Verifikatsiya Holati | Sana | Tasdiqlovchi Hujjat / Kod | Taqdimotlarda Ruxsat Etilgan Aniq Matn |
|---|---|---|---|---|---|---|
| **EV-01** | Platforma 12 oylik mavsumiy pul oqimini hisoblay oladi | Backend dvigateli | **VERIFIED PRODUCT FEATURE** | 2026-11-09 | `test_engine_cashflow.py` | "12 oylik mavsumiy pul oqimini to'liq hisoblovchi ishchi MVP mavjud" |
| **EV-02** | DSCR koeffitsienti Agrobank andozasi bo'yicha to'g'ri chiqadi | Moliyaviy modellashtirish | **VERIFIED PRODUCT FEATURE** | 2026-11-09 | `test_engine_dscr.py` | "DSCR va qarz to'lash qobiliyatini bank andozasida hisoblovchi funksional tayyor" |
| **EV-03** | 1 bosishda PDF va Excel kredit dossiyesi generatsiya qilinadi | Reporting moduli | **VERIFIED PRODUCT FEATURE** | 2026-11-09 | `test_reports_api.py` | "1 bosishda professional PDF Dossier va dinamik Excel model generatsiya qilinadi" |
| **EV-04** | O'zbekiston agrar bozori hajmi (TAM) ~$64.8M / yil | AgroVentures dastlabki hisoboti | **MARKET ESTIMATE** | 2026-11-09 | `docs/TAM_SAM_SOM_MODEL.md` | "Bozor tahlili bo'yicha baholangan TAM: ~$64.8M/yil (dastlabki tadqiqot bahosi)" |
| **EV-05** | Hujjat tayyorlash vaqti 70%+ ga qisqaradi | Ichki MVP sinovi va reja | **FOUNDER ASSUMPTION** | 2026-11-09 | `docs/VALIDATION_HYPOTHESES.md` | "Ichki sinovda <15 daqiqa (rejalashtirilgan tejamkorlik 70%+; pilotda tekshiriladi)" |
| **EV-06** | Hozirda 15 ta intervyu o'tkazildi | Research Tracker | **NOT VERIFIED** (0 ta o'tkazilgan) | 2026-11-09 | `backend/storage/research/` | "Mijozlar bilan 15-20 ta intervyu o'tkazish bo'yicha tadqiqot rejasi tayyorlandi" |
| **EV-07** | Hozirda real to'lovchi mijozlar mavjud | Buxgalteriya / Bank | **NOT VERIFIED** (0 ta mijoz) | 2026-11-09 | `docs/STARTUP_FINANCIAL_MODEL.md` | "Mahsulot pilot validatsiya bosqichida (real to'lovchi mijozlar 0 ta)" |
| **EV-08** | Agrobank bilan rasmiy hamkorlik imzolandi | Yuridik bo'lim | **NOT VERIFIED** (Hamkorlik yo'q) | 2026-11-09 | `docs/AGROBANK_PILOT_PROPOSAL.md` | "AgroVentures akseleratsiyasi doirasida Agrobank ekotizimi uchun pilot taklifi ishlab chiqildi" |
| **EV-09** | Tizim 175 ta avtomatik testdan to'liq o'tgan | Pytest runner | **VERIFIED FACT** | 2026-11-09 | `backend/tests/` | "175/175 ta avtomatlashtirilgan backend testi 100% muvaffaqiyatli o'tgan" |
| **EV-10** | Tizim Vercel, Render va Supabase da jonli ishlab turibdi | Jonli URL lar | **VERIFIED FACT** (Shartli: /pilot-dashboard prod 404, lokal 200) | 2026-11-09 | `https://agrohisob-cfo.vercel.app` | "Bulutda jonli ishlayotgan MVP (Vercel + Render + Supabase); yangi pilot dashboard marshruti navbatdagi deployda faollashadi" |

---

## 2. PITCH VA ARIZALAR UCHUN QAT'IY YO'RIQNOMA

1. Hech qachon sintetik demo profillarni ("Bog'dor Bog'i", "Zarafshon Baraka") real mijozlar sifatida ko'rsatmang!
2. Moliyaviy prognozlarni (`$102k ARR`) kutilayotgan kelajak nishoni (`[TARGET]`) deb ayting, hozirgi tushum emas!
3. Agrobank nomi faqat potensial akselerator ekotizimi va pilot taklifi sifatida tilga olinishi shart.
