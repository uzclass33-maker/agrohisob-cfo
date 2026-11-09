# AgroHisob CFO — AI-CFO Boshqaruv Paneli Arxitekturasi (Assignment 4)

## 1. Umumiy Arxitektura Ko'rinishi

AgroHisob CFO platformasi agrobiznes korxonalari uchun mo'ljallangan sun'iy intellektga asoslangan Virtual Bosh Moliyaviy Direktor (AI-CFO) boshqaruv panelini taqdim etadi. Tizim qat'iy ikki qatlamli (Two-Layer) arxitekturaga asoslangan:

1. **Layer A — Deterministik Moliyaviy Dvigatel (Deterministic Financial Engine v4.0.0)**:
   - Barcha kassa oqimlari, kredit amortizatsiyalari, DSCR ko'rsatkichlari, mavsumiy prognozlar va xatarlarni aniq matematik formulalar asosida hisoblaydi.
   - Barcha hisob-kitoblar `backend/app/financial_engine/` paketida amalga oshiriladi.
   - Frontend hech qachon o'zboshimchalik bilan moliyaviy ko'rsatkichlarni masshtablamaydi yoki klasterlamaydi; har bir qiymat backend orqali olinadi.

2. **Layer B — Maxfiylik Kafolatlangan Tahliliy Tushuntirish Qatlami (Privacy-Preserving Explanation Layer)**:
   - Hech qanday maxfiy bank hisobraqamlari, STIR/INN yoki individual schyot-fakturalar tashqi LLM servislariga yuborilmaydi.
   - FAQAT Layer A tomonidan tasdiqlangan va agregatlangan umumiy ko'rsatkichlar tahlil qilinadi.
   - Factual Numerical Claim Verification: LLM matnidagi har bir raqamli fakt tekshiriladi va gallyutsinatsiya holatida 100% Layer A deterministik qoidalariga fallback qilinadi.

---

## 2. 7 ta Asosiy Boshqaruv Modullari

```
+-----------------------------------------------------------------------------------+
|                         AGROHISOB CFO DASHBOARD (v4.0.0)                          |
+-----------------------------------------------------------------------------------+
| 1. Ijroiya Xulosa (Executive Financial Overview)                                  |
|    - 7 ta asosiy KPI (Tushum, Chiqim, Sof Oqim, Qoldiq, Opex, Qarz, DSCR)         |
|    - Eng past kassa nuqtasi va taqchillik oylari monitoringi                      |
+-----------------------------------------------------------------------------------+
| 2. Kassa Oqimlari Intellekti (Cash-Flow Intelligence)                             |
|    - 12 oylik dinamika grafigi (Recharts ComposedChart)                            |
|    - Toifalar bo'yicha tushum va chiqim taqsimoti (O'g'it, Yoqilg'i, Ish haqi...) |
|    - Roll-forward reconciliation jadvali: Closing(t) = Opening(t) + Net(t)        |
+-----------------------------------------------------------------------------------+
| 3. 12 Oylik Mavsumiy Prognoz (Seasonal Forecasting)                               |
|    - Ekin maydonlari, hosildorlik va agrar mavsumiylik kalendari                  |
|    - Interaktiv farazlar paneli va qayta hisoblash mexanizmi                      |
+-----------------------------------------------------------------------------------+
| 4. Qarz & DSCR Ko'rsatkichlari (Debt & DSCR Analytics)                            |
|    - Asosiy qarz vs Foiz to'lovlari taqsimoti                                     |
|    - Bank talablari bo'yicha DSCR risk benchmarklari (<1.0x, 1.0-1.2x, >=1.5x)    |
|    - Amortizatsiya jadvallari va garov ta'minoti reyestri                         |
+-----------------------------------------------------------------------------------+
| 5. Moliyaviy Xavflar Monitori (Risk Monitoring)                                   |
|    - Deterministik trigger qoidalari (Defitsit, Past bufer, Qarz bosimi)          |
|    - Xavflilik darajasi: CRITICAL, HIGH, MEDIUM, LOW                              |
|    - Amaliy biznes boshqaruv choralari va tavsiyalari                             |
+-----------------------------------------------------------------------------------+
| 6. Ssenariylar Simulyatsiyasi (Interactive Scenario Simulation)                   |
|    - Baza (0%), Optimistik (+20%/-10%), Pessimistik (-20%/+15%), Maxsus           |
|    - 4 ta slayder (Tushum, Xarajat, Kechikish, Foiz stavkasi)                     |
|    - Backend orqali to'liq qayta hisoblash (/api/v1/dashboard/scenarios)          |
+-----------------------------------------------------------------------------------+
| 7. AI-CFO Strategik Xulosalari (AI Insights Engine)                               |
|    - Korxona moliyaviy salomatligi xulosasi (Health Summary)                      |
|    - Tasdiqlangan dalillar va raqamli faktlar reyestri                            |
|    - Maxfiy LLM tushuntirishi va 100% deterministik fallback kafolati             |
+-----------------------------------------------------------------------------------+
```

---

## 3. API Routerlari va Yo'nalishlar

- `GET /api/v1/dashboard/overview`: 7 ta asosiy KPI, boshlang'ich/yakuniy qoldiqlar, kassa uzilishi oylari.
- `GET /api/v1/dashboard/cashflow`: Oylik tushum va chiqimlar, toifaviy taqsimot, roll-forward tekshiruvi.
- `GET /api/v1/dashboard/forecast`: 12 oylik agrar prognoz, ekinlar rejasi, eng past kassa nuqtasi.
- `GET /api/v1/dashboard/debt`: Kredit portfeli, amortizatsiya jadvallari, DSCR darajasi.
- `GET /api/v1/dashboard/risks`: Deterministik risk qoidalari natijalari va boshqaruv choralari.
- `POST /api/v1/dashboard/scenarios`: Muqobil ssenariylar simulyatsiyasi va farqlar tahlili.
- `GET /api/v1/insights`: AI-CFO tahliliy xulosalari, faktlar va tavsiyalar.
- `POST /api/v1/insights/explain`: Muayyan ko'rsatkich yoki xatar bo'yicha chuqur tushuntirish.
