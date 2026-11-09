# AGROHISOB CFO — THREE-TIER AGRICULTURAL CLASSIFICATION ENGINE

**Hujjat kodi:** `DOC-AGRO-A3-CLS-005`  
**Holati:** TASDIQLANGAN (APPROVED)  
**Versiya:** 1.0.0  

---

## 1. TASNIFLASH FALSAFASI VA STRUKTURASI

AgroHisob CFO platformasi fermer xo'jaliklarining daromad va xarajatlarini O'zbekiston qishloq xo'jaligi iqtisodiyoti uchun xos bo'lgan 18 ta standart toifaga ajratadi. Toifalash jarayoni deterministik bo'lib, ierarxik 3 bosqichli pipeline orqali amalga oshiriladi:

```
Tranzaksiya ma'lumotlari
         │
         ▼
[1-bosqich: MXIK (IKPU) Lug'ati] ──(Topilsa)──► 95% - 98% ishonchlilik (Rule: MXIK_DICTIONARY)
         │ (Topilmasa)
         ▼
[2-bosqich: Kalit So'zlar Hevristikasi] ──(Topilsa)──► 90% - 92% ishonchlilik (Rule: KEYWORD_HEURISTIC)
         │ (Topilmasa)
         ▼
[3-bosqich: Kontragent Profili] ──(Topilsa)──► 85% - 95% ishonchlilik (Rule: COUNTERPARTY_RULE)
         │ (Topilmasa)
         ▼
[4-bosqich: Zaxira Tasniflagich] ────────► 30% ishonchlilik (UNCATEGORIZED_EXPENSE / UNCATEGORIZED_INCOME)
```

---

## 2. 1-BOSQICH: MXIK (IKPU) KODLARI BO'YICHA XARITALASH

O'zbekiston Respublikasi Davlat Soliq Qo'mitasining klassifikatori prefikslari bo'yicha to'g'ridan-to'g'ri biriktirish:

| MXIK Prefiksi | Agronomik Toifa | O'zbekcha Nomi | Ishonchlilik |
|---|---|---|---|
| `01.11` | `CROP_SALES_GRAIN` | G'alla va don mahsulotlari sotuvi | 98% |
| `01.16` | `CROP_SALES_COTTON` | Paxta xomashyosi sotuvi | 98% |
| `01.13`, `01.21`, `01.24`, `01.25` | `CROP_SALES_HORTICULTURE` | Bog'dorchilik va sabzavotlar sotuvi | 95% |
| `01.64` | `SEEDS_SEEDLINGS` | Urug'lik va ko'chatlar | 95% |
| `20.15`, `20.20` | `FERTILIZER_CHEMICALS` | Mineral o'g'itlar va agroximiya | 98% |
| `19.20` | `FUEL_LUBRICANTS` | Yoqilg'i va moylash materiallari (Dizel/GSM) | 98% |
| `01.61`, `68.20`, `77.31` | `MACHINERY_SERVICES` | Texnika ijarasi va agrotexnik xizmatlar | 95% |
| `36.00` | `IRRIGATION_WATER` | Sug'orish suvi va suv xo'jaligi | 95% |
| `65.12` | `INSURANCE_AGRO` | Qishloq xo'jaligi mulkiy sug'urtasi | 95% |
| `84.11` | `TAXES_DUTIES` | Yagona yer solig'i va majburiy to'lovlar | 95% |
| `64.19` | `DEBT_SERVICE` | Bank kreditlari va foiz to'lovlari | 95% |

---

## 3. 2-BOSQICH: KO'P TILLI KALIT SO'ZLAR (KEYWORD HEURISTICS)

Bank to'lov maqsadi matnidagi kalit so'zlarni tahlil qilish (o'zbek lotin, o'zbek kirill, rus):

1. **Mineral o'g'itlar (`FERTILIZER_CHEMICALS`):**
   - o'g'it, ogit, o‘g‘it, удобрение, azot, азот, ammofos, аммофос, karbamid, карбамид, selitra, селитра, fosfor, kaliy, gerbitsid, pestitsid, defoliant, ximikat, kimyoviy.
2. **Yoqilg'i va GSM (`FUEL_LUBRICANTS`):**
   - yoqilg'i, dizel, дизель, solyarka, солярка, benzin, бензин, gsm, гсм, moy, avtol, автол, yoqilg'i-moylash, дизтопливо.
3. **Urug'lik va ko'chatlar (`SEEDS_SEEDLINGS`):**
   - urug', urug, семена, chigit, чигит, urug'lik, ko'chat, саженцы, don urug'i, elita urug'.
4. **Agrotexnika va MTP (`MACHINERY_SERVICES`):**
   - traktor, трактор, kombayn, комбайн, haydash, kultivatsiya, plug, zapchast, ehtiyot qism, mtp, agrotexnik xizmat.
5. **Ish haqi va terimchilar (`LABOR_PAYROLL`):**
   - ish haqi, oylik, zarplata, зарплата, maosh, mehnat haqi, terim puli, paxta terimi, avans ishchi, fzp.
6. **Sug'orish suvi (`IRRIGATION_WATER`):**
   - suv, nasos, вода, irrigatsiya, ирригация, suv xo'jaligi, suv yetkazib berish, ariq, kanal, nasos stansiyasi.
7. **Kredit va bank xizmatlari (`DEBT_SERVICE`):**
   - kredit, кредит, kredit foizi, foiz to'lovi, ssuda, ссуда, asosiy qarz, bank komissiyasi, kredit so'ndirish.
8. **Soliqlar (`TAXES_DUTIES`):**
   - soliq, налог, yagona yer solig'i, yer solig'i, ndfl, ндфл, daromad solig'i, davlat boji.
9. **Subsidiyalar (`SUBSIDY_GRANTS`):**
   - subsidiya, субсидия, davlat granti, grant, kompensatsiya, tomchilatib sug'orish subsidiyasi.

---

## 4. 3-BOSQICH: KONTRAGENT PROFILI BO'YICHA BIRIKTIRISH

Agar to'lov maqsadida mahsulot nomi ko'rsatilmagan bo'lsa (masalan: "Shartnoma №12 bo'yicha to'lov"), kontragentning nomi tekshiriladi:
- `Farg'onaAzot`, `NavoiyAzot`, `Maxam-Chirchiq`, `Dehqonobod` -> `FERTILIZER_CHEMICALS`
- `O'zbekneftgaz`, `UNG Petro`, `Neftebaza`, `Lukoil` -> `FUEL_LUBRICANTS`
- `Agrobank`, `Qishloq Qurilish Bank`, `Biznesni Rivojlantirish Banki`, `Mikrokreditbank` -> `DEBT_SERVICE`
- `Suv Ta'minoti`, `Suv Xo'jaligi Boshqarmasi` -> `IRRIGATION_WATER`

---

## 5. FOYDALANUVChI TAHRIRI (MANUAL OVERRIDE)

Avtomatik tasniflash natijasidan qat'i nazar, foydalanuvchi qoralama jadvalida (staging table) har qanday tranzaksiyaning toifasini o'z xohishiga ko'ra o'zgartirishi mumkin. Qo'lda o'zgartirilgan toifalar `MANUAL_USER_OVERRIDE` manbasi va `1.0` (100%) ishonchlilik bilan belgilanadi.
