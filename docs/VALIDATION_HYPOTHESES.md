# AGROHISOB CFO — MAHSULOTNI VALIDATSIYA QILISH GIPOTEZALARI (VALIDATION HYPOTHESES)

**Versiya:** 1.0.0  
**Holat:** Pilotgacha bo'lgan dastlabki gipotezalar to'plami  
**Eslatma:** Ushbu hujjatdagi bandlar ilmiy gipoteza hisoblanadi va hali real to'lovchi mijozlar tomonidan tasdiqlangan fakt deb qaralmaydi.

---

## 1. GIPOTEZALAR MATRITSASI

### H1 — Agrar korxonalar tuzilgan pul oqimi (Cash Flow) hisobotlarini tayyorlashda qiyinchilikka duch keladi
- **Maqsadli foydalanuvchi:** Fermer xo'jaliklari rahbarlari, agrosanoat buxgalterlari, moliyaviy menejerlar.
- **Muammo:** Qishloq xo'jaligida tushumlar mavsumiy (yiliga 1-2 marta yig'im-terim davrida), xarajatlar esa yil bo'yi bir maromda davom etadi. Mavjud 1C tizimlari o'tmishdagi buxgalteriya hisobini yuritadi, lekin kelgusi 12 oylik likvidlik uzilishlarini (cash gap) oldindan ko'rsatib bermaydi.
- **Tadqiqot usuli:** 15-20 ta agrar korxona buxgalteri va rahbari bilan yarim tuzilgan intervyular (semi-structured customer interviews).
- **Zarur dalil:** Kamida 10 ta respondent o'tgan 12 oy ichida kutilmagan kassa uzilishiga duch kelganini va buni Excelda qo'lda hisoblashga majbur bo'lganini tasdiqlashi kerak.
- **Muvaffaqiyat chegarasi (Success threshold):** Respondentlarning $\ge 70\%$ qismi pul oqimini rejalashtirishni o'zining "eng og'riqli 3 ta muammosi" qatoriga kiritadi.
- **Muvaffaqiyatsizlik chegarasi (Failure threshold):** Respondentlarning $\le 30\%$ qismi bu muammoni muhim deb hisoblaydi (mavjud Excel yoki 1C yetarli deydi).
- **Joriy holat:** `FOUNDER ASSUMPTION & SECONDARY RESEARCH` (O'zbekiston agrar sohasidagi umumiy tahlillar asosida shakllantirilgan, intervyular orqali tekshirilishi kerak).
- **Keyingi harakat:** 5 ta klaster buxgalteri va 10 ta fermer bilan intervyu o'tkazish.

---

### H2 — Mavjud ish jarayonlari Excel, 1C va bank ko'chirmalari o'rtasida katta hajmdagi qo'lda solishtirishni talab qiladi
- **Maqsadli foydalanuvchi:** Bosh buxgalterlar va moliyaviy tahlilchilar.
- **Muammo:** Buxgalterlar Didox elektron fakturalari, 1C aylanma vedomostlari va bank ko'chirmalarini qo'lda Excelga ko'chirib o'tiradi, bu esa haftasiga 8-15 soat vaqt oladi va insoniy xatolarga sabab bo'ladi.
- **Tadqiqot usuli:** Ish joyida bevosita kuzatuv (workflow shadow audit) va vaqt xronometraji (time tracking).
- **Zarur dalil:** Buxgalterlarning oylik yoki choraklik moliyaviy hisobotlarni birlashtirish uchun sarflaydigan aniq vaqt ko'rsatkichi (soatlarda).
- **Muvaffaqiyat chegarasi:** Buxgalterlar har oyda kamida 10 soatni turli tizimlardan ma'lumotlarni qo'lda Excelga yig'ishga sarflashini tasdiqlashi.
- **Muvaffaqiyatsizlik chegarasi:** Buxgalterlarning 1C tizimi to'liq avtomatlashgan va qo'shimcha birlashtirishga 2 soatdan kam vaqt ketishi.
- **Joriy holat:** `FOUNDER ASSUMPTION`.
- **Keyingi harakat:** Pilot ishtirokchilarining dastlabki xronometrajini o'lchash (Baseline measurement).

---

### H3 — AgroHisob CFO hisobot tayyorlash vaqtini kamida 60-70% ga qisqartiradi
- **Maqsadli foydalanuvchi:** Kredit oluvchi fermerlar va konsalting xizmati mutaxassislari.
- **Muammo:** Bankka kredit arizasi topshirish uchun talab etiladigan biznes-reja, pul oqimlari jadvali va DSCR hisob-kitoblarini tayyorlash 5 kundan 14 kungacha cho'ziladi.
- **Tadqiqot usuli:** 3-5 ta korxona ishtirokida 4 haftalik amaliy pilot sinovi (Pilot workflow benchmark).
- **Zarur dalil:** Aniq o'lchangan $Time\ Saved = \frac{T_{baseline} - T_{product}}{T_{baseline}} \times 100\%$.
- **Muvaffaqiyat chegarasi:** O'rtacha hisobot tayyorlash vaqti 3 kundan 2 soatgacha (kamida 70% tejash) qisqarishi.
- **Muvaffaqiyatsizlik chegarasi:** Vaqt tejalishi 30% dan kam bo'lishi yoki ma'lumotlarni tozalashga platformadan tashqari ko'p vaqt talab etilishi.
- **Joriy holat:** `UNVERIFIED PRODUCT HYPOTHESIS` (Platforma ichida hisob-kitob 1 soniyada amalga oshadi, biroq mijozning xom fayllarini tayyorlashi pilotda o'lchanishi shart).
- **Keyingi harakat:** Pilot bosqichida fermer bilan birga boshidan oxirigacha vaqtni qayd etish.

---

### H4 — Agrar moliya menejerlari 12 oylik mavsumiy prognoz va stress-test modellarini amalda qaror qabul qilishda qo'llaydi
- **Maqsadli foydalanuvchi:** Korxona rahbarlari va agrobiznes egalari.
- **Muammo:** Rahbarlar narxlar tushishi (-20%) yoki hosildorlik kamayishi (-15%) sharoitida korxona kreditni to'lay oladimi-yo'qmi bilmaydi va faqat bank talab qilgandagina formal qog'oz tayyorlaydi.
- **Tadqiqot usuli:** Pilot davrida ssenariy simulyatsiyasi modulidan foydalanish chastotasini (Product Analytics) va haftalik sifat intervyularini tahlil qilish.
- **Zarur dalil:** Pilot foydalanuvchilarining kamida 1 marta o'z korxonasining real stress-ssenariysini hisoblab, o'z strategiyasiga o'zgartirish kiritishi.
- **Muvaffaqiyat chegarasi:** Pilot ishtirokchilarining $\ge 60\%$ qismi ssenariylar tahlilini foydali deb baholashi va uni ichki rejalashtirishda saqlab qolishi.
- **Muvaffaqiyatsizlik chegarasi:** Foydalanuvchilar faqat bank uchun PDF olib, boshqa sahifalarga umuman qaytmasligi.
- **Joriy holat:** `UNVERIFIED PRODUCT HYPOTHESIS`.
- **Keyingi harakat:** Ssenariy moduli bo'yicha hodisalarni (`scenario_calculated`) analitika orqali qayd etish.

---

### H5 — Aniqlangan mijoz segmenti mahsulot uchun to'lashga tayyor (Willingness to Pay)
- **Maqsadli foydalanuvchi:** Meva-sabzavot eksportyorlari, 100+ gektar yerga ega agrosanoat korxonalari va klasterlar.
- **Muammo:** B2B SaaS mahsulotlari uchun O'zbekiston agrar sohasida oylik obuna madaniyati yangi hisoblanadi.
- **Tadqiqot usuli:** Van Westendorp narx sezgirligi modeli (Price Sensitivity Meter) va pilot yakunida haqiqiy tijorat taklifini (Commercial Proposal) berish.
- **Zarur dalil:** Kamida 2-3 ta korxona pilotdan so'ng 1 oylik yoki 1 yillik obuna to'loviga rozi bo'lishi yoki kafolat xati (Letter of Intent) imzolashi.
- **Muvaffaqiyat chegarasi:** Oyiga 500,000 – 1,200,000 so'm ($40 – $100/oy) atrofidagi obunaga kamida 20% respondentlarning tayyorligi.
- **Muvaffaqiyatsizlik chegarasi:** Barcha respondentlar faqat 1 martalik bepul xizmat kutishi va obunadan to'liq bosh tortishi.
- **Joriy holat:** `FOUNDER ASSUMPTION`.
- **Keyingi harakat:** Pilot ishtirokchilariga 4-haftada tijorat taklifini yuborish.

---

### H6 — Moliyaviy ma'lumotlarning maxfiyligi (Data Privacy) mahsulotni qabul qilishdagi asosiy to'siq hisoblanadi
- **Maqsadli foydalanuvchi:** Korxona egalari va bosh buxgalterlar.
- **Muammo:** Fermerlar o'zlarining bank aylanmalari, real daromadlari va xarajatlarini bulutli tizimga kiritishdan xavfsiraydi (soliq yoki raqobatchilarga ma'lumot chiqib ketishidan qo'rqish).
- **Tadqiqot usuli:** Intervyu savollarida xavfsizlikka oid e'tirozlarni (objections) tizimli tahlil qilish.
- **Zarur dalil:** Xavfsizlik shartnomasi (NDA) va ma'lumotlarni saqlash kafolatlari taqdim etilganda mijozning rozilik berish darajasi.
- **Muvaffaqiyat chegarasi:** Kuchli NDA va anonimlashtirish mexanizmi ko'rsatilganda $\ge 80\%$ korxonaning pilotga rozilik bildirishi.
- **Muvaffaqiyatsizlik chegarasi:** Korxonalarning 50% dan ortig'i hatto qat'iy shartnoma bilan ham bulutga ma'lumot yuklashdan qat'iy bosh tortishi.
- **Joriy holat:** `HIGH-RISK ASSUMPTION`.
- **Keyingi harakat:** Pilot shartnomasida qat'iy maxfiylik reglamentini (`PILOT_DATA_SECURITY.md`) taqdim etish.
