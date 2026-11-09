# AGROHISOB CFO — SSENARIYLAR VA SEZGIRLIK TAHLILI (SCENARIO ANALYSIS)
## Multi-Scenario Stress Testing & Deterministic Variance Modeling

---

## 1. Konseptual Yondashuv

Ko'plab sodda dasturlar yakuniy kassa balansini shunchaki biron foizga (masalan, $0.8$ ga) ko'paytirib, "stress-test" deb ataydi. Bu moliyaviy jihatdan qat'iyan noto'g'ri, chunki qishloq xo'jaligida:
- Ekin narxi yoki hosildorlik pasaysa, tushumlar kamayadi, lekin ekin ekish va yoqilg'i xarajatlari o'zgarmasdan qolishi mumkin.
- Shartnomaviy qarz to'lovlari (kredit asosiy qarzi va foizi) daromad kamayganiga qaramasdan qat'iy jadval bo'yicha to'lanishi shart.
- Shuning uchun har bir ssenariyda **barcha birlamchi kiruvchi parametrlar o'zgartirilib, 12 oylik kassa oqimi va kassa uzilishlari boshidan qayta hisoblanadi**.

---

## 2. Standart Ssenariylar Ta'rifi

1. **Baza Ssenariysi (`BASE`):**
   - Fermerning tasdiqlangan agrotexnik rejasi va standart narxlari.
2. **Optimistik Ssenariy (`OPTIMISTIC`):**
   - Bozor narxlari yoki hosildorlik $+20\%$ yuqori.
   - Resurslarni tejash va agrotexnik samaradorlik hisobiga xarajatlar $-10\%$ past.
   - Tushumlar o'z vaqtida kelib tushadi.
3. **Pessimistik Ssenariy (`PESSIMISTIC`):**
   - Qurg'oqchilik, sovuq urishi yoki narxlar tushishi oqibatida daromad $-20\%$ kamayadi.
   - Yoqilg'i va o'g'it inflyatsiyasi hisobiga xarajatlar $+15\%$ oshadi.
   - Eksport yoki xaridorlar tomonidan to'lovlar $+1$ oyga kechikadi.
   - Tijorat stavkasi $+2\%$ ga oshadi.
4. **Maxsus Ssenariy (`CUSTOM`):**
   - Foydalanuvchi tomonidan mustaqil kiritiladigan o'zgarishlar (`revenue_change_pct`, `cost_change_pct`, `collection_delay_months`, `interest_rate_delta_pct`).

---

## 3. Qayta Hisob-Kitob Zanjiri

Har qanday ssenariy o'zgarishi quyidagi to'liq zanjirni boshidan hisoblaydi:
$$\text{Yangi Hosil Narxi} \rightarrow \text{Oylik Tushumlar} \rightarrow \text{Oylik Xarajatlar} \rightarrow \text{Oylik Qarz Xizmati} \rightarrow \text{CFADS} \rightarrow \text{DSCR} \rightarrow \text{Defitsit Oylari} \rightarrow \text{Likvidlik Xatari}$$
