# AgroHisob CFO — AI-CFO Tahliliy Xulosalar Dvigateli (AI Insights Engine)

## 1. Dvigatel Vazifasi va Imkoniyatlari

AI-CFO dvigateli agrobiznes rahbarlariga murakkab moliyaviy jadvallarni o'qimasdan, to'g'ridan-to'g'ri amaliy strategik qarorlar qabul qilishda yordam beruvchi avtonom tahliliy tizimdir.

## 2. Ikki Qatlamli Arxitektura

### Layer A: Deterministik Qoidalar Dvigateli (Deterministic Rule Engine)
- To'liq mustaqil ishlaydi, hech qanday tashqi API yoki internetga bog'liq emas.
- 12 oylik mavsumiy prognoz va qarz xizmati natijalarini skanerlaydi.
- Quyidagi 4 ta kategoriya bo'yicha tahliliy kartalar ishlab chiqaradi:
  1. `LIQUIDITY_DEFICIT`: Bahorgi yoki mavsumiy kassa uzilishi.
  2. `DEBT_SERVICE_PRESSURE`: DSCR qoplash me'yoridan pastligi.
  3. `SEASONAL_GAP`: Tushumlar va chiqimlar o'rtasidagi vaqt bo'shlig'i.
  4. `HEALTHY_CONDITIONS`: Mustahkam kassa qoldig'i va investitsiya imkoniyatlari.

### Layer B: Maxfiy LLM Tushuntirishi (Privacy-Preserving LLM)
- Ixtiyoriy ravishda foydalanuvchi tugmani bosganda ishga tushadi.
- Maxfiy korxona ma'lumotlari (bank hisob raqami, STIR, individual fakturalar) tashqi modelga uzatilmaydi.
- Faqat agregatlangan xulosalar tabiiy o'zbek tilida boyitiladi.
- Chiqish matnidagi faktlar tekshiriladi; agar mos kelmasa, xatoliksiz Layer A ga qaytiladi (Zero-Failure Fallback).
