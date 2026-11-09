# AgroHisob CFO — AI Maxfiylik va Raqamli Faktlarni Tekshirish Spetsifikatsiyasi

## 1. Maxfiylik Qoidalari (Data Privacy Principles)

AgroHisob CFO platformasi quyidagi maxfiylik tamoyillariga qat'iy rioya qiladi:
1. **Shaxsiy va Bank Sirini Himoyalash**: Korxonaning STIR/INN raqamlari, bank hisob raqamlari (IBAN/MFO), kontragentlarining to'liq ma'lumotlari yoki maxfiy schyot-fakturalari hech qachon OpenAI, Google Gemini yoki boshqa tashqi LLM provayderlariga yuborilmaydi.
2. **Mahalliy Deterministik Ishlash**: Barcha asosiy moliyaviy hisob-kitoblar va tahliliy xulosalar 100% lokal Financial Engine orqali generatsiya qilinadi.
3. **Agregatlangan Ma'lumotlar bilan Ishlash**: Tashqi tushuntirish talab qilinganda faqat yillik yig'ma ko'rsatkichlar (masalan, "Yillik DSCR: 1.42x, 2 oy kassa taqchilligi") yuboriladi.

## 2. Faktik Raqamlarni Tekshirish (Numerical Claim Validation)

LLM tomonidan shakllantirilgan har qanday matn `validate_llm_claims` orqali tekshiriladi:
- Matndan barcha sonli qiymatlar ajratib olinadi.
- Ruxsat etilgan faktlar ro'yxatida mavjud bo'lmagan sun'iy sonlar aniqlansa, matn rad etiladi.
- Taqiqlangan regulyator da'volari ("kredit bank tomonidan tasdiqlandi", "davlat kafolati berildi") mavjud bo'lsa, xavfsizlik filtri orqali bloklanadi.
- Tekshiruvdan o'tmagan hollarda foydalanuvchiga 100% ishonchli Layer A deterministik xulosasi taqdim etiladi.
