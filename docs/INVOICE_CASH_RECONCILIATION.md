# AGROHISOB CFO — INVOICE VS. CASH RECONCILIATION & LEDGER SEPARATION

**Hujjat kodi:** `DOC-AGRO-A3-REC-006`  
**Holati:** TASDIQLANGAN (APPROVED)  
**Versiya:** 1.0.0  

---

## 1. FUNDAMENTAL BUXGALTERIYA INVARIANTI

Klassik qishloq xo'jaligi buxgalteriyasi va anderraytingida eng ko'p uchraydigan xatolik — bu hisobvaraq-faktura (e-faktura) hisobdan chiqarilishi bilanoq uni real naqd pul tushumi yoki xarajati sifatida qayd etishdir. 

O'zbekiston qonunchiligi va xalqaro buxgalteriya standartlariga muvofiq:
> **INVOYS $\neq$ NAQD PUL**  
> Hisobvaraq-faktura bu tijorat majburiyatidir (Debitorlik / Kreditorlik qarz). U korxonaning bank hisobvarag'idagi real pul qoldig'ini (Cash Balance) oshirmaydi yoki kamaytirmaydi.

AgroHisob CFO platformasi ushbu qoidani tizim darajasida majburiy invariant sifatida tatbiq etadi:
1. **Soliq E-Faktura (Invoice Obligation Ledger):** Faqat majburiyatlar reestriga yoziladi. U kassa/bank qoldig'iga kiritilmaydi. Agar foydalanuvchi yoki so'rov e-fakturani kassa reestriga kiritishga urinsa, tizim `LedgerSeparationViolationError` xatoligini chiqaradi.
2. **Bank Aylanmasi (Cash Transaction Ledger):** Bank hisobvarag'i ko'chirmasidagi har bir tasdiqlangan tranzaksiya to'g'ridan-to'g'ri kassa reestriga yoziladi, davriy sof pul oqimini (Net Cash Flow) va DSCR (qarzni qoplash koeffitsienti) ko'rsatkichini qayta hisoblaydi.

---

## 2. REESTRLARNING TUZILISHI VA FARQI

| Xususiyat | Invoys Majburiyatlari Reestri (`INVOICE_LEDGER`) | Kassa Tranzaksiyalari Reestri (`CASH_LEDGER`) |
|---|---|---|
| **Hujjat turi** | Soliq.uz E-Faktura, Shartnoma, Tovar-transport yukxati | Bank hisobvarag'i aylanmasi (Agrobank, Ipak Yo'li, Kapitalbank) |
| **Iqtisodiy mohiyati** | Debitorlik / Kreditorlik qarzdorligi (AR/AP) | Real pul harakati (Cash Inflow / Cash Outflow) |
| **Kassa balansiga ta'siri** | **0 so'm (Mutlaqo ta'sir qilmaydi)** | **To'g'ridan-to'g'ri ta'sir qiladi ($\pm \Delta Cash$)** |
| **Hisobotdagi o'rni** | Balance Sheet (Aktiv/Passiv majburiyatlar), QQS hisobi | Cash Flow Statement (Haqiqiy pul oqimlari to'g'risida hisobot) |
| **Anderraytingdagi roli** | Fermerning to'lanmagan qarz yukini ko'rsatadi | Fermerning kredit to'lashga qodirligini (DSCR) ko'rsatadi |

---

## 3. O'ZARO SOLISHTIRUV (RECONCILIATION) ALGORITMI

Tizim ochiq (to'lanmagan) hisobvaraq-fakturalarni kelib tushgan bank o'tkazmalari bilan avtomatik tarzda bog'laydi:
1. **STIR (INN) mosligi:** Invoysdagi kontragent STIRi bank tranzaksiyasidagi STIR bilan tekshiriladi.
2. **Summa tengligi:** Invoysning to'liq summasi bank to'lov summasi bilan solishtiriladi.
3. **Sana xronologiyasi:** Bank to'lovi sanasi invoys chiqarilgan sanadan keyin yoki bir xil bo'lishi shart ($T_{bank} \ge T_{invoice}$).
4. **Holat yangilanishi:**
   - Moslik topilganda: Invoys holati `SETTLED` (To'langan) ga o'zgaradi, uning ochiq debitorlik/kreditorlik qarzi 0 ga tenglashtiriladi va unga bog'langan bank tranzaksiyasi IDsi saqlanadi.
