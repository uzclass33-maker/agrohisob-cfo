# AgroHisob CFO — Assignment 6 Test Natijalari va Qabul Mezonlari Matritsasi

## 1. Test Sessiyasi Xulosasi
- **Jami testlar soni:** 153 ta
- **Muvaffaqiyatli o'tgan testlar:** 153 ta (100%)
- **Muvaffaqiyatsiz testlar:** 0 ta
- **Ogohlantirishlar:** 1 ta (Starlette deprecation warning)
- **Umumiy ijro vaqti:** ~10.9 soniya
- **Test muhiti:** Python 3.12, Pytest 9.2, FastAPI TestClient, Next.js 14.2

---

## 2. Acceptance Criteria (AC-01 — AC-26) Matritsasi

| AC ID | Qabul Mezoni Tavsifi | Holat | Tekshiruvchi Test Fayli |
|---|---|---|---|
| **AC-01** | Qishloq xo'jaligi yer ijara huquqi profili maydonlari (kadastr, maydon, muddatlar, cheklovlar) | **PASSED** | `test_collateral_subsidies_api.py` |
| **AC-02** | VMQ-613 qat'iy kalendar asosidagi 5 yillik post-kredit bufer tekshiruvi | **PASSED** | `test_collateral_eligibility.py` |
| **AC-03** | Davlat ro'yxatidan o'tganlik va kadastr raqami tekshiruvi | **PASSED** | `test_collateral_eligibility.py` |
| **AC-04** | Taqiq, arest, xatlov va sud nizolari screeningi | **PASSED** | `test_collateral_eligibility.py` |
| **AC-05** | Ikkilamchi ijara (sub-lease) bo'yicha yozma ruxsatnoma tekshiruvi | **PASSED** | `test_collateral_eligibility.py` |
| **AC-06** | Litsenziyali mustaqil baholash hisoboti sharti monitoringi | **PASSED** | `test_collateral_eligibility.py` |
| **AC-07** | Cheklangan ijara ufqiga asoslangan indikativ DCF baholash modeli | **PASSED** | `test_collateral_valuation.py` |
| **AC-08** | Asossiz cheksiz terminal qiymat mutlaqo qo'shilmasligi | **PASSED** | `test_collateral_valuation.py` |
| **AC-09** | Tuproq boniteti bo'yicha tuzatma (Bonitet / 65) | **PASSED** | `test_collateral_valuation.py` |
| **AC-10** | Tijorat banki LTV me'yori (65%) asosida garov ta'minoti summasi | **PASSED** | `test_collateral_valuation.py` |
| **AC-11** | Ko'p ssenariyli sezgirlik tahlili (Bazaviy, Optimistik, Pessimistik) | **PASSED** | `test_collateral_valuation.py` |
| **AC-12** | 9 ta rasmiy hujjatdan iborat garov nazorat ro'yxati va foizli tayyorgarlik | **PASSED** | `test_collateral_subsidies_api.py` |
| **AC-13** | Garov bo'yicha rasmiy nodavlat / nosertifikatlangan disclaimer | **PASSED** | `test_e2e_collateral_subsidies_journey.py` |
| **AC-14** | Subsidiya dasturlari versiyalangan reestri (PQ-47, PF-82) | **PASSED** | `test_regulatory_sources.py` |
| **AC-15** | 5 ta deterministik muvofiqlik statusi bo'yicha screening | **PASSED** | `test_subsidies_eligibility.py` |
| **AC-16** | PQ-47 ekin turlari bo'yicha bazaviy stavkalar (Paxta: 8M, Sabzavot: 6M, Bog': 10M, Uzum: 8M) | **PASSED** | `test_subsidies_pq47.py` |
| **AC-17** | PQ-47 hududiy koeffitsiyenti (1.2x suv tanqis hududlar) | **PASSED** | `test_subsidies_pq47.py` |
| **AC-18** | PQ-47 50/50 bosqichma-bosqich ajratish modeli | **PASSED** | `test_subsidies_pq47.py` |
| **AC-19** | PQ-47 kredit bo'yicha 4 foiz bandi foiz kompensatsiyasi | **PASSED** | `test_subsidies_pq47.py` |
| **AC-20** | PF-82 paxta va g'alla kreditlari bo'yicha 10 foiz bandi kompensatsiyasi | **PASSED** | `test_subsidies_pf82.py` |
| **AC-21** | PF-82 muddati o'tgan qarzdorlik bo'lganda to'liq rad etish | **PASSED** | `test_subsidies_pf82.py` |
| **AC-22** | PF-82 haqiqiy qoldiq va kunlik intizomli so'ndirish arifmetikasi | **PASSED** | `test_subsidies_pf82.py` |
| **AC-23** | Kassa oqimi va DSCR ta'sirini baholash (tarixiy kassa bilan aralashmaslik) | **PASSED** | `test_subsidies_eligibility.py` |
| **AC-24** | Credit Dossier (Assignment 5) ga garov va subsidiya integratsiyasi | **PASSED** | `test_e2e_collateral_subsidies_journey.py` |
| **AC-25** | To'liq interaktiv Next.js frontend sahifasi (`/collateral-subsidies`) | **PASSED** | `test_live_audit_run.py` |
| **AC-26** | 0% tafovut va barcha ko'rinishlarda yagona raqamlar invarianti | **PASSED** | `test_e2e_collateral_subsidies_journey.py` |
