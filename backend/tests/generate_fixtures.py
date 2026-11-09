import os
import openpyxl

fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
os.makedirs(fixtures_dir, exist_ok=True)

# 1. Bank Statement CSV
bank_csv_content = """Sana;Debet;Kredit;Kontragent;INN;Hujjat raqami;To'lov maqsadi
2026-03-12;28000000;;Farg'onaAzot AJ;200025114;PP-101;Mineral o'g'it ammofos va selitra xaridi uchun
2026-03-24;18500000;;O'zbekneftgaz YoQSh;200115542;PP-102;Dizel yoqilg'isi solyarka uchun to'lov
2026-04-10;12000000;;Urug'chilik Klasteri;204551234;PP-103;Bug'doy va g'alla elita urug'lik xaridi
2026-06-18;;85000000;O'zdonmahsulot filial;302998877;PO-201;G'alla hosili topshirishdan tushum
2026-07-22;;160000000;Toshkent Agro Klaster;305112233;PO-202;Paxta xomashyosi topshirishdan tushum
2026-08-05;9500000;;Agrobank ATB;200000001;PP-104;Kredit asosiy qarz va foiz to'lovi
2026-09-10;4200000;;Davlat Soliq Boshqarmasi;201122334;PP-105;Yagona yer solig'i to'lovi
"""

csv_path = os.path.join(fixtures_dir, "sample_bank_statement.csv")
with open(csv_path, "w", encoding="utf-8") as f:
    f.write(bank_csv_content)

# 2. Soliq E-Faktura XLSX
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Hisobvaraq-fakturalar"

headers = [
    "Sana",
    "Faktura raqami",
    "Yetkazib beruvchi",
    "Xaridor",
    "Yetkazib beruvchi STIR",
    "Xaridor STIR",
    "MXIK kodi",
    "Tovar va xizmatlar tavsifi",
    "Summa",
    "QQS summasi",
]
ws.append(headers)

rows = [
    ["2026-03-15", "SF-2026/0114", "Farg'onaAzot AJ", "Agro Ventures Farm MChJ", "200025114", "309876543", "20.15.10.101", "Karbamid va ammofos mineral o'g'itlari", 28000000, 3360000],
    ["2026-03-22", "SF-2026/0290", "O'zbekneftgaz YoQSh", "Agro Ventures Farm MChJ", "200115542", "309876543", "19.20.21.000", "Dizel yoqilg'isi E-5 (solyarka)", 18500000, 2220000],
    ["2026-04-05", "SF-2026/0441", "MTP Agrotexnika Servis MChJ", "Agro Ventures Farm MChJ", "205667788", "309876543", "01.61.10.000", "Traktor haydov va kultivatsiya xizmatlari", 14000000, 1680000],
    ["2026-07-28", "SF-2026/0890", "Agro Ventures Farm MChJ", "Toshkent Agro Klaster MChJ", "309876543", "305112233", "01.16.11.000", "Paxta xomashyosi 1-nav", 160000000, 19200000],
    ["2026-08-15", "SF-2026/1012", "Agro Ventures Farm MChJ", "O'zdonmahsulot AJ", "309876543", "302998877", "01.11.12.000", "Oziq-ovqat bug'doyi 3-sinf", 95000000, 11400000],
]

for r in rows:
    ws.append(r)

xlsx_path = os.path.join(fixtures_dir, "sample_soliq_efaktura.xlsx")
wb.save(xlsx_path)

print(f"Fixtures successfully generated at {fixtures_dir}")
