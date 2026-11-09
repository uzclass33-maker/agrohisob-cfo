# AGROHISOB CFO — KREDIT AMORTIZATSIYASI MODELI (LOAN AMORTIZATION)
## Annuity and Equal Principal Debt Schedules with Grace Periods

---

## 1. Qo'llab-Quvvatlanadigan To'lov Sxemalari

AgroHisob CFO platformasi O'zbekiston bank amaliyotida keng qo'llaniladigan 2 ta asosiy to'lov sxemasini to'liq qo'llab-quvvatlaydi:

### 1. Annuitet Sxemasi (Teng Oylik To'lovlar)
- Har bir davrda to'lanadigan jami summa teng bo'ladi ($A$).
- Dastlabki davrlarda foiz to'lovi katta bo'lib, asosiy qarz to'lovi kichik bo'ladi; vaqt o'tishi bilan asosiy qarz to'lovi oshib, foiz qismi kamayadi.
- Formula:
  $$A = P \times \frac{r(1+r)^n}{(1+r)^n - 1}$$
  Bu yerda $P$ — kredit asosiy qarzi, $r$ — oylik foiz stavkasi, $n$ — oylar soni.
  - Agar $r = 0$ bo'lsa (foizsiz davlat subsidiyasi yoki qarz): $A = P / n$.

### 2. Differensial Sxema (Teng Asosiy Qarz To'lovlari)
- Har bir davrda asosiy qarzdan teng miqdor to'lanadi:
  $$P_{\text{oy}} = \frac{P}{n}$$
- Foiz to'lovi qoldiq asosiy qarzga nisbatan hisoblanadi:
  $$I_t = \text{Remaining Principal}_{t-1} \times r$$
- Oylik to'lov vaqt o'tishi bilan kamayib boradi: $\text{Total}_t = P_{\text{oy}} + I_t$.

---

## 2. Imtiyozli Davr (Grace Period) Qoidasi
- Agar `grace_period_months` $> 0$ bo'lsa:
  - Imtiyozli oylarda faqat foiz to'lanadi ($I_t = P \times r$).
  - Asosiy qarz to'lanmaydi ($P_{\text{oy}} = 0$).
  - Imtiyozli davr tugagach, asosiy qarz qolgan davrlar soniga ($n - \text{grace}$) taqsimlanadi.

---

## 3. Qoldiqni Nolga Tushirish Kafolati (Zero Remaining Principal Reconciliation)
- Barcha hisob-kitoblar `Decimal` formatida yuritilib, so'nggi to'lovda qolgan asosiy qarz to'liq yopilishi kafolatlanadi.
- Qoldiq asosiy qarz hech qachon manfiy bo'lmaydi.
