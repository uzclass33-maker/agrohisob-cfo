# AgroHisob CFO — Ssenariylar Simulyatsiyasi Spetsifikatsiyasi

## 1. Muqobil Ssenariy Rejimlari

1. **Baza Ssenariysi (Base Scenario)**:
   - Tushum o'zgarishi: `0%`
   - Xarajatlar o'zgarishi: `0%`
   - To'lov kechikishi: `0 oy`
   - Foiz stavkasi delta: `0%`

2. **Optimistik Ssenariy (Optimistic Scenario)**:
   - Tushum o'zgarishi: `+20%` (hosildorlik yoki bozor narxining oshishi)
   - Xarajatlar o'zgarishi: `-10%` (tejamkor texnologiyalar, resurs tejash)
   - To'lov kechikishi: `0 oy`
   - Foiz stavkasi delta: `0%`

3. **Pessimistik Ssenariy (Pessimistic Scenario)**:
   - Tushum o'zgarishi: `-20%` (qurg'oqchilik, hosil nobudgarchiligi yoki narx tushishi)
   - Xarajatlar o'zgarishi: `+15%` (mineral o'g'it va yoqilg'i narxining ko'tarilishi)
   - To'lov kechikishi: `+1 oy` (xaridorlar tomonidan to'lovni kechiktirish)
   - Foiz stavkasi delta: `+2%` (tijorat banklari foiz oshishi)

4. **Maxsus Ssenariy (Custom Scenario)**:
   - Foydalanuvchi slayderlar yordamida o'z parametrlari kombinatsiyasini belgilaydi.

## 2. Backend Qayta Hisoblash Qoidasi

- Hech qanday hisob-kitob brauzerda oddiy ko'paytirish yo'li bilan bajarilmaydi.
- Har safar `POST /api/v1/dashboard/scenarios` chaqiriladi.
- Backend Financial Engine barcha 12 oyni yangidan hisoblab chiqadi:
  - Yangi oylik kassa oqimlari
  - Yangi CFADS va oylik/yillik DSCR
  - Yangi kassa uzilishlari va eng past kassa nuqtasi
  - Baza va Stressed ssenariylar o'rtasidagi aniq farqlar (Variance)
