# AGROHISOB CFO — MULTILINGUAL COLUMN MAPPING SPECIFICATION

**Hujjat kodi:** `DOC-AGRO-A3-MAP-003`  
**Holati:** TASDIQLANGAN (APPROVED)  
**Versiya:** 1.0.0  

---

## 1. KONSEPSIYA

O'zbekistondagi buxgalteriya va bank hisobotlarida ustun nomlari turli tillarda va har xil atamalar bilan yuritiladi. **AgroHisob CFO ColumnMapper** moduli quyidagi 12 ta tizimli kanonik maydonga ega bo'lib, ularni avtomatik tarzda aniqlaydi va biriktiradi.

---

## 2. KANONIK MAYDONLAR VA SINONIMLAR MATRITsASI

| Kanonik Maydon | Tavsif | O'zbek (Lotin) Sinonimlari | O'zbek (Kirill) Sinonimlari | Rus Tili Sinonimlari | Majburiylik |
|---|---|---|---|---|---|
| `transaction_date` | Tranzaksiya yoki faktura sanasi | sana, operatsiya sanasi, o'tkazma sanasi, hujjat sanasi, to'lov sanasi, vaqt, data, kun | сана, операция санаси, ўтказма санаси, тўлов санаси, ҳужжат санаси, вақт, кун | дата, дата операции, дата проводки, дата документа, дата платежа, число, дата с/ф | **HA (Barcha turlarda)** |
| `amount` | Tranzaksiya yoki faktura umumiy summasi | summa, operatsiya summasi, to'lov summasi, jami, jami summa, miqdor, qiymat, umumiy summa | сумма, операция суммаси, тўлов суммаси, жами, жами сумма, қиймат, умумий сумма | сумма, сумма операции, сумма платежа, всего, итого, сумма с ндс, размер, общая сумма | **HA (yoki debet+kredit)** |
| `direction` | Tranzaksiya yo'nalishi (Kirim / Chiqim) | yo'nalish, turi, operatsiya turi, harakat, kirim/chiqim | йўналиш, тури, операция тури, ҳаракат, кирим/чиқим | тип операции, направление, вид операции, приход/расход | Yo'q (Summa ishorasi yoki debet/kreditdan aniqlanadi) |
| `debit` | Chiqim / Xarajat summasi | debet, chiqim, xarajat, debet summasi | дебет, чиқим, харажат, дебет суммаси | дебет, расход, списание, сумма дебета | Split rejimda majburiy |
| `credit` | Kirim / Tushum summasi | kredit, kirim, tushum, kredit summasi | кредит, кирим, тушум, кредит суммаси | кредит, приход, поступление, зачисление, сумма кредита | Split rejimda majburiy |
| `counterparty_name` | Hamkor yoki tashkilot nomi | kontragent, hamkor, tashkilot, ta'minotchi, xaridor, yetkazib beruvchi, oluvchi, to'lovchi, korxona nomi | контрагент, ҳамкор, ташкилот, таъминотчи, харидор, етказиб берувчи, олувчи, тўловчи, корхона номи | контрагент, наименование контрагента, поставщик, покупатель, организация, плательщик, получатель | **HA (Barcha turlarda)** |
| `counterparty_inn` | Kontragent STIR (INN) raqami (9 xona) | inn, stir, kontragent inn, kontragent stir, stir/inn, xaridor inn, sotuvchi inn | инн, стир, контрагент инн, стир/инн | инн, инн контрагента, инн/кпп, инн плательщика, инн получателя, инн покупателя | Tavsiya etiladi |
| `document_number` | Faktura yoki to'lov topshiriqnomasi raqami | hujjat raqami, faktura raqami, shartnoma raqami, hisobvaraq-faktura raqami, sf raqami, order raqami, raqam | ҳужжат рақами, фактура рақами, шартнома рақами, рақам | номер документа, номер, № документа, номер счет-фактуры, счет-фактура №, документ №, номер п/п | Soliq E-Fakturada tavsiya etiladi |
| `purpose` | To'lov maqsadi yoki mahsulot tavsifi | to'lov maqsadi, tavsif, izoh, mazmuni, maqsad, to'lov tafsilotlari, tovar/xizmat nomi | тўлов мақсади, тавсиф, изоҳ, мазмуни, товар номи, хизмат номи | назначение платежа, описание, содержание, назначение, товар/услуга, наименование товара | Toifalash uchun muhim |
| `mxik_code` | Davlat Soliq Qo'mitasi MXIK (IKPU) kodi | mxik, mxik kodi, ikpu, ikpu kodi, mxik/ikpu, tovar kodi, mahsulot kodi | мхик, мхик коди, икпу, икпу коди, мхик/икпу | код икпу, икпу, мхик, код мхик, код товара, икпу код | Soliq E-Fakturada muhim |
| `vat_amount` | QQS (NDS) summasi | qqs, qqs summasi, qo'shilgan qiymat solig'i, nds | ққс, ққс суммаси | ндс, сумма ндс, налог на добавленную стоимость, в т.ч. ндс | Soliq E-Fakturada |
| `bank_account` | Kontragentning 20 xonali hisob raqami | hisob raqam, hisobraqam, h/r, korxona hisob raqami, kontragent hisob raqami | ҳисоб рақам, ҳ/р | расчетный счет, р/с, счет, счет плательщика, счет получателя | Bank ko'chirmasida |

---

## 3. MOSLIK DARAJASINI HISOBLASH (CONFIDENCE SCORING)

Ustunlarni bog'lashda quyidagi koeffitsientlar qo'llaniladi:
- **1.0 (100%):** Lug'atdagi sinonim bilan to'liq harfma-harf moslik (katta-kichik harflar va bo'shliqlar normallashtirilgandan so'ng).
- **0.90 (90%):** Qisman yoki qo'shimcha so'zlar bilan moslik (masalan, `Sana (kun/oy/yil)` -> `transaction_date`).
- **0.60 - 0.85:** Matn ichida sinonim so'zining uchrashi (substring match).
- **< 0.50:** Moslik hisobga olinmaydi va foydalanuvchi interfeysida qo'lda tanlash taklif etiladi.
