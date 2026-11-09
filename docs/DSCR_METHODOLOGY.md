# AGROHISOB CFO — DSCR METODOLOGIYASI (DEBT SERVICE COVERAGE RATIO)
## Cash Flow Available for Debt Service (CFADS) & Bank Underwriting Capacity

---

## 1. Nazariy Asoslar

Qarzga Xizmat Ko'rsatish Koeffitsienti (**Debt Service Coverage Ratio — DSCR**) qishloq xo'jaligi korxonasining sof operatsion kassa oqimi uning mavjud qarz to'lovlarini (asosiy qarz va foizlar) necha barobar qoplay olishini ko'rsatuvchi muhim anderrayting mezonidir.

AgroHisob CFO platformasida DSCR quyidagi aniq formula bo'yicha hisoblanadi:

$$\text{DSCR} = \frac{\text{CFADS}}{\text{Total Debt Service}}$$

Bu yerda:
- **CFADS (Cash Flow Available for Debt Service):**
  $$\text{CFADS} = \text{Operatsion Kassa Tushumlari} - \text{Operatsion Xarajatlar (qarz to'lovlarisiz)}$$
- **Total Debt Service (Jami qarz xizmati):**
  $$\text{Total Debt Service} = \text{Asosiy Qarz To'lovi} + \text{Foiz To'lovi}$$

---

## 2. Maxsus Holatlar va Chegaraviy Qiymatlar

1. **Qarz Majburiyati Mavjud Bo'lmaganda (`Total Debt Service == 0`):**
   - Ko'p hollarda `0` ga bo'lish xatosi (`ZeroDivisionError`) yuzaga keladi.
   - AgroHisob CFO da bu holatda `dscr = None` va `status_tier = "NO_DEBT"` qaytariladi, korxona to'liq o'z mablag'lari hisobiga ishlayotgani ko'rsatiladi.
2. **Manfiy CFADS (`CFADS < 0`):**
   - Agar korxona operatsion faoliyatidan zarar ko'rayotgan bo'lsa, DSCR salbiy chiqadi.
   - Bu holatda tizim `is_acceptable = False` va `CRITICAL` darajadagi ogohlantirishni faollashtiradi: korxona qarzga xizmat ko'rsata olmaydi.

---

## 3. Anderrayting Tavsiyaviy Mezonlari (Illustrative Risk Bands)

| DSCR Oralig'i | Holat Kategoriya | Tavsif va Bank Xulosasi |
|---|---|---|
| **$\text{DSCR} \ge 1.50$x** | `STRONG` | Mustahkam va barqaror qoplash darajasi. Qo'shimcha kredit limiti ajratilishi mumkin. |
| **$1.20 \le \text{DSCR} < 1.50$x** | `MODERATE` | Mo'tadil qoplash darajasi. O'zbekiston banklarining 1.25x lik minimal anderrayting talabiga mos. |
| **$1.00 \le \text{DSCR} < 1.20$x** | `LIMITED` | Cheklangan qoplash darajasi. Daromad biroz pasaysa, kassa uzilishi xavfi mavjud. |
| **$\text{DSCR} < 1.00$x** | `INSUFFICIENT` | Yetarsiz qoplash darajasi. Kassa oqimi qarz to'lovlarini to'liq qoplamaydi, defolt xatari. |
