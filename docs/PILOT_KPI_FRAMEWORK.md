# AGROHISOB CFO — PILOT METRIKALAR VA KPI ASOSLARI (PILOT KPI FRAMEWORK)

**Sana:** 2026-yil 9-noyabr  
**Maqsad:** Pilot davrida vaqt tejalishi, moliyaviy aniqlik va tijorat qiziqishini o'lchashning qat'iy matematik tizimi.

---

## 1. AMALIY METRIKALAR MATRITSASI

| KPI Kodi | Metrika Nomi | Hisoblash Formulasi | O'lchov Birligi | Boshlang'ich Holat (Baseline) | Pilot Maqsadi (Target) | Joriy Natija | Tekshiruv Dalili |
|---|---|---|---|---|---|---|---|
| **KPI-OP-01** | Hujjatlarni import qilish vaqti | $Time_{import} = T_{upload\_end} - T_{upload\_start}$ | Daqiqa | 8-12 soat (qo'lda Excelga yig'ish) | $\le 15$ daqiqa | MVP simulyatsiyasida < 1s | `test_import_normalization.py` |
| **KPI-OP-02** | Tejalgan umumiy vaqt | $Time\ Saved = \frac{T_{base} - T_{prod}}{T_{base}} \times 100\%$ | Foiz (%) | 0% | $\ge 70\%$ | Pilot o'lchovi kutilmoqda | Baseline formasi |
| **KPI-OP-03** | Importdagi xatoliklar darajasi | $\frac{Failed\ Imports}{Total\ Imports} \times 100\%$ | Foiz (%) | Excelda 15-20% formulaviy xato | $\le 2.0\%$ | Avtomatlashgan testlarda 0% | `test_import_file_validation.py` |
| **KPI-FIN-01** | DSCR hisoblash aniqligi | $\Delta DSCR = \vert DSCR_{system} - DSCR_{bank} \vert$ | Koeffitsient | Qo'lda hisobda 0.20-0.40 tafovut | $0.00$ (mutlaq moslik) | 0.00% nomuvofiqlik tasdiqlangan | `docs/FINANCIAL_RELEASE_VALIDATION.md` |
| **KPI-FIN-02** | Tranzaksiyalar va bank qoldig'i rekonsilyatsiyasi | $\vert Opening + Inflows - Outflows - Closing \vert$ | UZS | Qo'lda hisobda nomuvofiqliklar uchraydi | $0.00$ so'm farq | 100% balansli | `test_dashboard_cashflow.py` |
| **KPI-REP-01** | Kredit dossiyesi generatsiyasi tezligi | $T_{dossier\_gen}$ | Sekund | Konsaltingda 5-10 kun | $\le 30$ sekund | ~2.5 sekundda tayyor | `test_reports_api.py` |
| **KPI-COM-01** | Tasdiqlangan intervyular | Qayd etilgan `VERIFIED_INTERVIEW` soni | Soni | 0 ta | 15-20 ta | 0 ta (rejalashtirilgan) | Research Tracker API |
| **KPI-COM-02** | Pullik obunaga tayyorlik (Conversion) | $\frac{Paying\ Customers}{Active\ Pilots} \times 100\%$ | Foiz (%) | 0% | $\ge 40\%$ | 0% (hali boshlanmagan) | Haqiqiy to'lov dalili |

---

## 2. METODOLOGIK QAT'IYLIK QOIDASI

- Hech qanday "75% vaqt tejaydi" degan da'vo $T_{base}$ va $T_{prod}$ ikkala ko'rsatkichi ham real pilotda o'lchanmasdan turib investorlarga haqiqat sifatida taqdim etilmaydi.
- Taqdimotlarda ushbu ko'rsatkich aniq qilib **"Ichki MVP benchmarki: <15 daqiqa (rejalashtirilgan tejamkorlik 70%+)"** deb yoziladi.
