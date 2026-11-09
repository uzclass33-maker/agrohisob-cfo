# AgroHisob CFO — Moliyaviy Xavflar Monitoring Qoidalari

## 1. Deterministik Risk Qoidalari

| Risk ID | Nomi | Severity | Trigger Qoidasi | Biznes Ma'nosi |
| :--- | :--- | :--- | :--- | :--- |
| `risk-deficit` | Kassa Taqchilligi (Kassa Uzilishi) | **CRITICAL** | `Closing Balance < 0` | Korxona ekin ekish davrida o'z majburiyatlarini to'lash uchun yetarli naqd pulga ega emas. |
| `risk-buffer` | Xavfli Past Likvidlik Buferi | **HIGH** | `Closing < 15% Buffer` | Kutilmagan narx oshishi yoki noqulay ob-havo holatida to'lov qobiliyati yo'qolish xavfi. |
| `risk-dscr` | Qarz Qoplash Xatari (DSCR) | **CRITICAL / HIGH** | `Annual DSCR < 1.20x` | Korxona erkin operatsion kassa oqimi bank kreditini xavfsiz to'lashga yetarli emas. |
| `risk-seasonality` | Tushumlar Konsentratsiyasi | **MEDIUM** | `Harvest Months <= 3` | Yillik tushumning 70%+ qismi 3 oydan kamroq davrda to'plangan. |

## 2. Boshqaruv Choralari (Mitigation Actions)

1. **Kassa uzilishida**: Imtiyozli 14% stavkali Agrobank aylanma krediti yoki klasterdan fyuchers avansi jalb qilish.
2. **Past buferda**: Zaruriy bo'lmagan kapital xarajatlarni hosil terimi tugaguncha qoldirish.
3. **DSCR bosimida**: Bank bilan kredit to'lov grafigini mavsumiy daromad oylariga moslashtirish (annuitetdan hosil davriga moslashgan grafikga o'tish).
4. **Mavsumiylikda**: Oraliq ekinlar va issiqxona xo'jaligi hisobiga erta bahorgi tushumlarni diversifikatsiya qilish.
