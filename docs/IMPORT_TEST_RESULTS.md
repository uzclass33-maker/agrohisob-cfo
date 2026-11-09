# AGROHISOB CFO — IMPORT ENGINE COMPREHENSIVE TEST RESULTS

**Hujjat kodi:** `DOC-AGRO-A3-TST-008`  
**Holati:** TASDIQLANGAN (APPROVED)  
**Versiya:** 1.0.0  
**Sinov o'tkazilgan sana:** 2026-yil 9-noyabr  
**Test platformasi:** Pytest 9.2.0 / Python 3.12.14 / Next.js 14 SSR  

---

## 1. TESTLAR XULOSASI (TEST SUMMARY)

AgroHisob CFO platformasining barcha birlik (unit), integratsion va E2E testlari muvaffaqiyatli yakunlandi:

- **Jami testlar soni:** 91 ta
- **Muvaffaqiyatli o'tganlar (Passed):** 91 ta (**100%**)
- **Muvaffaqiyatsiz (Failed):** 0 ta (**0%**)
- **Ogohlantirishlar (Warnings):** 1 ta (FastAPI testclient deprecation)
- **Umumiy ijro vaqti:** 7.95 soniya

---

## 2. MODULLAR KESIMIDA TEST NATIJALARI

| Test Moduli Fayli | Sinovdan O'tgan Funksionallik | Testlar Soni | Holat |
|---|---|---|---|
| `test_import_file_validation.py` | CSV/XLSX validatsiyasi, MIME, hajm cheklovi, bo'sh fayl, VBA makros blokirovkasi, SHA-256 xesh | 7 ta | **PASSED** |
| `test_import_column_mapping.py` | Ko'p tilli ustun moslashtirish (lotin, kirill, rus), majburiy ustunlar tekshiruvi, sample extractor | 5 ta | **PASSED** |
| `test_import_normalization.py` | O'zbek raqam formatlari (`1 250 000,50 so'm`), ISO/MDH/Excel sanalar, 9 xonali STIR/INN, MXIK kodi | 4 ta | **PASSED** |
| `test_import_classification.py` | 1-bosqich (MXIK), 2-bosqich (Kalit so'zlar), 3-bosqich (Kontragent), 4-bosqich (Fallback) | 4 ta | **PASSED** |
| `test_import_duplicates.py` | SHA-256 fayl dublikatlari, qator kanonik barmoq izi (fingerprint), partiya ichidagi dublikatlar | 3 ta | **PASSED** |
| `test_import_ledger_separation.py` | E-faktura kassa balansiga ta'sir qilmasligi, bank ko'chirmasi kassa balansini oshirishi, solishtiruv | 4 ta | **PASSED** |
| `test_api_imports.py` | API upload (`.csv`, `.xlsx`), dublikat 409 xatoligi, qator toifasini o'zgartirish (override), commit & DSCR | 4 ta | **PASSED** |
| `test_api_finance.py` | Finance router (cashflow, loans, dscr, forecast, scenarios) | 5 ta | **PASSED** |
| `test_api.py` | Tizim salomatligi, stsenariylar, stress test, kredit xulosasi | 12 ta | **PASSED** |
| `test_engine_*.py` | Moliya dvigateli (cashflow, loans, dscr, forecasting, risk, scenarios) | 26 ta | **PASSED** |
| `test_financial_calculations.py` | Moliyaviy invariantlar (A, B, C, D, E testlari) | 5 ta | **PASSED** |
| `test_financial_engine.py` | VMQ-613 formulasi, DSCR koeffitsientlari | 3 ta | **PASSED** |
| `test_scenarios.py` | 3 ta sintetik agro stsenariy va fermer mavsumiyligi | 3 ta | **PASSED** |
| `test_e2e_journey.py` | Foydalanuvchining to'liq yo'li (backend + frontend) | 6 ta | **PASSED** |
| **JAMI** | **AgroHisob CFO To'liq Test To'plami** | **91 ta** | **100% PASSED** |

---

## 3. QABUL QILISH MEZONLARI (ACCEPTANCE CRITERIA) STATUSI

- **AC-01 (CSV & XLSX yuklash):** To'liq bajarildi.
- **AC-02 (Fayl hajmi va xavfsizlik):** 10 MB cheklovi va VBA makros blokirovkasi tatbiq etildi.
- **AC-03 (SHA-256 fayl dublikat nazorati):** To'liq bajarildi.
- **AC-04 (Ko'p tilli ustun moslashtirish):** Lotin, kirill va rus tillaridagi 12 ta kanonik ustun qamrab olindi.
- **AC-05 (Mahalliy raqam normalizatsiyasi):** Bo'shliqlar, vergul, valyuta suffikslari `Decimal`ga o'tkazildi.
- **AC-06 (Sana normalizatsiyasi):** ISO, MDH va Excel seriya sanalari to'g'ri o'qildi.
- **AC-07 (STIR va MXIK tekshiruvi):** 9 xonali STIR va MXIK prefikslari tekshirildi.
- **AC-08 (1-bosqich MXIK toifalash):** 01.11, 01.16, 20.15, 19.20 va boshqalar 95-98% aniqlikda ishlamoqda.
- **AC-09 (2-bosqich Kalit so'z toifalash):** O'zbek/rus agro atamalar 90-92% aniqlikda ishlamoqda.
- **AC-10 (3-bosqich Kontragent toifalash):** Farg'onaAzot, O'zbekneftgaz, Agrobank va boshqalar tanildi.
- **AC-11 (Zaxira toifalash):** Tasniflanmagan kirim/chiqim 30% ishonchlilik bilan belgilandi.
- **AC-12 (Qator barmoq izi):** Intra-batch va bazaviy dublikatlar aniqlandi.
- **AC-13 (Ledger Separation Invarianti):** E-faktura kassa balansini o'zgartirmasligi qat'iy ta'minlandi.
- **AC-14 (Bank aylanmasi kassa integratsiyasi):** Bank tranzaksiyalari kassa balansini va DSCRni yangilamoqda.
- **AC-15 (O'zaro solishtiruv - Reconciliation):** Invoyslar bank to'lovlari bilan bog'landi.
- **AC-16 (Qoralama ko'rish - Preview API):** Xaritalash, statuslar va moliyaviy jami ko'rsatkichlar berilmoqda.
- **AC-17 (Qo'lda tahrirlash - Override API):** Foydalanuvchi toifani va summani to'g'rilashi mumkin.
- **AC-18 (Bazaga tasdiqlash - Commit API):** Yaroqli qatorlar tanlangan reestrga yozilmoqda.
- **AC-19 (Audit jurnali - History API):** Barcha import partiyalari xronologik tartibda saqlanmoqda.
- **AC-20 (Next.js foydalanuvchi interfeysi):** 5 bosqichli to'liq interaktiv UI yaratildi va static builddan o'tdi.
- **AC-21 (Regressiyasiz to'liq test qamrovi):** 91/91 test muvaffaqiyatli o'tdi.
