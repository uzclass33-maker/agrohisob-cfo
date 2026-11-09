# Qishloq Xo'jaligi Subsidiyalari Hisob-Kitob Metodlari va Moliyaviy Modellar

## 1. Nazariy Asos

Ushbu hujjat AgroHisob CFO tizimida davlat subsidiyalari va imtiyozli foiz kompensatsiyalarini modellashtirishning yagona matematik standartini belgilaydi.

---

## 2. PQ-47 Suv Tejovchi Tizimlar Formulalari

$$S_{baza} = \text{CropRate}(\text{Ekin})$$
$$S_{samarali} = S_{baza} \times K_{hudud}$$
$$S_{jami} = S_{samarali} \times \text{Maydon}_{ga}$$

Bosqichma-bosqich ajratish:
$$S_{1-bosqich} = S_{jami} \times 0.50$$
$$S_{2-bosqich} = S_{jami} - S_{1-bosqich}$$

Bank krediti mavjud bo'lganda yillik foiz kompensatsiyasi:
$$Kompensatsiya_{PQ47} = \text{Kredit Asosiy Summasi} \times 0.04$$

---

## 3. PF-82 Paxta & G'alla Foiz Kompensatsiyasi Formulalari

Agar $\text{HasOverdue} == \text{True}$ bo'lsa:
$$\text{Kompensatsiya}_{PF82} = 0$$

Aks holda:
$$\text{Kompensatsiya}_{PF82} = \frac{\text{Qoldiq} \times 0.10 \times \text{Kunlar}}{365}$$

Fermer to'laydigan yakuniy foiz stavkasi:
$$r_{fermer} = \max\left(0.0\%, r_{shartnoma} - 10.0\%\right)$$

---

## 4. Buxgalteriya va Kassa Invarianti

1. **Tarixiy Kassa:** Hech qanday potentsial subsidiya tasdiqlangan bank ko'chirmasi mavjud bo'lmaguncha tarixiy tushumlarga kiritilmaydi.
2. **Prognoz Kassa:** 1-bosqich investitsiya davrida o'rnatish xarajatlarini qoplaydi, 2-bosqich vegetatsiya yakunida aylanma mablag'larga ijobiy ta'sir ko'rsatadi.
3. **Qarz Ko'rsatkichi (DSCR):** Yillik foiz kompensatsiyasi qarzga xizmat ko'rsatish yukini kamaytiradi:
   $$DSCR_{yangi} = \frac{CFADS}{\text{Debt Service} - \text{Kompensatsiya}}$$
