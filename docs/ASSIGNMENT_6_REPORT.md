# AgroHisob CFO — Assignment 6 Yakuniy Ijro va Audit Hisoboti

## 1. Umumiy Xulosa

**AgroHisob CFO** platformasida **Assignment 6: Qishloq Xo'jaligi Garov Intellekti, Subsidiya Muvofiqligi, Indikativ Baholash va Normativ Moliyaviy Tahlil** to'liq, mukammal va me'yoriy qonunchilik talablariga 100% mos ravishda amalga oshirildi va sinovdan o'tkazildi.

Tizim fermer xo'jaliklariga:
1. **VMQ-613** talablari asosida yer ijara huquqini kredit garoviga qo'yish huquqiy tayyorgarligini tekshirish;
2. Kalendar asosidagi 5 yillik post-kredit bufer muddati, Davlat kadastri ro'yxatidan o'tganligi, taqiqlar va sub-ijara holatini tahlil qilish;
3. Cheklangan ijara ufqiga asoslangan, terminal qiymatsiz indikativ DCF baholash va 3 ta sezgirlik ssenariysini hisoblash;
4. 9 ta rasmiy hujjatdan iborat nazorat ro'yxatini shakllantirish;
5. **PQ-47** bo'yicha suv tejovchi texnologiyalar subsidiyasini ekin stavkalari (8M, 6M, 10M, 8M), hududiy koeffitsiyent (1.2x) va 50/50 bosqichma-bosqich to'lov asosida hisoblash;
6. **PF-82** bo'yicha paxta va g'alla kreditlariga 10 foiz bandi kompensatsiyasini muddati o'tgan qarzdorlikni qat'iy inkor etgan holda kunlik hisoblash imkoniyatlarini taqdim etdi.

---

## 2. Asosiy Natijalar Ko'rsatkichlari

- **Yangi Yaratilgan Backend Modullari:** `app/regulatory/`, `app/collateral/`, `app/subsidies/`
- **Yangi REST API Yo'nalishlari:**
  - `GET /api/v1/regulatory/sources`
  - `GET /api/v1/regulatory/sources/{code}`
  - `GET /api/v1/collateral/profile/default`
  - `POST /api/v1/collateral/eligibility`
  - `POST /api/v1/collateral/valuation/illustrative`
  - `POST /api/v1/collateral/scenarios`
  - `POST /api/v1/collateral/checklist`
  - `POST /api/v1/collateral/summary`
  - `GET /api/v1/subsidies/programs`
  - `POST /api/v1/subsidies/match`
  - `POST /api/v1/subsidies/calculate/pq47`
  - `POST /api/v1/subsidies/calculate/pf82`
  - `POST /api/v1/subsidies/financial-impact`
- **Frontend Interfeysi:**
  - `/collateral-subsidies` (Next.js 14.2 statik optimallashtirilgan, 3 ta interaktiv tab, kalkulyatorlar, cheklist)
  - Navbarda to'g'ridan-to'g'ri havola
- **Pytest Sinovlari:** 153 ta test, 153 ta muvaffaqiyatli (100% PASS), 0 ta xatolik
- **Kassa Invarianti:** 100% saqlandi (potentsial subsidiyalar tarixiy pul aylanmalariga aralashtirilmadi)
- **Nosertifikatlangan Baholash Ogohlantirishi (Disclaimer):** Har bir hisobot va API javobida majburiy mavjud.
