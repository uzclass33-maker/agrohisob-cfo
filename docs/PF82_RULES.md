# PF-82 Paxta va G'alla Yetishtiruvchilarni Qo'llab-Quvvatlash Farmoni Qoidalari

## 1. Huquqiy Asos
- **Hujjat:** O'zbekiston Respublikasi Prezidentining 2026-yil 8-maydagi PF-82-son Farmoni
- **Nomi:** «Paxta va g'alla yetishtiruvchi qishloq xo'jaligi korxonalarini moliyaviy qo'llab-quvvatlash chora-tadbirlari to'g'risida»
- **Rasmiy Lex.uz havolasi:** [https://lex.uz/uz/acts/-8187068](https://lex.uz/uz/acts/-8187068)
- **Kuchga kirish sanasi:** 2026-yil 8-may
- **Boshqaruvchi organ:** Qishloq xo'jaligini qo'llab-quvvatlash jamg'armasi

---

## 2. 10 Foiz Bandi Kompensatsiyasi Qoidasi (1-band)

- **Qo'llanish sohasi:** Paxta va g'alla yetishtirish agrotexnikasi uchun tijorat banklaridan ajratilgan imtiyozli kreditlar.
- **Kompensatsiya miqdori:** Shartnomaviy foiz stavkasining **10 foiz bandi (10.0% points)**.
- **Fermer uchun yakuniy yuk:**
  $$\text{Net Interest Rate} = \max\left(0.0\%, \text{Contract Rate} - 10.0\%\right)$$
  - Misol: Shartnoma bo'yicha foiz 14% bo'lsa, davlat 10% ini to'laydi, fermer atigi **4%** to'laydi.

---

## 3. Qat'iy Cheklov: Muddati O'tgan Qarzdorlik (Overdue Debt Disqualification)

PF-82 ning eng muhim talabi intizomli to'lov mexanizmidir:
- Kredit to'lovlari bo'yicha **muddati o'tgan qarzdorlik (prosrochka)** mavjud bo'lgan davr uchun foiz kompensatsiyasi **aslo to'lanmaydi** (`is_eligible = False`, `compensation = 0`).
- Kompensatsiya faqat o'z vaqtida so'ndirilgan kredit qoldig'iga nisbatan, intizomli kunlar soniga mutanosib ravishda beriladi.

---

## 4. Kunlik Aniq Hisob-Kitob Formulasi

$$\text{Kompensatsiya} = \frac{\text{Haqiqiy Qarz Qoldig'i} \times 10\% \times \text{O'z Vaqtida So'ndirilgan Kunlar}}{365}$$

### Misol:
- Qarz qoldig'i: 120 000 000 so'm
- Intizomli kunlar: 365 kun
- Hisoblangan davlat yordami:
  $$\frac{120\,000\,000 \times 0.10 \times 365}{365} = \mathbf{12\,000\,000 \text{ so'm}}$$
