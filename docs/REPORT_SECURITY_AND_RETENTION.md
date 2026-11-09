# AGROHISOB CFO — HISOBOTLAR XAVFSIZLIGI VA SAQLASH SIYOSATI (ASSIGNMENT 5)

## 1. Kirish
Kredit dosyelari va moliyaviy modellar tijorat siri va bank anderraytingiga tegishli maxfiy moliyaviy ma'lumotlarni o'z ichiga oladi. Mazkur hujjat ushbu hisobotlarning saqlanishi, himoyasi va foydalanish xavfsizligini belgilaydi.

---

## 2. Xavfsizlik Qoidalari va Himoya Mexanizmlari

### 2.1. Fayl In'eksiyasi va Formula Xavfsizligi
- Excel modellarida foydalanuvchi tomonidan kiritilgan nomlar, korxona faoliyati va izohlar kataklarga yozilishdan avval `_sanitize_cell_text()` funksiyasidan o'tkaziladi.
- Agar satr `=`, `+`, `-`, `@` belgilaridan biri bilan boshlansa, uning boshiga bitta tirnoq (`'`) qo'shilib, uning formula sifatida xavfli bajarilishi (Formula Injection / CSV Injection) to'xtatiladi.

### 2.2. SHA-256 Kriptografik Xeshlar
- Har bir yaratilgan PDF fayli uchun `hashlib.sha256` orqali nazorat xeshi hisoblanadi.
- Bu xesh faylning keyinchalik o'zgartirilmaganligini va asl holatini tasdiqlovchi raqamli tamg'a vazifasini bajaradi.

### 2.3. Fayllarni Diskda Saqlash va Izolyatsiya
- Barcha generatsiya qilingan hisobotlar `backend/storage/reports/` katalogida saqlanadi.
- Har bir fayl nomi takrorlanmas `report_id` (masalan: `rep-de92fd5dfe52_scenario-small-farmer_dossier.pdf`) bilan saqlanadi.
- To'g'ridan-to'g'ri statik web orqali fayl tizimiga kirish bloklangan. Yuklab olish faqat FastAPI ning `FileResponse` nazoratidan o'tgan holda amalga oshiriladi.

### 2.4. Saqlash Muddati va Tozalash (Retention Policy)
- Generatsiya qilingan hisobotlar 90 kun davomida faol reestrda saqlanadi.
- Keraksiz yoki eskirgan hisobotlar `ReportRepository.delete_report(report_id)` orqali fayllari bilan birga xavfsiz o'chirilishi mumkin.
