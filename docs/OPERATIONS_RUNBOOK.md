# AGROHISOB CFO — FOYDALANISH VA OPERATSION RUNBOOK (OPERATIONS RUNBOOK)

**Hujjat identifikatori:** `DOC-AH-OPS-01`  
**Sana:** 2026-11-09  
**Holat:** TASDIQLANGAN (APPROVED)  
**Tadqiqotchi guruh:** Site Reliability Engineer (SRE), Platform DevOps  

---

## 1. TIZIM MONITORINGI VA SOG'LOMLIK TEKSHIRUVLARI (HEALTH & READINESS)

AgroHisob CFO backend xizmati ikkita asosiy operatsion monitoring endpointlariga ega:

### A. Liveness Probe (`GET /health`)
- **Vazifasi:** Server va ma'lumotlar bazasi aloqasining faolligini tekshiradi.
- **Kutilayotgan javob:**
  ```json
  {
    "status": "healthy",
    "service": "agrohisob-backend",
    "version": "1.0.0-mvp",
    "engine": "Python/FastAPI Financial Engine",
    "environment": "production",
    "database": "connected"
  }
  ```
- **Kodni qaytarish:** `HTTP 200 OK`. Agar baza ulanmasa yoki kritik xato bo'lsa, avtomatik ravishda SQLite ga o'tgan holda uzilishsiz ishlaydi.

### B. Readiness Probe (`GET /ready`)
- **Vazifasi:** Trafik qabul qilishga tayyorlikni tekshiradi.
- **Kutilayotgan javob:**
  ```json
  {
    "status": "ready",
    "database": "connected",
    "engine_version": "1.0.0",
    "environment": "production"
  }
  ```

---

## 2. SERVERLARNI ISHGA TUSHIRISH VA BOSHQARISH BUYRUQLARI

### Ishlab chiqish / Lokal rejimda:
```powershell
# Backend (FastAPI / Uvicorn):
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000

# Frontend (Next.js 14):
cd frontend
pnpm run dev # yoki production test: pnpm start -p 3000
```

### Ishlab chiqarish (Production / Docker):
```bash
# Docker konteynerni yig'ish va ishga tushirish:
docker build -t agrohisob-backend:latest ./backend
docker run -d -p 8000:8000 --env-file ./backend/.env.production agrohisob-backend:latest
```

---

## 3. LOGLAR TUZILISHI VA XATOLIKLARNI TAHLIL QILISH

- **Barcha kiruvchi so'rovlar:** `X-Process-Time` sarlavhasi bilan qayd etiladi.
- **Log formati:** Python standart `logging` moduli orqali formatlangan xabarlar:
  ```
  INFO: Successfully connected to primary PostgreSQL database.
  WARNING: Could not connect to PostgreSQL (...). Falling back to local SQLite engine.
  INFO: 127.0.0.1:51234 - "POST /api/v1/financials/calculate HTTP/1.1" 200 OK
  ```
- **Fayllarni yuklash loglari:** Yuklangan fayl nomi, SHA-256 xeshi, qatorlar soni va aniqlangan dublikatlar soni qayd etiladi.

---

## 4. FAVQULODDA VAZIYATLAR VA ZAXIRAGA O'TISH (INCIDENT MANAGEMENT)

| Favqulodda Holat | Alomatlar | Tezkor Choralar |
| :--- | :--- | :--- |
| **PostgreSQL aloqasi uzilishi** | Logda `Could not connect to PostgreSQL` ogohlantirishi | Tizim avtomatik ravishda `SQLITE_FALLBACK_URL` ga o'tadi; Supabase xizmat holatini tekshirish, ulanish satrini yangilash. |
| **Yuqori xotira sarfi (OOM)** | Katta PDF yoki ko'p qatorli Excel yuklanganda xotira oshishi | Fayl hajmi 15MB bilan cheklangan; streaming generatsiya yoqilgan; zarurat bo'lsa konteyner RAM hajmini 1GB gacha oshirish. |
| **CORS xatoligi** | Brauzerda `CORS Missing Allow Origin` xabari | Backend muhitida `ALLOWED_ORIGINS` o'zgaruvchisiga yangi front domenini qo'shish va qayta yuklash. |
| **Frontend SSR xatoligi** | Next.js 500 xatosi | `NEXT_PUBLIC_BACKEND_URL` to'g'riligini va backend `/health` endpointi faolligini tekshirish. |
