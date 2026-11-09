# Qishloq Xo'jaligi Yer Ijara Huquqini Indikativ Baholash Metodologiyasi (DCF)

## 1. Nazariy Asos va Cheklovlar

O'zbekiston Respublikasi Yer Kodeksiga muvofiq, qishloq xo'jaligi yeri davlat mulki bo'lib, uning o'zi emas, balki **yer uchastkasiga bo'lgan ijara huquqi** fuqarolik-huquqiy muomalada garov predmeti bo'lishi mumkin (VMQ-613).

AgroHisob CFO platformasi yer ijara huquqini baholashda **Daromad yondashuvi (Income Approach)** doirasidagi **Diskontlangan Pul Oqimi (DCF - Discounted Cash Flow)** usulidan foydalanadi.

---

## 2. Matematik Modellashtirish

### A. Bonitet Balli Tuzatmasi
Respublika bo'yicha me'yoriy o'rtacha tuproq boniteti 65 ball deb qabul qilingan:
$$K_{bonitet} = \min\left(1.80, \max\left(0.30, \frac{\text{Bonitet}}{65}\right)\right)$$

### B. Yillik Sof Iqtisodiy Foyda (Attributable Net Benefit)
Gektariga me'yoriy yillik sof foyda tuproq unumdorligi va xo'jalik maydoniga ko'paytiriladi:
$$CF_{yillik} = \text{Normativ Daromad}_{/ga} \times K_{bonitet} \times \text{Maydon}_{ga}$$

### C. Cheklangan Ijara Ufqi Diskontlash Formulasi
Ijara muddati cheklangan bo'lganligi sababli, tahlil ufqi $N = \text{Qolgan Ijara Yillari}$ bilan qat'iy chegaralanadi. 
**Asossiz cheksiz terminal qiymat (Terminal Value = 0) qat'iyan qo'llanilmaydi**:

$$PV = \sum_{t=1}^{N} \frac{CF_t}{(1 + r)^t}$$

bu yerda:
- $CF_t$ — $t$-yildagi sof kutilayotgan pul tushumi;
- $r$ — yillik diskont stavkasi (masalan, 16.0%);
- $N$ — ijaraning qolgan yillari soni.

Annuity ifodasi orqali:
$$PV = CF_{yillik} \times \left[ \frac{1 - (1 + r)^{-N}}{r} \right]$$

### D. Maksimal Garov Ta'minoti (LTV Bo'yicha)
Tijorat banklari odatda ko'chmas mulk va nomoddiy aktivlar bo'yicha ehtiyotkorlik printsipi asosida 60-70% (standart: 65%) LTV koeffitsiyentini qo'llaydi:
$$\text{Max Pledge Value} = PV \times \text{Target LTV Pct}$$

---

## 3. Ko'p Ssenariyli Sezgirlik Tahlili (Sensitivity Recalculation)

Platforma parametrik o'zgarishlarni soxtalashtirmasdan, quyidagi uchta to'liq qayta hisoblangan ssenariyni taqdim etadi:

1. **Bazaviy Ssenariy (Base Case):**
   - Foydalanuvchi kiritgan me'yoriy daromad va diskont stavkasi ($r$).
   - O'rtacha agrotexnik sharoit.
2. **Optimistik Ssenariy (Optimistic Case):**
   - Diskont stavkasi 200 bazis punktga pasaytiriladi: $r_{opt} = \max(6.0\%, r - 2.0\%)$.
   - Yillik sof iqtisodiy foyda 15% ga oshiriladi: $CF_{opt} = CF \times 1.15$.
   - Qiymat o'sishi: $+18\%$ dan $+25\%$ gacha.
3. **Pessimistik Ssenariy (Pessimistic Case):**
   - Diskont stavkasi 300 bazis punktga oshiriladi: $r_{pes} = \min(35.0\%, r + 3.0\%)$.
   - Yillik sof iqtisodiy foyda 20% ga pasaytiriladi (narx yoki hosildorlik shoki): $CF_{pes} = CF \times 0.80$.
   - Qiymat pasayishi: $-28\%$ dan $-35\%$ gacha.

---

## 4. Misol Hisob-Kitob (Andijon Baraka Fermer Xo'jaligi)

- **Maydon:** 65.0 ga
- **Bonitet:** 68 ball ($K_{bonitet} = 68 / 65 \approx 1.0462$)
- **Bazaviy normativ foyda:** 8 500 000 so'm/ga
- **Tuzatilgan foyda:** 8 892 308 so'm/ga
- **Yillik jami sof foyda:** 578 000 000 so'm
- **Ijara qoldiq muddati ($N$):** 25 yil
- **Diskont stavkasi ($r$):** 16.0%
- **Annuity koeffitsiyenti:** 6.1032
- **Indikativ Bozor Qiymati ($PV$):** **3 527 637 127 so'm**
- **Bank LTV Ta'minoti (65%):** **2 292 964 133 so'm**
