# AGROHISOB CFO — HUQUQIY QOIDALAR VERIFIKATSIYASI VA XATARLAR TAHLILI

## 1. Kirish
Ushbu hujjat VMQ-613, PQ-47 va PF-82 me'yoriy qoidalarining dasturiy realizatsiyasidagi huquqiy aniqlik, cheklovlar va talqinlarni belgilaydi.

---

## 2. Huquqiy Qoidalar Matritsasi va Algoritmik Moslashuv

| Me'yoriy Hujjat | Modda / Band | Huquqiy Talab | Dasturiy Amalga Oshirish Usuli | Holati |
| :--- | :--- | :--- | :--- | :--- |
| **VMQ-613** | 8-band | Ijara muddati kredit muddati tugashidan kamida 5 yil ortiq bo'lishi | `dateutil.relativedelta(years=5)` yoki taqvimiy kunbay solishtirish: `lease_end >= loan_maturity + 5 years`. | **VERIFIED** |
| **VMQ-613** | 5-band | Ijara huquqi davlat ro'yxatidan o'tgan bo'lishi shart | `is_registered == True` va `registration_number` mavjudligi. | **VERIFIED** |
| **VMQ-613** | 12-band | Sud nizolari, taqiqlar va shartnoma bekor qilinmaganligi | `has_restrictions == False` va `is_disputed == False`. | **VERIFIED** |
| **VMQ-613** | 14-band | Ikkilamchi ijara (sub-lease) huquqi | Sub-lease holatida ijaraga beruvchi hokimlik/vasiy organ rozilik hujjati talab etiladi, aks holda `ADDITIONAL_VERIFICATION_REQUIRED`. | **VERIFIED** |
| **VMQ-613** | 15-band | Mustaqil baholovchi hisoboti talabi | Avtomatlashtirilgan DCF bahosi "Indikativ namunaviy model" deb belgilanadi, rasmiy baholash hisoboti `MISSING` yoki `AVAILABLE` sifatida ro'yxatda tekshiriladi. | **VERIFIED** |
| **PQ-47** | 2-ilova | Tomchilatib sug'orish bazaviy subsidiyalari | Ekin turlari bo'yicha gektariga 6, 8, 10 mln so'mlik rasmiy tabaqalashgan matritsa. | **VERIFIED** |
| **PQ-47** | 2-band | Bosqichli to'lov (50% / 50%) | Dastlabki kassa tushumi sifatida 50% ko'rsatiladi, qolgan 50% esa 1 mavsumdan so'ng shartli kutilma sifatida belgilanadi. | **VERIFIED** |
| **PQ-47** | 3-band | Imtiyozli kredit foizi kompensatsiyasi | Asosiy stavkadan oshgan foiz bandi (masalan, 4%) kredit qoldig'iga nisbatan davrlar bo'yicha hisoblanadi. | **VERIFIED** |
| **PF-82** | 1-band | Paxta va g'alla intizomli to'lovchilari uchun foiz kompensatsiyasi | Faqat o'z vaqtida to'langan asosiy qarz qoldig'i bo'yicha yillik 10 foiz bandi kompensatsiya qilinadi. Kechiktirilgan davrlar chiqarib tashlanadi. | **VERIFIED** |

---

## 3. Qat'iy Cheklovlar va Ogohlantirishlar
1. **Litsenziyali Baholash Cheklovi:** AgroHisob CFO avtomatlashtirilgan hisoblagichi O'zbekiston Respublikasining «Baholash faoliyati to'g'risida»gi Qonuni ma'nosidagi rasmiy baholash hisoboti hisoblanmaydi.
2. **Kredit Ajratish Kafolati Yo'qligi:** Qoidalar bo'yicha talablar bajarilishi bank tomonidan kredit berilishi kafolatini bermaydi. Yakuniy qaror bank kredit qo'mitasi vakolatidadir.
3. **Subsidiya Kafolati Yo'qligi:** Tizim subsidiya olish ehtimoli va uning miqdorini baholaydi, ammo subsidiya to'lash vakolatli davlat organlari va Jamg'arma qarori bilan amalga oshiriladi.
