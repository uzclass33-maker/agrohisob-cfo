# AGROHISOB CFO — MOLIYAVIY HISOBLASH DVIGATELI SPETSIFIKATSIYASI
## Financial Calculation Engine Architecture Specification (Assignment 2)

---

## 1. Dvigatel Falsafasi va Asosiy Prinsiplari

**AgroHisob CFO** platformasining moliyaviy hisoblash dvigateli O'zbekiston agrobiznes subyektlari (fermerlar, klasterlar, eksportyorlar) va tijorat banklari (xususan ATB «Agrobank») anderrayting standartlariga xizmat qiluvchi deterministik tizimdir.

### Asosiy Prinsiplar:
1. **Sof Determinizm:** Hech qanday LLM yoki generativ model moliyaviy raqamlar va kassa balanslarini hisoblashda ishtirok etmaydi. Barcha raqamlar qat'iy matematik formulalar orqali olinadi.
2. **`Decimal` Arifmetikasi:** Suzuvchi nuqtali (binary float IEEE 754) yaxlitlash xatolarini yo'qotish uchun barcha pul qiymatlari Python `Decimal` turida hisoblanadi va `Decimal('0.01')` aniqligida `ROUND_HALF_UP` qoidasi bilan yaxlitlanadi.
3. **Buxgalteriya Invariantlari:**
   - Kassa qoldig'i balansi: $\text{Closing}_t = \text{Opening}_t + \text{Inflows}_t - \text{Outflows}_t$
   - Uzluksizlik (Roll-forward): $\text{Opening}_{t+1} \equiv \text{Closing}_t$
   - Yillik rekonsilyatsiya: $\text{Closing}_{12} \equiv \text{Opening}_1 + \sum \text{Inflows} - \sum \text{Outflows}$
4. **Tarixiy Haqiqat va Kelajak Prognozining Ajratilishi:**
   - Tarixiy kassa tushumlari faqat tasdiqlangan bank/kassa harakatlariga tayanadi (accrual daromadlar kassa tushumi sifatida ko'rsatilmaydi).
   - Prognozlar esa aniq agronomik ekin kalendari, hosildorlik va xarajatlar taqvimiga asoslanadi.

---

## 2. Modulli Paket Tuzilishi (`backend/app/financial_engine/`)

```
backend/app/financial_engine/
├── __init__.py           # Paket eksportlari va API interfeysi
├── schemas.py            # Pydantic v2 kirish va chiqish sxemalari
├── exceptions.py         # Maxsus moliyaviy va validatsiya istisnolari
├── cashflow.py           # Tarixiy kassa oqimlarini tahlil qilish va agregatsiya
├── loans.py              # Annuitet va differensial kredit amortizatsiyasi
├── dscr.py               # CFADS va qarzga xizmat ko'rsatish koeffitsienti
├── forecasting.py        # 12 oylik mavsumiy agrar prognozlash
├── scenarios.py          # Baza, optimistik, pessimistik va maxsus ssenariylar
└── risk.py               # Deterministik likvidlik xatarlari va ogohlantirishlar
```

---

## 3. Asosiy Formulalar va Matematik Metodologiya

### 3.1. Kassa Balansi Oqimi (`cashflow.py`)
Har bir $t$ oyi uchun:
$$\text{Net Cash Flow}_t = \sum \text{Inflow}_t - \sum \text{Outflow}_t$$
$$\text{Closing Balance}_t = \text{Opening Balance}_t + \text{Net Cash Flow}_t$$
$$\text{Opening Balance}_{t+1} = \text{Closing Balance}_t$$

### 3.2. Kredit Amortizatsiyasi (`loans.py`)
1. **Annuitet To'lov (Teng to'lovlar):**
   $$A = P \times \frac{r(1+r)^n}{(1+r)^n - 1}$$
   Bu yerda:
   - $P$ — asosiy qarz summasi (UZS)
   - $r$ — davriy foiz stavkasi (yillik stavka / 12)
   - $n$ — amortizatsiya davrlari soni (oylar)
   - Agar $r = 0$ bo'lsa: $A = P / n$.
   - Imtiyozli davrda faqat foiz to'lanadi: $I = P \times r$, asosiy qarz kamaymaydi.

2. **Teng Asosiy Qarz (Differensial to'lov):**
   $$P_{\text{to'lov}} = \frac{P}{n} \quad (\text{o'zgarmas})$$
   $$I_t = \text{Qoldiq Asosiy Qarz}_{t-1} \times r$$
   $$\text{Jami Oylik To'lov}_t = P_{\text{to'lov}} + I_t$$

### 3.3. Qarzga Xizmat Ko'rsatish Koeffitsienti (`dscr.py`)
$$\text{CFADS} = \text{Operatsion Kassa Tushumlari} - \text{Operatsion Xarajatlar (qarz to'lovlaridan tashqari)}$$
$$\text{Total Debt Service} = \text{Asosiy Qarz To'lovi} + \text{Foiz To'lovi}$$
$$\text{DSCR} = \frac{\text{CFADS}}{\text{Total Debt Service}}$$

- Agar qarz to'lovi 0 bo'lsa: `has_debt = False`, `dscr = None` (bo'lish xatoligisiz).
- Agar CFADS $\le 0$ bo'lsa: `status_tier = "INSUFFICIENT"`, korxona kritik defitsitda.

### 3.4. Mavsumiy Prognozlash (`forecasting.py`)
- Ekin daromadi:
  $$\text{Kutilgan Hosil (tonna)} = \text{Maydon (ga)} \times \text{Hosildorlik (t/ga)}$$
  $$\text{Yalpi Tushum} = \text{Hosil (tonna)} \times \text{Sotish Narxi (so'm/tonna)}$$
- Hosil oylari va tushumlar kechikishi (collection delay) inobatga olinib, kassa tushumi $h_{\text{oy}} + \text{delay}$ oyiga yoziladi.

---

## 4. Versiyalangan API Endpointlari

| HTTP Metod | URL Yo'nalishi | Vazifasi |
|---|---|---|
| `POST` | `/api/v1/finance/cashflow/analyze` | Tarixiy kassa oqimlarini tahlil qilish va rekonsilyatsiya |
| `POST` | `/api/v1/finance/forecast` | 12 oylik mavsumiy kassa prognozini hisoblash |
| `POST` | `/api/v1/finance/loans/schedule` | Kredit to'lov jadvalini (annuitet/differensial) hisoblash |
| `POST` | `/api/v1/finance/dscr/calculate` | CFADS va DSCR koeffitsientini hisoblash |
| `POST` | `/api/v1/finance/scenarios/analyze` | Baza, optimistik, pessimistik ssenariylarni to'liq qayta hisoblash |
