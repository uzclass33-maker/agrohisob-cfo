# AgroHisob CFO — Qishloq Xo'jaligi Subsidiya Intellekti Arxitekturasi (Module B)

## 1. Modul Maqsadi

O'zbekiston agrar sektorida subsidiyalar fermer xo'jaliklarining kapital xarajatlarini (CAPEX) va qarz xizmati yukini sezilarli darajada yengillashtiruvchi muhim davlat qo'llab-quvvatlash vositasi hisoblanadi.

AgroHisob CFO **Subsidiya Intellekti (Subsidy Intelligence)** modulining vazifalari:
1. Amaldagi normativ-huquqiy hujjatlar (**PQ-47**, **PF-82**) bo'yicha subsidiya dasturlari reestrini yuritish;
2. Fermer xo'jaligi profiliga (ekin turi, hudud, sug'orish texnologiyasi, kredit tarixi) asoslanib, dasturlarni 5 ta qat'iy holat bo'yicha saralash;
3. Suv tejovchi texnologiyalar (PQ-47) va paxta/g'alla foiz kompensatsiyasi (PF-82) bo'yicha aniq kalkulyatorlarni taqdim etish;
4. Subsidiyalarning kassa oqimiga va kredit qoplash koeffitsiyentiga (DSCR) ta'sirini baholash;
5. **Kassa Invarianti:** Potentsial subsidiyalarni hech qachon tasdiqlanmagan tarixiy kassa aylanmalariga qo'shmaslik.

---

## 2. 5 Ta Deterministik Muvofiqlik Statusi

Har bir subsidiya dasturi bo'yicha fermer profili quyidagi 5 holatdan biriga ajratiladi:

1. `POTENTIALLY_ELIGIBLE` — Dastlabki mezonlarga mos (ekin, hudud, texnologiya mos, amal qilish muddatida).
2. `NOT_ELIGIBLE_UNDER_VERIFIED_RULE` — Qonun qoidasiga binoan to'g'ri kelmaydi (masalan, paxta o'rniga meva ekilgan yoki muddati o'tgan qarz mavjud).
3. `MORE_INFORMATION_REQUIRED` — Qo'shimcha ma'lumot talab etiladi (masalan, ekin maydoni 0 ko'rsatilgan).
4. `OUTSIDE_EFFECTIVE_PERIOD` — Dasturning amal qilish muddatidan tashqarida (kuchga kirish sanasidan oldin yoki muddati o'tgan).
5. `RULE_NOT_VERIFIED` — Huquqiy asos rasmiy Lex.uz bazasida to'liq tasdiqlanmagan.

---

## 3. Dasturiy Modullar Tuzilishi

```
backend/app/subsidies/
├── schemas.py           # Pydantic shartnomalari (Dasturlar, so'rovlar, natijalar)
├── rule_registry.py     # PQ-47 va PF-82 bo'yicha rasmiy qoidalar bazasi
├── eligibility.py       # 5-statusli saralash dvigateli
├── calculators.py       # PQ-47 va PF-82 bo'yicha deterministik hisob-kitoblar
├── program_matcher.py   # Ko'p dasturli solishtirish va tartiblash
├── service.py           # Yagona fasad va moliyaviy ta'sir sintezi
└── __init__.py
```

---

## 4. Kassa Oqimi va DSCR Bilan Bog'liqlik Tamoyillari

- **Tarixiy Kassa:** Tasdiqlangan bank ko'chirmasida aks etmagan subsidiya tarixiy operatsion kassa oqimiga aslo qo'shilmaydi.
- **Prognoz Kassa:** PQ-47 bo'yicha subsidiyalar 2 bosqichda kutiladi:
  - 1-bosqich: Uskuna o'rnatilib komissiya dalolatnomasi tuzilgach — **50% dastlabki tushum**;
  - 2-bosqich: 1 vegetatsiya mavsumi yakunida texnologiya ishlaganligi tasdiqlangach — **50% shartli tushum**.
- **Kredit DSCR:** PF-82 bo'yicha 10 foiz bandi va PQ-47 bo'yicha 4 foiz bandi kompensatsiyasi yillik qarzga xizmat ko'rsatish xarajatlarini pasaytirib, DSCR ko'rsatkichini 0.15 - 0.35 punktga oshiradi.
