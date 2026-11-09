# AGROHISOB CFO — API CONTRACT SPECIFICATION
## Version: 1.0.0-mvp | Protocol: HTTP/REST | Format: JSON

Ushbu hujjat **AgroHisob CFO** B2B SaaS platformasining barcha backend API interfeyslari, so'rov va javob sxemalari, holat kodlari hamda ma'lumotlar invariantlarini belgilaydi.

---

## 1. Umumiy Qoidalar va Konvensiyalar

1. **Baza URL:** `http://127.0.0.1:8000` (mahalliy ishlab chiqish)
2. **Prefikslar:** `/` (tizimli tekshiruvlar), `/api` va `/api/v1` (resurs marshrutlari).
3. **Valyuta va Aniqlik:** Barcha pul mablag'lari O'zbekiston so'mida (`UZS`) ifodalanadi. Moliyaviy arifmetikada 2 xonali kasr aniqligi (`Numeric(18, 2)`) kafolatlanadi.
4. **Matematik Invariant:**
   $$\text{Closing Balance}_t = \text{Opening Balance}_t + \text{Inflows}_t - \text{Outflows}_t$$
   $$\text{Opening Balance}_{t+1} = \text{Closing Balance}_t$$

---

## 2. Tizimli Tekshiruv Endpointlari

### 2.1. `GET /health` yoki `GET /api/health`
Xizmatning tirikligi (liveness) va umumiy sog'lomligini tekshiradi.

- **Status Code:** `200 OK`
- **Response JSON:**
```json
{
  "status": "healthy",
  "service": "agrohisob-backend",
  "version": "1.0.0-mvp",
  "engine": "Python/FastAPI Financial Engine",
  "environment": "development",
  "database": "connected"
}
```

### 2.2. `GET /ready`
Tizimning mijoz so'rovlarini qabul qilishga tayyorligi (readiness) va ma'lumotlar bazasi aloqasini tekshiradi.

- **Status Code:** `200 OK`
- **Response JSON:**
```json
{
  "status": "ready",
  "database": "connected",
  "engine_version": "1.0.0",
  "environment": "development"
}
```

---

## 3. Demo Tashkilotlar va Benchmarklar

### 3.1. `GET /api/v1/demo/organizations` (yoki `/api/scenarios`)
Mavjud sintetik qishloq xo'jaligi korxonalari ro'yxatini qaytaradi.

- **Status Code:** `200 OK`
- **Response JSON:**
```json
[
  {
    "id": "scenario-small-farmer",
    "key": "small_farmer",
    "name": "Andijon Baraka Fermer Xo'jaligi",
    "category": "small_farmer",
    "category_label": "Kichik/O'rta Fermer Xo'jaligi",
    "region": "Andijon viloyati",
    "district": "Asaka tumani",
    "land_hectares": 65.0,
    "soil_bonitet_score": 68,
    "main_crop": "Paxta va Mavsumiy Sabzavotlar (Karam, Pomidor, Piyoz)",
    "has_drip_irrigation": true,
    "has_cold_storage": false,
    "initial_cash_uzs": 45000000.0,
    "annual_revenue_estimate_uzs": 1120000000.0,
    "debt_load_uzs": 144000000.0,
    "description": "65 gektar yer maydoniga ega oilaviy fermer xo'jaligi...",
    "key_dynamics": "Aprel-May oylarida kassa taqchilligi; Sentabr-Noyabrda yuqori tushum; Imtiyozli 14% li Agrobank krediti.",
    "is_synthetic": true,
    "is_demo": true,
    "currency": "UZS"
  },
  {
    "id": "scenario-exporter",
    "key": "exporter",
    "name": "«Samarqand Agro Eksport» MChJ",
    "category": "exporter",
    "category_label": "Meva-Sabzavot Eksportyori",
    "region": "Samarqand viloyati",
    "district": "Urgut tumani",
    "land_hectares": 120.0,
    "soil_bonitet_score": 74,
    "main_crop": "Meva va Uzum (Gilos, Xo'raki uzum, Mayiz)",
    "has_drip_irrigation": true,
    "has_cold_storage": true,
    "initial_cash_uzs": 320000000.0,
    "annual_revenue_estimate_uzs": 4850000000.0,
    "debt_load_uzs": 540000000.0,
    "description": "120 gektar intensiv bog' va 1 000 tonnalik zamonaviy sovutkichli omborga ega...",
    "key_dynamics": "Iyun va Sentabrda eksport cho'qqisi; Muzlatkich elektr va fito-nazorat opex; Tijorat 23.5% li aylanma kredit.",
    "is_synthetic": true,
    "is_demo": true,
    "currency": "UZS"
  },
  {
    "id": "scenario-cluster",
    "key": "cluster",
    "name": "«Qashqadaryo Paxta-G'alla Klasteri»",
    "category": "cluster",
    "category_label": "Vertikal Integratsiyalashgan Agro-Klaster",
    "region": "Qashqadaryo viloyati",
    "district": "Qarshi tumani",
    "land_hectares": 2500.0,
    "soil_bonitet_score": 71,
    "main_crop": "Paxta, Bug'doy va Qayta Ishlash Xomashyosi",
    "has_drip_irrigation": true,
    "has_cold_storage": false,
    "initial_cash_uzs": 1850000000.0,
    "annual_revenue_estimate_uzs": 28400000000.0,
    "debt_load_uzs": 3360000000.0,
    "description": "2 500 gektar ekin maydoniga ega yirik agrosanoat klasteri...",
    "key_dynamics": "Iyun (g'alla) va Oktabr-Noyabr (paxta) tushumlari; Katta hajmdagi yoqilg'i va lizing xarajatlari; 280M/oy kredit xizmati.",
    "is_synthetic": true,
    "is_demo": true,
    "currency": "UZS"
  }
]
```

### 3.2. `GET /api/v1/demo/organizations/{id}`
Muayyan demo tashkilotning to'liq kadastr, agronomik va qarz parametrlari.

- **URL Parametri:** `id` (masalan, `scenario-small-farmer`)
- **Status Code:** `200 OK` (yoki `404 Not Found`)
- **Response JSON:**
```json
{
  "organization": {
    "id": "scenario-small-farmer",
    "name": "Andijon Baraka Fermer Xo'jaligi (Sintetik Demo)",
    "inn": "304819205",
    "legal_type": "FERMER_XOJALIGI",
    "region": "Andijon viloyati",
    "district": "Asaka tumani",
    "land_hectares": 65.0,
    "cadastre_number": "17:03:010203:0492",
    "soil_bonitet_score": 68,
    "main_crop_type": "Paxta va Sabzavot",
    "has_drip_irrigation": true,
    "has_cold_storage": false,
    "cold_storage_capacity_tons": 0.0
  },
  "initial_opening_balance": 45000000.0,
  "debt_schedule": [
    {
      "lender_name": "ATB «Agrobank» Asaka filiali",
      "loan_type": "PREFERENTIAL_STATE_AGRO",
      "contract_number": "AGR-2025/11-042",
      "principal_amount": 100000000.0,
      "outstanding_balance": 88000000.0,
      "annual_interest_rate": 14.0,
      "monthly_payment_total": 12000000.0,
      "monthly_principal": 10000000.0,
      "monthly_interest": 2000000.0,
      "start_date": "2025-03-01",
      "maturity_date": "2027-02-28",
      "collateral_description": "Texnika garovi va uchinchi shaxs kafilligi"
    }
  ],
  "monthly_debt_service": [12000000.0, 12000000.0, 12000000.0, 12000000.0, 12000000.0, 12000000.0, 12000000.0, 12000000.0, 12000000.0, 12000000.0, 12000000.0, 12000000.0],
  "currency": "UZS",
  "is_demo": true,
  "data_source_type": "SYNTHETIC_BENCHMARK"
}
```

### 3.3. `GET /api/v1/demo/organizations/{id}/cashflow`
12 oylik to'liq deterministik kassa oqimini hisoblash va mutanosiblik hisobotini qaytaradi.

- **Status Code:** `200 OK`
- **Response JSON:**
```json
{
  "organization_id": "scenario-small-farmer",
  "organization_name": "Andijon Baraka Fermer Xo'jaligi (Sintetik Demo)",
  "currency": "UZS",
  "reporting_period": "2024",
  "total_inflows": 1125000000.0,
  "total_outflows": 857500000.0,
  "net_cash_flow": 267500000.0,
  "opening_balance": 45000000.0,
  "closing_balance": 312500000.0,
  "total_debt_service": 144000000.0,
  "annual_dscr": 2.858,
  "dscr_rating": "EXCELLENT",
  "months_in_deficit": 2,
  "lowest_cash_point": -16500000.0,
  "lowest_cash_month": "May",
  "is_mathematically_reconciled": true,
  "calculation_version": "1.0.0",
  "data_source_type": "SYNTHETIC_BENCHMARK",
  "monthly_breakdown": [
    {
      "month_number": 1,
      "month_name": "Yanvar",
      "opening_balance": 45000000.0,
      "total_inflows": 0.0,
      "total_outflows": 28000000.0,
      "net_cash_flow": -28000000.0,
      "closing_balance": 17000000.0,
      "debt_service": 12000000.0,
      "dscr": -1.33,
      "is_deficit": false,
      "inflows_breakdown": {"CROP_SALES": 0.0, "STATE_SUBSIDY": 0.0},
      "outflows_breakdown": {"SEEDS_PLANTING": 5000000.0, "FUEL_LUBRICANTS": 4000000.0, "LABOR_SALARIES": 6000000.0, "DEBT_SERVICE": 12000000.0, "UTILITIES_WATER_TAX": 1000000.0}
    }
  ]
}
```

---

## 4. Moliyaviy Hisoblash va Stress-Test API

### 4.1. `POST /api/financials/calculate`
Foydalanuvchi yoki sintetik ma'lumotlar asosida 12 oylik kassa oqimini rekonsilyatsiya qiladi.

- **Request JSON:**
```json
{
  "scenario_id": "scenario-small-farmer",
  "initial_opening_balance": 45000000.0
}
```
- **Xato holatlari:**
  - `422 Unprocessable Entity`: agar `initial_opening_balance < 0` bo'lsa yoki noto'g'ri oylar massivi uzatilsa.

### 4.2. `POST /api/financials/stress-test`
Agro-iqlimiy va bozor shoklarini modellashtirish:
- Hosildorlik shoki (`yield_shock_pct`: masalan `-20.0%`)
- Mahsulot narxi shoki (`price_shock_pct`: masalan `-15.0%`)
- Xarajatlar inflyatsiyasi (`cost_shock_pct`: masalan `+12.0%`)

- **Request JSON:**
```json
{
  "scenario_id": "scenario-small-farmer",
  "yield_shock_pct": -20.0,
  "price_shock_pct": -10.0,
  "cost_shock_pct": 15.0
}
```
- **Response JSON:**
```json
{
  "scenario_id": "scenario-small-farmer",
  "shocks_applied": {
    "yield_shock_pct": -20.0,
    "price_shock_pct": -10.0,
    "cost_shock_pct": 15.0
  },
  "baseline_annual_inflow": 1125000000.0,
  "stressed_annual_inflow": 810000000.0,
  "baseline_dscr": 2.858,
  "stressed_dscr": 1.12,
  "solvency_status": "VULNERABLE",
  "additional_liquidity_needed_uzs": 65000000.0,
  "recommendations": [
    "Bahorgi ekin davri uchun 65M so'mlik aylanma mablag' liniyasi zarur",
    "Xarajatlarni 10% ga optimallashtirish tavsiya etiladi"
  ]
}
```

---

## 5. Bank Kreditiga Tayyorlik Dosyesi (Pre-Underwriting)

### 5.1. `GET /api/reports/credit-readiness/{id}`
Agrobank va boshqa tijorat banklari anderrayting talablariga mos kreditga layoqatlilik skoringini generatsiya qiladi.

- **Status Code:** `200 OK`
- **Response JSON:**
```json
{
  "scenario_id": "scenario-small-farmer",
  "organization_name": "Andijon Baraka Fermer Xo'jaligi",
  "credit_score": 78,
  "rating_tier": "B+",
  "annual_dscr": 2.858,
  "dscr_status": "STRONG_CAPACITY",
  "vmq613_bankable_collateral_uzs": 156420000.0,
  "max_recommended_credit_limit_uzs": 250000000.0,
  "key_strengths": [
    "Muntazam tushumlar va yuqori DSCR ko'rsatkichi",
    "Tomchilatib sug'orish texnologiyasining mavjudligi"
  ],
  "risk_flags": [
    "Aprel-May oylarida mavsumiy kassa uzilishi (deficit)"
  ],
  "disclaimer": "DIQQAT: Ushbu hisobot sintetik modellashtirish natijasidir va bank kafolati hisoblanmaydi."
}
```
