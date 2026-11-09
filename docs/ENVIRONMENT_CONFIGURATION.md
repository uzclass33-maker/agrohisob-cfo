# AGROHISOB CFO — MUHIT O'ZGARUVCHILARI VA SOZLAMALAR MA'LUMOTNOMASI (ENVIRONMENT CONFIGURATION)

**Hujjat identifikatori:** `DOC-AH-ENV-01`  
**Sana:** 2026-11-09  
**Holat:** TASDIQLANGAN (APPROVED)  

---

## 1. BACKEND MUHIT O'ZGARUVCHILARI (`backend/.env`)

Quyidagi jadvalda backend tizimi uchun barcha konfiguratsion kalitlar keltirilgan:

| O'zgaruvchi nomi | Standart (Default) qiymat | Tavsifi va Ishlab chiqarish talabi |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | Ishlash muhiti: `development`, `staging`, yoki `production`. Productionda debug cheklanadi. |
| `DEBUG` | `true` | Xatoliklarni to'liq ko'rsatish bayrog'i. Productionda qat'iy ravishda `false` bo'lishi shart. |
| `DATABASE_URL` | `postgresql://agrohisob:...` | Asosiy PostgreSQL / Supabase ulanish satri. Mavjud bo'lmasa, SQLite ga avtomatik o'tadi. |
| `SQLITE_FALLBACK_URL`| `sqlite:///./agrohisob_local.db`| Lokal yoki oflayn testlar uchun lokal ma'lumotlar bazasi zaxira yo'li. |
| `SECRET_KEY` | `agrohisob-dev-secret...` | JWT va sessiya shifrlash kaliti. Productionda kamida 32 ta tasodifiy belgi bo'lishi shart! |
| `ALLOWED_ORIGINS` / `CORS_ORIGINS` | `http://localhost:3000,...` | Vergul bilan ajratilgan ruxsat etilgan domenlar ro'yxati (masalan, `https://agrohisob-cfo.vercel.app`). |
| `API_V1_PREFIX` | `/api` | RESTful API marshrutlari prefiksi. |
| `DEFAULT_CBU_POLICY_RATE`| `0.14` | O'zbekiston Markaziy Banki asosiy stavkasi (14.0% — 2026-yil noyabr holati). |
| `COMMERCIAL_LOAN_RATE` | `0.235` | Tijorat agro-kreditlarining o'rtacha bozor stavkasi (23.5%). |
| `PREFERENTIAL_AGRO_RATE`| `0.14` | Imtiyozli qishloq xo'jaligi kreditlari stavkasi (14.0%). |
| `MIN_ACCEPTABLE_DSCR` | `1.25` | O'zbekiston tijorat banklarining minimal qarz qoplash koeffitsienti talabi (DSCR). |

---

## 2. FRONTEND MUHIT O'ZGARUVCHILARI (`frontend/.env.local`)

| O'zgaruvchi nomi | Standart qiymat | Tavsifi |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_BACKEND_URL` | `http://127.0.0.1:8000` | Backend API ga ulanishning ommaviy domeni (masalan, `https://api.agrohisob.uz`). |
| `NODE_ENV` | `development` | Node.js ishlash rejimi (`production` yoki `development`). |

---

## 3. AMALIY NAMUNALAR (.ENV.EXAMPLE)

### Backend Namunaviy Ishlab Chiqarish Fayli (`backend/.env.production.example`):
```ini
# Production Environment Variables
ENVIRONMENT=production
DEBUG=false
APP_NAME=AgroHisob CFO
APP_VERSION=1.0.0-mvp

# Security Keys (Generate via: openssl rand -hex 32)
SECRET_KEY=9f82d1c7a8b3e4f50123456789abcdef9f82d1c7a8b3e4f50123456789abcdef

# Supabase Production PostgreSQL Database
DATABASE_URL=postgresql://postgres.xxx:strongpassword@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

# Dynamic CORS Allowed Origins
ALLOWED_ORIGINS=https://agrohisob-cfo.vercel.app,https://agrohisob.uz,https://www.agrohisob.uz

# Regulatory & Banking Benchmarks
DEFAULT_CBU_POLICY_RATE=0.14
COMMERCIAL_LOAN_RATE=0.235
PREFERENTIAL_AGRO_RATE=0.14
MIN_ACCEPTABLE_DSCR=1.25
```

### Frontend Namunaviy Ishlab Chiqarish Fayli (`frontend/.env.production.example`):
```ini
NEXT_PUBLIC_BACKEND_URL=https://agrohisob-api-production.up.railway.app
NODE_ENV=production
```

---

## 4. SIRLARNI BOSHQARISH VA XAVFSIZLIK QOIDALARI

1. **Git omboriga kiritmaslik:** Hech qachon haqiqiy `.env` fayllarini `git add` qilmang. Ular `.gitignore` da qat'iy belgilangan.
2. **Konteyner sirlari:** Railway, Render va Vercel da o'zgaruvchilarni faqat boshqaruv panelidagi *Environment Variables* xavfsiz bo'limiga kiriting.
3. **Kalitlarni yangilash (Rotation):** Har 90 kunda yoki har bir katta relizda `SECRET_KEY` va ma'lumotlar bazasi parollari yangilab borilishi lozim.
