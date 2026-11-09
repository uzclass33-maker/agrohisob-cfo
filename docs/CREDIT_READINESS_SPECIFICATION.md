# AGROHISOB CFO — KREDITGA TAYYORGARLIK SPETSIFIKATSIYASI (ASSIGNMENT 5)

## 1. Kirish va Maqsad
AgroHisob CFO platformasining 5-topshirig'i doirasida O'zbekiston agrar sektori (fermer xo'jaliklari, agrosanoat eksportyorlari va paxta-to'qimachilik/g'allachilik klasterlari) uchun tijorat banklari (Agrobank, Mikrokreditbank, Qishloq Qurilish Bank va boshqalar) anderrayting mezonlariga moslashtirilgan **Kreditga Tayyorgarlik Baholash Tizimi** (Credit Readiness Assessment) ishlab chiqildi.

Mazkur tizim qishloq xo'jaligi korxonasining qarzga xizmat ko'rsatish qobiliyati, mavsumiy kassa uzilishlari xavfi, hujjatlar to'liqligi va ssenariy barqarorligini deterministik algoritmlar asosida tahlil qilib, bank kredit qo'mitasi talablariga mos professional tahliliy dosye va moliyaviy modelni shakllantiradi.

---

## 2. Kreditga Tayyorgarlik Reytingi Metodologiyasi

### 2.1. Skoring Shkalasi (0-100 Ball)
Reyting deterministik qoidalar asosida 0 dan 100 gacha oraliqda hisoblanadi:

| Reyting Diapazoni | Status (StatusEnum) | Izoh va Tavsiya |
| :--- | :--- | :--- |
| **80 – 100 ball** | `READY_FOR_REVIEW` (Tahlil uchun tayyor) | Korxona to'liq hujjatlar to'plamiga va barqaror qarz qoplash ko'rsatkichiga (DSCR >= 1.25x) ega. Ariza bank anderraytingiga topshirishga tayyor. |
| **60 – 79 ball** | `ADDITIONAL_INFO_REQUIRED` (Qo'shimcha ma'lumot talab etiladi) | Asosiy parametrlar ijobiy, biroq ayrim muhim hujjatlar (masalan, 12 oylik bank aylanmasi yoki offtake shartnomasi) yetishmaydi yoki kassa uzilishi mavjud. |
| **0 – 59 ball** | `INSUFFICIENT_DATA` (Ma'lumotlar yetarli emas) | Ma'lumotlar to'liqligi 50% dan past yoki qarz yuki kritik darajada yuqori (DSCR < 1.0x). |

### 2.2. Baholash Komponentlari va Ballar Taqsimoti
1. **Qarzga Xizmat Ko'rsatish Qoplami (DSCR) — 35 ball:**
   - DSCR >= 1.60x: +35 ball (A'lo daraja).
   - 1.25x <= DSCR < 1.60x: +25 ball (Barqaror bank me'yori).
   - 1.00x <= DSCR < 1.25x: +10 ball (Kuzatuv ostida, yuqori xatar).
   - DSCR < 1.00x: 0 ball (Operatsion pul oqimi qarzni qoplamaydi).
2. **Kassa Oqimi Uzilishlari (Cash Deficit) — 20 ball:**
   - 0 oy uzilish (hech qaysi oyda salbiy qoldiq yo'q): +20 ball.
   - 1-2 oy kassa uzilishi (mavsumiy aylanma liniyasi zarur): +10 ball.
   - 3 va undan ortiq oy kassa uzilishi: +0 ball.
3. **Birlamchi Hujjatlar To'liqligi — 25 ball:**
   - 100% hujjatlar mavjud: +25 ball.
   - 75% - 99%: +18 ball.
   - 50% - 74%: +10 ball.
   - < 50%: +0 ball.
4. **Agrar Aktivlar va Texnologiya — 10 ball:**
   - Suv tejovchi tomchilatib sug'orish mavjudligi (PQ-47 imtiyozlari): +5 ball.
   - Zamonaviy sovutkichli omborxona (Cold Storage): +5 ball.
5. **Yer Maydoni va Tuproq Boniteti — 10 ball:**
   - Tuproq boniteti >= 70 ball: +10 ball.
   - 50 <= Bonitet < 70 ball: +6 ball.
   - Bonitet < 50 ball: +2 ball.

---

## 3. Hujjatlar Nazorat Ro'yxati (5 Domen)

1. **Korxona Yuridik Ma'lumotlari (Company Info):**
   - Davlat ro'yxatidan o'tganlik to'g'risida guvohnoma (Guvohnoma).
   - Ustav va ta'sis shartnomasi.
   - Rahbar va bosh buxgalter shaxsini tasdiqlovchi pasport nusxalari.
2. **Buxgalteriya va Moliyaviy Axborot (Financial Info):**
   - So'nggi 12 oylik bank hisobvarag'i ko'chirmasi (Bank Statement).
   - Soliq solishtirma dalolatnomasi va moliyaviy hisobotlar (1 va 2-shakl).
   - Mavjud kredit va lizing majburiyatlari bo'yicha bank ma'lumotnomasi.
3. **Agrar Faoliyat va Yer Maydoni (Agricultural Info):**
   - Uzoq muddatli yer ijarasi shartnomasi va kadastr pasporti.
   - Tuproq boniteti baholash xulosasi (O'zdaverloyiha).
   - Ekin ekish xaritasi va hosil yig'ishtirish rejasi.
4. **Biznes Reja va Bozor Aloqalari (Business Info):**
   - Moliyalashtirish maqsadi bo'yicha Biznes Reja / TIA.
   - Klaster yoki xaridorlar bilan fyuchers/kontraktatsiya shartnomalari.
5. **Garov Ta'minoti va Kredit Parametrlari (Financing Info):**
   - Taklif etilayotgan garov ta'minoti mulk hujjatlari yoki VMQ-613 ijara huquqi bahosi.

---

## 4. Huquqiy Cheklov va Rasmiy Ogohlantirish (Statutory Disclaimer)
Dosye va Excel modelida quyidagi qat'iy ogohlantirish majburiy keltiriladi:
> «Mazkur dosye AgroHisob CFO dasturiy platformasi tomonidan korxona taqdim etgan birlamchi bank aylanmalari va kiritilgan prognoz farazlari asosida shakllantirilgan tahliliy axborot hujjatidir. Ushbu hujjat mustaqil auditorlik xulosasi, rasmiy garov baholash dalolatnomasi yoki tijorat bankining qat'iy kredit qarori hisoblanmaydi. Kredit ajratish to'g'risidagi yakuniy qaror faqat vakolatli bank kredit qo'mitasi tomonidan mustaqil anderrayting mezonlari asosida qabul qilinadi.»
