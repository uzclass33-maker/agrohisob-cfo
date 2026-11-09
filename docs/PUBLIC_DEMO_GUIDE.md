# AGROHISOB CFO — OMMAVIY DEMONSTRATSIYA VA REVYUERLAR QO'LLANMASI (PUBLIC DEMO GUIDE)

**Hujjat identifikatori:** `DOC-AH-DEMO-01`  
**Sana:** 2026-11-09  
**Holat:** TASDIQLANGAN (APPROVED)  

---

## 1. DEMONSTRATSIYA MAQSADI VA TIZIM HAVOLALARI

AgroHisob CFO — O'zbekiston agrobiznesi uchun sun'iy intellekt va qat'iy moliyaviy muhandislikka asoslangan avtomatlashtirilgan moliyaviy direktor (AI-CFO) va bank kredit tayyorgarligi (Pre-Underwriting) platformasidir.

- **Frontend interfeysi:** `http://localhost:3000` (yoki Vercel havolasi)
- **Backend API hujjatlari (Swagger):** `http://127.0.0.1:8000/docs`
- **Sog'lomlik tekshiruvi:** `http://127.0.0.1:8000/health`

---

## 2. 3 TA SINTETIK AGROBIZNES SSENARIYSI TAHLILI

Revidentlar va investorlar tizimni 3 ta real agrobiznes profili asosida to'liq sinab ko'rishlari mumkin:

### 1-Ssenariy: Kichik Fermer Xo'jaligi ("Baxrom Fermer Fayz")
- **Profil:** Farg'ona vodiysi, 50 gektar paxta va g'alla.
- **Moliyaviy ko'rsatkichlar:** Yillik tushum ~375 mln UZS, bahor oylarida kassa uzilishi (May-Iyun oylarida Cash Gap: -45 mln UZS).
- **Asosiy muammo:** Mavsumiy uzilish tufayli banklar kredit berishdan qo'rqadi.
- **AgroHisob CFO yechimi:** Tizim kassa taqchilligini oldindan prognoz qiladi, imtiyozli aylanma mablag' kreditiga tavsiya beradi, PQ-47 bo'yicha tomchilatib sug'orishga 50% subsidiya topadi.

### 2-Ssenariy: Intensiv Meva Eksportchisi ("Agro-Export Samarkand")
- **Profil:** Samarqand viloyati, 120 gektar intensiv olma va gilos bog'lari, zamonaviy muzlatkichli saqlash ombori.
- **Moliyaviy ko'rsatkichlar:** Yillik tushum ~3.2 mlrd UZS, kuchli DSCR (2.4x).
- **AgroHisob CFO yechimi:** Chekli muddatli DCF bo'yicha bog' va yer ijarasi huquqi 8.4 mlrd UZS ga baholanadi, PF-82 bo'yicha foiz kompensatsiyasi orqali yillik 120 mln UZS tejaladi.

### 3-Ssenariy: Vertikal Integratsiyalashgan Paxta-To'qimachilik Klasteri ("Buxoro Agro Cluster")
- **Profil:** Buxoro viloyati, 2 500 gektar yer, paxta yetishtirishdan ip-kalava ishlab chiqarishgacha to'liq sikl.
- **Moliyaviy ko'rsatkichlar:** Yillik tushum ~45 mlrd UZS, murakkab qarz portfeli (5 ta kredit shartnomasi).
- **AgroHisob CFO yechimi:** 1C va bank ko'chirmalarini avtomatlashtirilgan konsolidatsiyasi, xususiy va korporativ mablag'larni qat'iy ajratish, 13 bo'limli institutsional Bank Dosyesi.

---

## 3. ASOSIY BO'LIMLAR BO'YICHA INTERFAOL SAYOHAT (WALKTHROUGH)

1. **Dashboard & AI-CFO Analitika (`/dashboard`):**
   - Yuqori paneldan korxona profilini o'zgartiring ("Kichik fermer", "Meva eksportchisi", "Agro klaster").
   - 12 oylik Kassa Oqimlari (Cash Flow) grafigini va DSCR dinamikasini kuzating.
   - Ssenariy slayderlarini (Hosil tushishi, Narx oshishi, Yoqilg'i narxi) suring va real vaqtda qayta hisoblashni ko'ring.
   - Deterministic AI Tavsiyalar blokida bank kreditiga tayyorgarlik bo'yicha qat'iy ko'rsatmalarni o'qing.

2. **Smart Ma'lumotlar Importi (`/data-import`):**
   - 1C, Bank ko'chirmasi yoki E-faktura namunaviy fayllarini yuklang.
   - Leksik klassifikator va dublikatlarni aniqlash mexanizmi qanday ishlashini ko'ring.
   - Shaxsiy xarajatlar korxona xarajatlaridan qanday ajratilishini tekshiring.

3. **Kredit Tayyorgarligi va Bank Dosyesi (`/credit-report`):**
   - 100 ballik kredit skoringi va 4 o'lchovli matritsani ko'ring.
   - 1-klik orqali **Professional PDF Dosye** (vektorli jadvallar va muhr bilan) yuklab oling.
   - 1-klik orqali **Jonli Formulali Excel Moliyaviy Modeli**ni (`.xlsx`) yuklab oling va formulalar ishlashini tekshiring.

4. **Garov Aktivlari va Davlat Subsidiyalari (`/collateral-subsidies`):**
   - VMQ-613 mezonlari bo'yicha yer ijarasi huquqi garovi talablarini (kadastr, 5 yillik bufer) tekshiring.
   - Chekli muddatli DCF baholash kalkulyatorida bonitet balli va diskont stavkasi bo'yicha sezgirlik tahlilini ko'ring.
   - PQ-47 (suv tejovchi texnologiyalar) va PF-82 (foiz subsidiyasi) kalkulyatorlarida tejaladigan mablag'ni hisoblang.
   - Qonuniy ogohlantirish (Statutory Disclaimer) doimo aks etishiga e'tibor bering.
