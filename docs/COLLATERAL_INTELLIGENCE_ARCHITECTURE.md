# AgroHisob CFO — Qishloq Xo'jaligi Garov Intellekti Arxitekturasi (Module A)

## 1. Modul Maqsadi va Umumiy Ko'rinish

O'zbekiston Respublikasi Vazirlar Mahkamasining 2025-yil 30-sentabrdagi 613-son qarori (**VMQ-613**) «Qishloq xo'jaligiga mo'ljallangan yer uchastkalarini ijaraga berish huquqini kredit ta'minoti sifatida garovga qo'yish tartibi to'g'risida»gi normativ hujjat hisoblanadi.

AgroHisob CFO platformasining **Garov Intellekti (Collateral Intelligence)** moduli fermer xo'jaliklariga:
1. Yer ijara huquqining garovga qabul qilinish huquqiy tayyorgarligini avtomatlashtirilgan tarzda tekshirish;
2. Kalendar asosida 5 yillik post-kredit bufer muddatini xatosiz hisoblash;
3. Cheklangan ijara ufqiga asoslangan indikativ DCF (diskontlangan pul oqimi) bozor qiymatini modellashtirish;
4. Uch ssenariyli (Bazaviy, Optimistik, Pessimistik) sezgirlik tahlilini yuritish;
5. Tijorat banki kredit qo'mitasiga taqdim etiladigan 9 ta me'yoriy hujjatdan iborat tayyorgarlik nazorat ro'yxatini shakllantirish imkonini beradi.

---

## 2. Dasturiy Arxitektura va Ma'lumotlar Oqimi

```
[ Frontend: /collateral-subsidies ]
            │
            ▼ (JSON API)
[ FastAPI Router: /api/v1/collateral ]
            │
            ├─► screen_land_lease_collateral()  [eligibility.py]
            │     └─► VMQ-613 5 yillik bufer, kadastr, taqiq, sub-ijara tekshiruvi
            │
            ├─► calculate_indicative_lease_valuation()  [valuation.py]
            │     └─► Cheklangan DCF modeli: PV = Σ [CF_t / (1+r)^t] (Terminal qiymatsiz)
            │
            ├─► run_collateral_sensitivity_analysis()  [sensitivity.py]
            │     └─► Bazaviy, Optimistik (-200bps, +15%), Pessimistik (+300bps, -20%)
            │
            ├─► build_collateral_checklist()  [document_checklist.py]
            │     └─► 9 ta me'yoriy hujjat monitoringi & foizli tayyorgarlik
            │
            └─► DossierBuilder.build_dossier()  [dossier_builder.py]
                  └─► CreditDossierData ga integratsiya (0% tafovut kafolati)
```

---

## 3. Asosiy Komponentlar

1. **`backend/app/collateral/schemas.py`**:
   Pydantic shartnomalari (`LandLeaseProfile`, `VMQ613ScreeningResult`, `IndicativeValuationRequest`, `IndicativeValuationResult`, `CollateralSensitivityAnalysis`, `CollateralDocumentChecklist`, `CollateralPreparationSummary`).
2. **`backend/app/collateral/eligibility.py`**:
   Qat'iy kalendar arifmetikasi (`_add_years_calendar_aware`) orqali kabisa yillarini (29-fevral) hisobga oluvchi 5 yillik bufer tekshiruvi, Davlat kadastri ro'yxati, sud nizolari, taqiqlar va ikkilamchi ijara huquqi screeningi.
3. **`backend/app/collateral/valuation.py`**:
   Cheklangan ufq bo'yicha diskontlangan pul oqimi (DCF) indikativ baholash dvigateli. Tuproq bonitet tuzatmasi ($Bonitet / 65$), terminal qiymatni mutlaqo inkor etuvchi sof diskontlash va bank LTV me'yori (65%).
4. **`backend/app/collateral/sensitivity.py`**:
   Gektariga sof daromad va diskont stavkasi tebranishlarini mustaqil modellashtiruvchi ko'p ssenariyli sezgirlik mexanizmi.
5. **`backend/app/collateral/document_checklist.py`**:
   VMQ-613 va bank anderrayting talablari bo'yicha 9 ta rasmiy hujjatning mavjudligi, talab qilinishi va yetishmovchiligini kuzatuvchi nazorat ro'yxati.
6. **`backend/app/collateral/service.py`**:
   Barcha modullarni birlashtiruvchi yagona fasad servisi.

---

## 4. Rasmiy Ogohlantirish (Disclaimer Invarianti)

Barcha natijalar va API javoblari quyidagi majburiy huquqiy matn bilan ta'minlanadi:
> «Mazkur hisob-kitob indikativ (namunaviy) vosita bo'lib, «Baholash faoliyati to'g'risida»gi Qonunga muvofiq litsenziyalangan mustaqil baholovchi tashkilotning rasmiy hisoboti yoki tijorat bankining qat'iy kredit qarori o'rnini bosmaydi.»
