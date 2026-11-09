# AGROHISOB CFO — KASSA OQIMI MODELI (CASH-FLOW MODEL)
## Historical Cash-Flow Analysis & Monthly Continuity Invariants

---

## 1. Nazariy Asoslar va Buxgalteriya Qoidalari

AgroHisob CFO kassa oqimi modeli sof kassa usuliga (Cash Basis Accounting) asoslangan.

### Muhim Qoidalar:
1. **Accrual Daromadlar Man Etiladi:** Faktura berilgan bo'lsa-da, bank hisobvarag'iga yoki kassaga real pul tushmagan bo'lsa, u kassa tushumi sifatida tan olinmaydi.
2. **Qaytarishlar (Reversals/Refunds):** Noto'g'ri o'tkazmalar yoki xaridorga qaytarilgan mablag'lar kassa oqimida `is_reversal=True` belgisi bilan hisobga olinadi va tegishli kassa moddasini kamaytiradi.
3. **Ichki O'tkazmalar (Internal Transfers):** Korxonaning bitta hisobvarag'idan boshqasiga o'tkazilgan mablag'lar daromad yoki xarajat sifatida hisobga olinmaydi (ikki marotaba hisoblash xatosi bartaraf etilgan).
4. **Valyuta Yaxlitligi:** Barcha tranzaksiyalar belgilangan valyutada (standart: `UZS`) bo'lishi shart. Turli valyutalarni avtomat konvertatsiyasiz qo'shish qat'iyan taqiqlangan (`CurrencyMismatchError`).

---

## 2. Formulalar va Balans Tenglamasi

Har bir $t$ oyi uchun ($1 \le t \le 12$):
$$\text{Total Inflows}_t = \sum_{i \in \text{Inflows}} \text{Amount}_{i, t} - \sum_{j \in \text{Inflow Reversals}} \text{Amount}_{j, t}$$
$$\text{Total Outflows}_t = \sum_{k \in \text{Outflows}} \text{Amount}_{k, t} - \sum_{l \in \text{Outflow Reversals}} \text{Amount}_{l, t}$$
$$\text{Net Cash Flow}_t = \text{Total Inflows}_t - \text{Total Outflows}_t$$
$$\text{Closing Balance}_t = \text{Opening Balance}_t + \text{Net Cash Flow}_t$$
$$\text{Opening Balance}_{t+1} \equiv \text{Closing Balance}_t$$

Yillik jamlanma:
$$\text{Final Closing Balance} \equiv \text{Initial Opening Balance} + \sum_{t=1}^{12} \text{Total Inflows}_t - \sum_{t=1}^{12} \text{Total Outflows}_t$$

---

## 3. Ma'lumotlarning To'liqligi va Ishonchliligi (Completeness Indicators)

Har bir tahlil natijasida quyidagi sifat ko'rsatkichlari qaytariladi:
- `transaction_count`: Qayta ishlangan tranzaksiyalar soni.
- `reversal_count`: Bekor qilingan/qaytarilgan operatsiyalar soni.
- `continuity_verified`: Balans uzluksizligi qoidasi $100\%$ bajarilganligining mantiqiy isboti (`True`).
- `rounding_difference_uzs`: Yaxlitlash qoldig'i (har doim `0.00` UZS bo'lishi kafolatlangan).
