# AGROHISOB CFO — HISOBOT GENERATSIYA API SPETSIFIKATSIYASI (ASSIGNMENT 5)

## 1. Kirish
Kredit dosyesi va moliyaviy modelni shakllantirish, tekshirish va yuklab olish uchun FastAPI da `/api/v1/reports/*` marshrutlari ishlab chiqildi.

---

## 2. API Marshrutlari Tavsifi

### 2.1. Kredit Profilini Tekshirish
- **Metod / URI:** `POST /api/v1/reports/credit/profile`
- **Tavsif:** Arizachi korxona profili va so'ralayotgan kredit parametrlarini mantiqiy chegaralar bo'yicha tekshiradi.
- **Request Body:** `CreditProfile`
- **Response:**
  ```json
  {
    "is_valid": true,
    "errors": [],
    "credit_profile": { ... }
  }
  ```

### 2.2. Hujjatlar Nazorat Ro'yxati
- **Metod / URI:** `POST /api/v1/reports/credit/validate?organization_id=...`
- **Tavsif:** 5 toifadagi 12 ta hujjat holatini, to'liqlik foizini va izohlarini qaytaradi.
- **Response:** `DocumentReadinessChecklist`

### 2.3. Jonli Dosye Dastlabki Ko'rinishi (Live Preview)
- **Metod / URI:** `POST /api/v1/reports/credit/preview`
- **Tavsif:** UI da barcha 8 ta bo'limni real vaqtda ko'rsatish uchun kanonik `CreditDossierData` ni shakllantiradi.
- **Request Body (Ixtiyoriy):** `{ "organization_id": "...", "credit_profile": { ... } }`
- **Response:** `CreditDossierData`

### 2.4. Hisobot Fayllarini Generatsiya Qilish
- **Metod / URI:** `POST /api/v1/reports/credit/generate`
- **Tavsif:** PDF va XLSX fayllarini diskda yaratadi, SHA-256 xeshini hisoblaydi, `ReportRepository` da ro'yxatga oladi va metadata bilan qaytaradi.
- **Response:** `GeneratedReportRecord`

### 2.5. Hisobot Metadatasini Olish
- **Metod / URI:** `GET /api/v1/reports/{report_id}`
- **Tavsif:** Berilgan hisobot ID si bo'yicha fayl holati va parametrlarini qaytaradi.

### 2.6. PDF Dosyeni Yuklab Olish
- **Metod / URI:** `GET /api/v1/reports/{report_id}/download/pdf`
- **Tavsif:** Print-ready A4 PDF hujjatini attachment ko'rinishida yuklaydi (`application/pdf`).

### 2.7. Excel Moliyaviy Modelni Yuklab Olish
- **Metod / URI:** `GET /api/v1/reports/{report_id}/download/xlsx`
- **Tavsif:** 8 varaqli Excel modelini attachment ko'rinishida yuklaydi (`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`).

### 2.8. Hisobotlar Tarixi
- **Metod / URI:** `GET /api/v1/reports/history?organization_id=...`
- **Tavsif:** Korxona bo'yicha avval generatsiya qilingan barcha hisobotlar ro'yxatini qaytaradi.
