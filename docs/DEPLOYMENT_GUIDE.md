# AGROHISOB CFO — BULUTGA JOYLASHTIRISH VA ISHLAB CHIQARISH YO'RIQNOMASI (DEPLOYMENT GUIDE)

**Hujjat identifikatori:** `DOC-AH-DEP-01`  
**Versiya:** `1.0.0-mvp`  
**Sana:** 2026-11-09  
**Holat:** TASDIQLANGAN (APPROVED)  
**Tadqiqotchi guruh:** Senior DevOps, Cloud Infrastructure Architect, Platform Engineer  

---

## 1. UMUMIY KO'RINISH VA TALABLAR

Ushbu yo'riqnoma AgroHisob CFO platformasini xavfsiz, barqaror va yuqori unumdorlik bilan bulutli ishlab chiqarish (production) muhitiga joylashtirish bo'yicha to'liq amaliy qadamlarni o'z ichiga oladi.

### Kerakli hisoblar va vositalar:
1. **GitHub** — Manba kodi ombori (CI/CD quvurlari bilan ulangan).
2. **Supabase Cloud** — Boshqariladigan PostgreSQL 15+ ma'lumotlar bazasi.
3. **Railway** (yoki **Render**) — FastAPI / Python 3.12 konteyner xostingi.
4. **Vercel** — Next.js 14 frontend xostingi.

---

## 2. 1-BOSQICH: SUPABASE POSTGRESQL MA'LUMOTLAR BAZASINI SOZLASH

1. **Loyiha yaratish:**
   - Supabase boshqaruv paneliga kiring (`app.supabase.com`).
   - "New Project" tugmasini bosing va loyiha nomini kiriting: `agrohisob-prod`.
   - Mintaqani (Region) tanlang: `eu-central-1` (Frankfurt) — O'zbekiston uchun eng past kechikish vaqti.
   - Kuchli ma'lumotlar bazasi parolini generatsiya qiling va xavfsiz saqlang.

2. **Ulanish satrini (Connection String) olish:**
   - *Project Settings* -> *Database* -> *Connection String* bo'limiga o'ting.
   - **URI (Session mode)** yoki **Transaction mode (Port 6543)** ni tanlang.
   - Format namunasi:
     ```
     postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
     ```
   - *Eslatma:* AgroHisob tizimining `backend/app/db/database.py` drayveri ushbu satrni avtomatik ravishda `postgresql+psycopg2://` formatiga normallashtiradi.

3. **Jadvallarni ishga tushirish (Schema Initialization):**
   - Backend birinchi marta ishga tushganda `init_db()` orqali barcha 13 ta SQLAlchemy jadvallari avtomatik yaratiladi.

---

## 3. 2-BOSQICH: BACKEND API NI RAILWAY (YOKI RENDER) GA JOYLASHTIRISH

### A. Railway orqali joylashtirish (Tavsiya etiladi):
1. **Yangi xizmat qo'shish:**
   - Railway boshqaruv panelida `New Project` -> `Deploy from GitHub repo` ni tanlang.
   - `agroventures` repozitoriysini belgilang.
2. **Sozlamalar (Service Settings):**
   - **Root Directory:** `/backend`
   - **Build Command:** avtomatik (mavjud `backend/Dockerfile` yoki `requirements.txt` aniqlanadi).
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Muhit o'zgaruvchilari (Variables):**
   - `ENVIRONMENT` = `production`
   - `DEBUG` = `false`
   - `SECRET_KEY` = `<kuchli-kamida-32-belgili-tasodifiy-kalit>`
   - `DATABASE_URL` = `<Supabase-PostgreSQL-Ulanish-Satri>`
   - `ALLOWED_ORIGINS` = `https://agrohisob-cfo.vercel.app,https://agrohisob.uz`
4. **Health Check:**
   - Healthcheck Path: `/health` (Konteyner sog'lomligini avtomatik kuzatib boradi).
5. **Domen berish:**
   - *Networking* bo'limida Railway bepul domen yaratadi (masalan: `https://agrohisob-api-production.up.railway.app`).

---

## 4. 3-BOSQICH: FRONTENDNI VERCEL GA JOYLASHTIRISH

1. **Vercel ga loyihani import qilish:**
   - Vercel boshqaruv panelida `Add New...` -> `Project` ni tanlang.
   - GitHub repozitoriyangizni import qiling.
2. **Loyiha parametrlarini sozlash:**
   - **Framework Preset:** `Next.js`
   - **Root Directory:** `frontend` (Edit tugmasini bosib `frontend` ni tanlang).
   - **Build Command:** `pnpm run build` (yoki avtomatik).
   - **Install Command:** `pnpm install`.
3. **Environment Variables (Muhit O'zgaruvchilari):**
   - `NEXT_PUBLIC_BACKEND_URL` = `https://agrohisob-api-production.up.railway.app`
   - `NODE_ENV` = `production`
4. **Deploy tugmasini bosish:**
   - 1-2 daqiqada butun Next.js 14 frontend global CDN tarmog'ida faollashadi.

---

## 5. 4-BOSQICH: PRODUCTION RELIZINI TEKSHIRISH (SMOKE TEST CHECKLIST)

Joylashtirish tugallangach, quyidagi nazorat tekshiruvlari o'tkaziladi:

| Sinov bosqichi | Tekshiriladigan endpoint / sahifa | Kutilgan natija |
| :--- | :--- | :--- |
| **API Sog'lomligi** | `GET https://[BACKEND-URL]/health` | HTTP 200, `"status": "healthy"`, `"database": "connected"` |
| **Tayyorgarlik** | `GET https://[BACKEND-URL]/ready` | HTTP 200, `"status": "ready"` |
| **Normativ Manbalar** | `GET https://[BACKEND-URL]/api/v1/regulatory/sources` | HTTP 200, VMQ-613, PQ-47, PF-82 ro'yxati |
| **Frontend Bosh sahifa**| `GET https://[FRONTEND-URL]/` | HTTP 200, Hero bo'limi, 3 ta modul kartasi |
| **Dashboard ssenariylar**| `GET https://[FRONTEND-URL]/dashboard` | 3 ta sintetik korxona, kassa grafigi va DSCR to'liq chiqishi |
| **PDF Hisobot yuklash** | `POST .../api/v1/reports/credit-readiness/pdf` | Valid `application/pdf` baytlari yuklanishi |
| **Excel Model yuklash** | `POST .../api/v1/reports/credit-readiness/excel` | Valid `application/vnd.openxmlformats...` yuklanishi |

---

## 6. DISASTER RECOVERY VA ORQAGA QAYTISH (ROLLBACK PROCEDURES)

1. **Frontend orqaga qaytarish:**
   - Vercel boshqaruv panelida *Deployments* ro'yxatidan oldingi barqaror reliz tanlanadi va "Instant Rollback" bitta tugma bilan faollashtiriladi (nol uzilish bilan).
2. **Backend orqaga qaytarish:**
   - Railway / Render da avvalgi muvaffaqiyatli commit tegi yoki konteyner tasviri tanlanib "Rollback" bosiladi.
3. **Ma'lumotlar bazasi xavfsizligi:**
   - Supabase Point-In-Time-Recovery (PITR) yordamida ma'lumotlar bazasini istalgan daqiqadagi holatga qaytarish mumkin.
