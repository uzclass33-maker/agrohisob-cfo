# AgroHisob CFO — Moliyaviy Vizualizatsiya Standartlari

## 1. Ranglar Palitrasi va Semantik Ma'nolar

- **Tushumlar (Inflows)**: Emerald Green (`#10b981`, `bg-emerald-500`, `text-emerald-700`).
- **Chiqimlar (Outflows)**: Crimson Rose (`#f43f5e`, `bg-rose-500`, `text-rose-700`).
- **Kassa Qoldig'i (Closing Balance)**: Sky Blue (`#0284c7`, `bg-sky-500`, `text-sky-700`).
- **Qarz Xizmati (Debt Service)**: Amber / Deep Orange (`#d97706`, `bg-amber-500`, `text-amber-700`).
- **Kassa Taqchilligi (Deficit Alert)**: Dark Red Alert (`#be123c`, `bg-rose-100`, `text-rose-800`).

## 2. Recharts Grafik Konfiguratsiyasi

- `ComposedChart`:
  - `Bar` komponenti oylik tushum va chiqimlarni taqqoslash uchun ishlatiladi.
  - `Line` komponenti (Sky Blue, strokeWidth 3) kassa qoldig'i dinamikasini ko'rsatadi.
  - `ReferenceLine (y=0)`: Kassa taqchilligi chegarasini ajratib ko'rsatadi.
  - `CustomTooltip`: O'zbek tilida oylik ko'rsatkichlarni (Yalpi Tushum, Jami Chiqim, Sof Kassa Oqimi, Yakuniy Kassa) to'liq formatlangan UZS summalari bilan aks ettiradi.

## 3. Sonlarni Formatlash

- Standart format: `formatUZS(val)` &rarr; `120 000 000,00 so'm`
- Yilqiq ixcham format: `formatCompactUZS(val)` &rarr; `120,0 mln so'm` yoki `4,85 mlrd so'm`
- Koeffitsientlar: `dscr.toFixed(2)x` &rarr; `1.42x`
