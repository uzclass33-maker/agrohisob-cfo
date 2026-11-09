# AGROHISOB CFO — MAVSUMIY PROGNOZLASH MODELI (FORECASTING MODEL)
## Twelve-Month Agricultural Seasonal Cash-Flow Forecasting

---

## 1. Modellashtirish Yondashuvi

Agromahsulotlar ishlab chiqarish tsiklik xususiyatga ega:
- **Bahor (Mart-May):** Urug'chilik, mineral o'g'itlar, yoqilg'i va texnika xarajatlari yuqori, kassa tushumi deyarli yo'q.
- **Yoz (Iyun-Avgust):** Ertachi ekinlar (bug'doy, meva, sabzavot) hosili va dastlabki tushumlar.
- **Kuz (Sentabr-Noyabr):** Paxta, uzum va kechki ekinlar hosili, asosiy daromad va klasterlar bilan yakuniy hisob-kitoblar.
- **Qish (Dekabr-Fevral):** Sovutgichli omborlardan saqlangan mahsulotlarni sotish va keyingi mavsumga tayyorgarlik.

AgroHisob CFO prognozlash dvigateli ushbu agronomik tsiklni ekinlar bo'yicha parametrlar va xarajatlar taqvimi orqali to'liq aks ettiradi.

---

## 2. Formulalar

### 2.1. Ekin Tushumlari
Har bir ekin $c$ uchun:
$$\text{Production}_c = \text{Area}_c \times \text{Yield}_c \quad (\text{tonna})$$
$$\text{Gross Revenue}_c = \text{Production}_c \times \text{Price}_c \quad (\text{UZS})$$

Agar hosil $H_c$ oylarda yig'ib olinsa va xaridor bilan to'lov kechikishi $D_c$ oy bo'lsa:
$$\text{Tushum Oyi} = h + D_c, \quad h \in H_c$$
$$\text{Oylik Tushum} = \frac{\text{Gross Revenue}_c}{|H_c|}$$

### 2.2. Xarajatlar Taqsimoti
Oylik operatsion xarajatlar quyidagi moddalar yig'indisidan iborat:
$$\text{Opex}_t = \text{Seeds}_t + \text{Fertilizer}_t + \text{Fuel}_t + \text{Labor}_t + \text{Fixed Opex}$$

### 2.3. Oylik Balans va Defitsit
$$\text{Closing}_t = \text{Opening}_t + \text{Inflows}_t - (\text{Opex}_t + \text{Debt Service}_t)$$
Agar $\text{Closing}_t < 0$ bo'lsa, oy **kassa uzilishi (defitsit)** holatida deb belgilanadi va `NEGATIVE_CASH` ogohlantirishi beriladi.
