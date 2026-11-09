# AGROHISOB CFO — GIT RELEASE & VERSIONING CHECKLIST

**Hujjat identifikatori:** `DOC-AH-REL-01`  
**Versiya:** `1.0.0-mvp`  
**Sana:** 2026-11-09  
**Holat:** TASDIQLANGAN (APPROVED)  

---

## 1. RELEASE STRATEGIYASI VA GITHUB XAVFSIZLIGI

AgroHisob CFO platformasi O'zbekiston agrobiznes korxonalari va moliya institutlari uchun xizmat ko'rsatuvchi muhim FinTech tizimi bo'lganligi sababli, versiyalarni boshqarish va kodni chiqarish (release) jarayoni quyidagi qat'iy standartlarga asoslanadi:

### Asosiy Branch Qoidalari:
1. `master` / `main` — Faqat barqaror, barcha testlardan 100% o'tgan, production darajasidagi kod saqlanadi. Branch himoyasi (Branch Protection Rules) yoqilgan bo'lishi shart.
2. `develop` — Yangi xususiyatlar (features) va topshiriqlar integratsiya qilinadigan asosiy ishchi shoxobcha.
3. `feature/AH-*` — Alohida modullar, kalkulyatorlar yoki UI komponentlarini ishlab chiqish uchun qisqa muddatli branchlar.
4. `release/v1.0.0-mvp` — Productionga chiqarilayotgan yig'ma reliz branchi.

---

## 2. RELEASE OLDIDAN MAJBURIY TEKSHIRUV RO'YXATI (PRE-RELEASE CHECKLIST)

Har qanday production relizidan oldin quyidagi nazorat punktlari bajarilishi shart:

### A. Kod va Arxitektura Sifati
- [x] Barcha Python fayllari sintaktik jihatdan to'g'ri va kompyutatsiyaga tayyor (`py_compile`).
- [x] TypeScript turlari qat'iy tekshirilgan, interfeyslar backend Pydantic schemalariga to'liq mos keladi.
- [x] Dead code, ishlatilmayotgan importlar va xatolik keltirib chiqaruvchi qismlar tozalandi.
- [x] Frontend Next.js production rejimida muvaffaqiyatli build bo'ladi (`pnpm run build`).

### B. Sinovlar va Avtomatlashtirilgan Audit
- [x] Barcha 153+ ta avtomatlashtirilgan testlar to'liq o'tgan (`python -m pytest backend/tests` — 100% PASS).
- [x] End-to-End (E2E) asosiy foydalanuvchi yo'llari (Dashboard, Import, Kredit Dosyesi, Garov/Subsidiya) sinovdan o'tkazildi.
- [x] Live audit endpointlari (`/health`, `/ready`, `/api/v1/demo/organizations`) 200 OK qaytarmoqda.

### C. Xavfsizlik va Maxfiylik (Security & Secrets Hygiene)
- [x] Kod bazasida hech qanday ishlab chiqarish (production) API kalitlari, Supabase parollari yoki bank tokenlari saqlanmagan.
- [x] `.env` fayli `.gitignore` ga kiritilgan; barcha muhit o'zgaruvchilari `.env.example` da namunaviy hujjatlashtirilgan.
- [x] CORS siyosati tashqi ruxsat etilgan domenlarni (`ALLOWED_ORIGINS`) dinamik qo'llab-quvvatlaydi.
- [x] HTTP xavfsizlik sarlavhalari (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`) faollashtirildi.

### D. Foydalanuvchi va Normativ Talablar
- [x] Barcha garov va subsidiya hisobotlarida davlat litsenziyasiga ega mustaqil baholovchi emasligi haqidagi qonuniy ogohlantirish (Statutory Non-Certification Disclaimer) mavjud.
- [x] 3 ta sintetik korxona (Kichik fermer, Meva eksportchisi, Agromahsulot klasteri) to'liq va uzluksiz ishlamoqda.
- [x] PDF va Excel hisobotlarida hisoblangan sonlar bilan foydalanuvchi interfeysidagi sonlar o'rtasida 0% tafovut ta'minlangan.

---

## 3. GIT RELIZINI YARATISH BO'YICHA QADAMLAR

Lokal o'zgarishlarni Git omboriga xavfsiz qo'shish va teglash:

```bash
# 1. Barcha o'zgarishlarni tekshirish
git status

# 2. Ishlab chiqarish fayllarini indekslash
git add backend/ frontend/ docs/ .github/ .gitignore README.md

# 3. Aniq va standartlashtirilgan commit yaratish
git commit -m "chore(release): v1.0.0-mvp production-ready release with security hardening, full test suite & cloud configs"

# 4. Versiya tegini yaratish
git tag -a v1.0.0-mvp -m "AgroHisob CFO v1.0.0-mvp: Security hardened, 153/153 tests pass, cloud ready"

# 5. Tashqi repository mavjud bo'lganda push qilish (Foydalanuvchi tasdig'i bilan)
# git push origin master --tags
```
