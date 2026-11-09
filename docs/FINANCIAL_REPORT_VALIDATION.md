# AGROHISOB CFO — MOLIYAVIY HISOBOTLAR VALIDATSIYASI VA INTEGRITETI (ASSIGNMENT 5)

## 1. Kirish
AgroHisob CFO platformasida moliyaviy hisobotlarning aniqligi va ishonchliligi 1-darajali ustuvorlik hisoblanadi. 5-topshiriq doirasida Dashboard, PDF hisobot va Excel moliyaviy modeli o'rtasida 0% tafovutni (Zero Discrepancy Invariant) ta'minlovchi arxitektura amalga oshirildi.

---

## 2. Asosiy Moliyaviy Invariantlar

### 2.1. Kassa Hisobi Balans Qoidasi (Roll-Forward Invariant)
Har bir oy uchun va yillik yakun bo'yicha:
$$\text{Boshlang'ich Balans} + \text{Tushumlar} - \text{Chiqimlar} = \text{Yakuniy Balans}$$
Ushbu tenglik tarixiy davrda ham, prognoz davrida ham, PDF va Excelda ham qat'iy tekshiriladi.

### 2.2. Qarzga Xizmat Ko'rsatish Qoplami (DSCR)
$$\text{CFADS} = \text{Yalpi Tushum} - \text{Operatsion Chiqim (Qarzsiz)}$$
$$\text{DSCR} = \frac{\text{CFADS}}{\text{Mavjud Qarz To'lovi} + \text{Yangi Kredit To'lovi}}$$
DSCR koeffitsienti barcha taqdimot shakllarida (UI, PDF, Excel) bir xil raqam bilan aks etadi.

### 2.3. Birlashtirilgan Yagona Manba (Single Source of Truth)
- Dashboard ko'rsatkichlari, PDF sahifalaridagi jadvallar va Excel varaqlaridagi kataklar mustaqil hisoblanmaydi.
- Ular `DossierBuilder.build_dossier()` orqali yaratilgan bitta `CreditDossierData` ob'ektidan olinadi.
- Bu xatoliklarning oldini oladi va foydalanuvchi qaysi eksport turini tanlashidan qat'i nazar, bir xil raqamlarni ko'rishini kafolatlaydi.

---

## 3. Avtomatlashtirilgan Tekshiruv Natijalari
- `test_e2e_credit_dossier_cross_consistency` testi orqali eksportyor korxonasi uchun so'ralgan 500 mln so'mlik kredit parametri, prognoz tushumlar, opex va birlashgan DSCR ko'rsatkichlari Excel modeli va PDF fayllarida 100% bir xilligi tasdiqlangan.
