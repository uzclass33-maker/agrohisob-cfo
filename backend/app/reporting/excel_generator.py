"""
AgroHisob CFO - Excel Financial Model Generator
Generates structured, professional multi-sheet Excel (.xlsx) financial models using OpenPyXL.
Includes 8 standardized worksheets, UZS formatting, frozen panes, and spreadsheet formula injection safeguards.
"""

from io import BytesIO
from typing import Any, List, Optional
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from app.reporting.report_schemas import CreditDossierData


def _sanitize_cell_text(val: Any) -> Any:
    """
    Prevents spreadsheet formula injection (CSV/Excel injection).
    If a string starts with formula operators '=', '+', '-', '@', prepends single quote.
    """
    if isinstance(val, str):
        if val.startswith(('=', '+', '-', '@')):
            return f"'{val}"
    return val

# Public export alias for testing and validation
sanitize_excel_cell_value = _sanitize_cell_text


class ExcelModelGenerator:
    """Enterprise financial model workbook exporter for AgroHisob CFO."""

    @classmethod
    def generate_dossier_xlsx(cls, dossier: CreditDossierData, output_path: str = None) -> bytes:
        wb = openpyxl.Workbook()
        # Remove default sheet
        wb.remove(wb.active)

        # Style Definitions
        font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        font_title = Font(name="Calibri", size=14, bold=True, color="0F172A")
        font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
        font_regular = Font(name="Calibri", size=10, color="1E293B")
        font_disclaimer = Font(name="Calibri", size=8, italic=True, color="64748B")

        fill_header_navy = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        fill_sub_header = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        fill_accent_green = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid")

        align_center = Alignment(horizontal="center", vertical="center")
        align_right = Alignment(horizontal="right", vertical="center")
        align_left = Alignment(horizontal="left", vertical="center")

        thin_border = Border(
            left=Side(style='thin', color='E2E8F0'),
            right=Side(style='thin', color='E2E8F0'),
            top=Side(style='thin', color='E2E8F0'),
            bottom=Side(style='thin', color='E2E8F0')
        )

        UZS_FORMAT = '#,##0 "so\'m"'
        PCT_FORMAT = '0.0"%"'
        NUM_FORMAT = '#,##0.00'

        def apply_table_header(ws, row_idx, headers):
            for col_idx, h in enumerate(headers, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=_sanitize_cell_text(h))
                cell.font = font_header
                cell.fill = fill_header_navy
                cell.alignment = align_center
                cell.border = thin_border

        def auto_fit_columns(ws):
            for col in ws.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    if cell.value:
                        val_str = str(cell.value)
                        max_len = max(max_len, len(val_str))
                ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        prof = dossier.credit_profile
        hist = dossier.historical_summary
        fc = dossier.forecast_summary
        db = dossier.debt_dscr_summary
        ra = dossier.readiness_assessment

        # =====================================================================
        # SHEET 1: EXECUTIVE SUMMARY
        # =====================================================================
        ws1 = wb.create_sheet(title="Ijroiya Xulosa")
        ws1.views.sheetView[0].showGridLines = True
        ws1.freeze_panes = "A5"

        ws1.cell(row=1, column=1, value="AGROHISOB CFO — KREDIT DOSYESI IJROIYA XULOSASI").font = font_title
        ws1.cell(row=2, column=1, value=f"Korxona: {dossier.organization_name} | Davr: {dossier.reporting_period}").font = font_bold
        ws1.cell(row=3, column=1, value=f"Dosye ID: {dossier.dossier_id} | Generatsiya: {dossier.generation_timestamp}").font = font_regular

        headers_s1 = ["Ko'rsatkich", "Qiymat (UZS)", "O'lchov Birligi", "Baho / Izoh"]
        apply_table_header(ws1, 5, headers_s1)

        s1_rows = [
            ("Kreditga Tayyorgarlik Reytingi", ra.readiness_score, "Ball (0-100)", ra.status_label_uz),
            ("Hujjatlar To'liqligi", ra.data_completeness_pct, "Foiz (%)", f"{dossier.checklist.available_count}/{dossier.checklist.total_items} ta hujjat"),
            ("So'ralayotgan Kredit Summasi", float(prof.requested_loan_amount_uzs), "UZS", f"{prof.proposed_term_months} oy, {prof.proposed_annual_interest_rate_pct}% stavka"),
            ("Tarixiy Yillik Tushum", hist["total_inflows"], "UZS", "So'nggi 12 oylik aylanma"),
            ("Prognoz Qilingan Yillik Tushum", fc["total_annual_inflows"], "UZS", "2026-yil hosil prognozi"),
            ("Prognoz Sof Kassa Oqimi", fc["net_annual_cash_flow"], "UZS", "Yillik sof pul ko'payishi"),
            ("Davr Yakuni Kassa Qoldig'i", fc["final_closing_balance"], "UZS", "Yil oxiri likvidlik zaxirasi"),
            ("Birlashtirilgan DSCR Koeffitsienti", db["combined_dscr"] or 0.0, "Koeffitsient (x)", "Bank talabi: >= 1.25x"),
            ("Kassa Uzilishi Oylari", fc["months_in_deficit"], "Oy", f"Eng past oy: {fc['lowest_cash_month']}")
        ]

        for r_idx, (name, val, unit, note) in enumerate(s1_rows, start=6):
            c1 = ws1.cell(row=r_idx, column=1, value=_sanitize_cell_text(name))
            c2 = ws1.cell(row=r_idx, column=2, value=val)
            c3 = ws1.cell(row=r_idx, column=3, value=_sanitize_cell_text(unit))
            c4 = ws1.cell(row=r_idx, column=4, value=_sanitize_cell_text(note))

            for c in (c1, c2, c3, c4):
                c.font = font_regular
                c.border = thin_border
            if isinstance(val, (int, float)) and "UZS" in unit:
                c2.number_format = UZS_FORMAT
                c2.alignment = align_right

        auto_fit_columns(ws1)

        # =====================================================================
        # SHEET 2: HISTORICAL CASH FLOW
        # =====================================================================
        ws2 = wb.create_sheet(title="Tarixiy Kassa Oqimlari")
        ws2.views.sheetView[0].showGridLines = True
        ws2.freeze_panes = "A3"

        ws2.cell(row=1, column=1, value="TARIXIY OYLIK KASSA OQIMLARI TAFSILOTI").font = font_title
        headers_s2 = ["Oy Raqami", "Oy Nomi", "Boshlang'ich Balans", "Yalpi Tushumlar", "Jami Chiqimlar", "Sof Pul Oqimi", "Yakuniy Balans", "Kassa Taqchilligi"]
        apply_table_header(ws2, 2, headers_s2)

        for r_idx, m in enumerate(hist["monthly_data"], start=3):
            ws2.cell(row=r_idx, column=1, value=m["month_number"]).alignment = align_center
            ws2.cell(row=r_idx, column=2, value=_sanitize_cell_text(m["month_name"]))
            
            c_op = ws2.cell(row=r_idx, column=3, value=m["opening_balance"])
            c_in = ws2.cell(row=r_idx, column=4, value=m["inflows"])
            c_out = ws2.cell(row=r_idx, column=5, value=m["outflows"])
            c_net = ws2.cell(row=r_idx, column=6, value=m["net_cash_flow"])
            c_cl = ws2.cell(row=r_idx, column=7, value=m["closing_balance"])
            c_def = ws2.cell(row=r_idx, column=8, value="HA" if m["is_deficit"] else "YO'Q")

            for col in range(1, 9):
                cell = ws2.cell(row=r_idx, column=col)
                cell.font = font_regular
                cell.border = thin_border
                if col in (3, 4, 5, 6, 7):
                    cell.number_format = UZS_FORMAT
                    cell.alignment = align_right
            c_def.alignment = align_center

        auto_fit_columns(ws2)

        # =====================================================================
        # SHEET 3: FORECAST ASSUMPTIONS
        # =====================================================================
        ws3 = wb.create_sheet(title="Prognoz Farazlari")
        ws3.views.sheetView[0].showGridLines = True
        ws3.freeze_panes = "A3"

        ws3.cell(row=1, column=1, value="AGRAR PROGNOZ ASOSLARI VA FARAZLAR").font = font_title
        headers_s3 = ["Parametr Nomi", "Faraz Qiymati", "O'lchov Birligi", "Asos / Ma'lumot Manbasi"]
        apply_table_header(ws3, 2, headers_s3)

        s3_rows = [
            ("Asosiy Ekin Maydoni", prof.land_hectares, "Gektar", "Kadastr va ijara shartnomasi"),
            ("Asosiy Ekin Turlari", ", ".join(prof.main_crop_types), "Ro'yxat", "Ekish xaritasi"),
            ("Hosil Terimi Oylari", ", ".join(str(m) for m in prof.harvest_months), "Oylar", "Agrar kalendar"),
            ("Mahsulot Realizatsiya Oylari", ", ".join(str(m) for m in prof.sales_months), "Oylar", "Kontraktatsiya shartnomalari"),
            ("Xarajatlar Inflyatsiya Indeksi", 8.5, "Foiz (%)", "Markaziy bank va iqtisodiy tahlil"),
            ("Tushum Kechikishi", 20, "Kun", "Xaridorlar to'lov shartlari"),
            ("Boshlang'ich Kassa Zaxirasi", fc["initial_cash_balance"], "UZS", "Bank hisobvarag'i ko'chirmasi")
        ]

        for r_idx, (p_name, val, p_unit, p_src) in enumerate(s3_rows, start=3):
            ws3.cell(row=r_idx, column=1, value=_sanitize_cell_text(p_name))
            ws3.cell(row=r_idx, column=2, value=_sanitize_cell_text(val) if isinstance(val, str) else val)
            ws3.cell(row=r_idx, column=3, value=_sanitize_cell_text(p_unit))
            ws3.cell(row=r_idx, column=4, value=_sanitize_cell_text(p_src))
            for c in range(1, 5):
                cell = ws3.cell(row=r_idx, column=c)
                cell.font = font_regular
                cell.border = thin_border

        auto_fit_columns(ws3)

        # =====================================================================
        # SHEET 4: TWELVE-MONTH FORECAST
        # =====================================================================
        ws4 = wb.create_sheet(title="12 Oylik Prognoz")
        ws4.views.sheetView[0].showGridLines = True
        ws4.freeze_panes = "A3"

        ws4.cell(row=1, column=1, value="2026-YIL PROGNOZ QILINGAN KASSA OQIMLARI").font = font_title
        headers_s4 = ["Oy", "Oy Nomi", "Boshlang'ich", "Prognoz Tushum", "Opex Chiqim", "Qarz Xizmati", "Jami Chiqim", "Sof Oqim", "Yakuniy Balans", "CFADS", "Oylik DSCR"]
        apply_table_header(ws4, 2, headers_s4)

        for r_idx, m in enumerate(fc["monthly_forecast"], start=3):
            ws4.cell(row=r_idx, column=1, value=m["month_number"]).alignment = align_center
            ws4.cell(row=r_idx, column=2, value=_sanitize_cell_text(m["month_name"]))
            ws4.cell(row=r_idx, column=3, value=m["opening_balance"]).number_format = UZS_FORMAT
            ws4.cell(row=r_idx, column=4, value=m["inflows"]).number_format = UZS_FORMAT
            ws4.cell(row=r_idx, column=5, value=m["operating_outflows"]).number_format = UZS_FORMAT
            ws4.cell(row=r_idx, column=6, value=m["debt_service"]).number_format = UZS_FORMAT
            ws4.cell(row=r_idx, column=7, value=m["total_outflows"]).number_format = UZS_FORMAT
            ws4.cell(row=r_idx, column=8, value=m["net_cash_flow"]).number_format = UZS_FORMAT
            ws4.cell(row=r_idx, column=9, value=m["closing_balance"]).number_format = UZS_FORMAT
            ws4.cell(row=r_idx, column=10, value=m["cfads"]).number_format = UZS_FORMAT
            ws4.cell(row=r_idx, column=11, value=m["monthly_dscr"] or 0.0).number_format = NUM_FORMAT

            for c in range(1, 12):
                cell = ws4.cell(row=r_idx, column=c)
                cell.font = font_regular
                cell.border = thin_border
                if c >= 3 and c <= 10:
                    cell.alignment = align_right

        auto_fit_columns(ws4)

        # =====================================================================
        # SHEET 5: LOAN SCHEDULE
        # =====================================================================
        ws5 = wb.create_sheet(title="Kredit Grafigi")
        ws5.views.sheetView[0].showGridLines = True
        ws5.freeze_panes = "A3"

        ws5.cell(row=1, column=1, value=f"SO'RALAYOTGAN KREDIT AMORTIZATSIYA GRAFIGI ({prof.requested_loan_amount_uzs:,.0f} UZS)").font = font_title
        headers_s5 = ["Davr", "To'lov Sanasi", "Boshlang'ich Asosiy Qarz", "Asosiy Qarz To'lovi", "Foiz To'lovi", "Jami Oylik To'lov", "Qoldiq Asosiy Qarz"]
        apply_table_header(ws5, 2, headers_s5)

        for r_idx, row in enumerate(db["amortization_schedule"], start=3):
            ws5.cell(row=r_idx, column=1, value=row["period"]).alignment = align_center
            ws5.cell(row=r_idx, column=2, value=_sanitize_cell_text(row["date"])).alignment = align_center
            ws5.cell(row=r_idx, column=3, value=row["opening_principal"]).number_format = UZS_FORMAT
            ws5.cell(row=r_idx, column=4, value=row["principal_paid"]).number_format = UZS_FORMAT
            ws5.cell(row=r_idx, column=5, value=row["interest_paid"]).number_format = UZS_FORMAT
            ws5.cell(row=r_idx, column=6, value=row["total_payment"]).number_format = UZS_FORMAT
            ws5.cell(row=r_idx, column=7, value=row["remaining_principal"]).number_format = UZS_FORMAT

            for c in range(1, 8):
                cell = ws5.cell(row=r_idx, column=c)
                cell.font = font_regular
                cell.border = thin_border
                if c >= 3:
                    cell.alignment = align_right

        auto_fit_columns(ws5)

        # =====================================================================
        # SHEET 6: DSCR ANALYSIS
        # =====================================================================
        ws6 = wb.create_sheet(title="DSCR Tahlili")
        ws6.views.sheetView[0].showGridLines = True
        ws6.freeze_panes = "A3"

        ws6.cell(row=1, column=1, value="QARZGA XIZMAT KO'RSATISH VA DSCR QOPLASH TAHLILI").font = font_title
        headers_s6 = ["Parametr", "Qiymat", "O'lchov Birligi", "Metodologiya Izohi"]
        apply_table_header(ws6, 2, headers_s6)

        s6_rows = [
            ("So'ralayotgan Kredit Asosiy Qarz", float(prof.requested_loan_amount_uzs), "UZS", "Yangi investitsiya"),
            ("Jami Foiz Xarajati", db["total_interest_cost"], "UZS", f"To'liq muddat ({prof.proposed_term_months} oy) bo'yicha"),
            ("Yangi Kredit 1-Yil Xizmati", db["first_year_new_loan_service"], "UZS", "Dastlabki 12 oylik to'lovlar"),
            ("Mavjud Yillik Qarz Xizmati", db["existing_annual_debt_service"], "UZS", "Agrobank va amaldagi shartnomalar"),
            ("Jami Yillik Qarz Xizmati", db["combined_annual_debt_service"], "UZS", "Mavjud + Yangi kredit"),
            ("Mavjud DSCR (Yangi kreditsiz)", db["standalone_dscr"] or 0.0, "Koeffitsient (x)", "Hozirgi to'lov qobiliyati"),
            ("Birlashtirilgan DSCR (Yangi kredit bilan)", db["combined_dscr"] or 0.0, "Koeffitsient (x)", "Kredit ajratilgandan keyin")
        ]

        for r_idx, (param, val, unit, desc) in enumerate(s6_rows, start=3):
            ws6.cell(row=r_idx, column=1, value=_sanitize_cell_text(param))
            c_val = ws6.cell(row=r_idx, column=2, value=val)
            ws6.cell(row=r_idx, column=3, value=_sanitize_cell_text(unit))
            ws6.cell(row=r_idx, column=4, value=_sanitize_cell_text(desc))
            for c in range(1, 5):
                cell = ws6.cell(row=r_idx, column=c)
                cell.font = font_regular
                cell.border = thin_border
            if "UZS" in unit:
                c_val.number_format = UZS_FORMAT
                c_val.alignment = align_right
            else:
                c_val.number_format = NUM_FORMAT
                c_val.alignment = align_right

        auto_fit_columns(ws6)

        # =====================================================================
        # SHEET 7: SCENARIOS
        # =====================================================================
        ws7 = wb.create_sheet(title="Ssenariylar Tahlili")
        ws7.views.sheetView[0].showGridLines = True
        ws7.freeze_panes = "A3"

        ws7.cell(row=1, column=1, value="SSENARIYLAR VA SEZGIRLIK SIMULYATSIYASI").font = font_title
        headers_s7 = ["Ssenariy Nomi", "Yillik Tushum", "Yillik Chiqim", "Yakuniy Kassa", "DSCR (x)", "Kassa Taqchilligi Oylari", "Farq (Kassa Qoldig'i)"]
        apply_table_header(ws7, 2, headers_s7)

        sc = dossier.risks_scenarios_summary
        sc_rows = [
            ("Baza Ssenariysi (0%)", sc["base"]["inflows"], sc["base"]["outflows"], sc["base"]["closing_balance"], sc["base"]["dscr"] or 0.0, sc["base"]["deficits"], 0.0),
            ("Optimistik Ssenariy (+20%/-10%)", sc["optimistic"]["inflows"], sc["optimistic"]["outflows"], sc["optimistic"]["closing_balance"], sc["optimistic"]["dscr"] or 0.0, sc["optimistic"]["deficits"], sc["optimistic"].get("variance_closing", 0.0)),
            ("Pessimistik Ssenariy (-20%/+15%)", sc["pessimistic"]["inflows"], sc["pessimistic"]["outflows"], sc["pessimistic"]["closing_balance"], sc["pessimistic"]["dscr"] or 0.0, sc["pessimistic"]["deficits"], sc["pessimistic"].get("variance_closing", 0.0))
        ]

        for r_idx, (s_name, s_in, s_out, s_cl, s_dscr, s_def, s_var) in enumerate(sc_rows, start=3):
            ws7.cell(row=r_idx, column=1, value=_sanitize_cell_text(s_name))
            ws7.cell(row=r_idx, column=2, value=s_in).number_format = UZS_FORMAT
            ws7.cell(row=r_idx, column=3, value=s_out).number_format = UZS_FORMAT
            ws7.cell(row=r_idx, column=4, value=s_cl).number_format = UZS_FORMAT
            ws7.cell(row=r_idx, column=5, value=s_dscr).number_format = NUM_FORMAT
            ws7.cell(row=r_idx, column=6, value=f"{s_def} oy").alignment = align_center
            ws7.cell(row=r_idx, column=7, value=s_var).number_format = UZS_FORMAT

            for c in range(1, 8):
                cell = ws7.cell(row=r_idx, column=c)
                cell.font = font_regular
                cell.border = thin_border
                if c in (2, 3, 4, 5, 7):
                    cell.alignment = align_right

        auto_fit_columns(ws7)

        # =====================================================================
        # SHEET 8: DATA SOURCES & METHODOLOGY
        # =====================================================================
        ws8 = wb.create_sheet(title="Manbalar va Metodologiya")
        ws8.views.sheetView[0].showGridLines = True
        ws8.freeze_panes = "A3"

        ws8.cell(row=1, column=1, value="MOLIYAVIY MODEL METODOLOGIYASI VA HUQUQIY CHEKLOVLAR").font = font_title
        headers_s8 = ["Bo'lim", "Tavsif / Standart", "Qoidalar va Cheklovlar"]
        apply_table_header(ws8, 2, headers_s8)

        meta = dossier.data_sources_and_assumptions
        s8_rows = [
            ("Dvigatel Versiyasi", f"AgroHisob Financial Engine v{meta.get('calculation_engine_version', '5.0.0')}", "100% deterministik arifmetika"),
            ("Kassa Hisobi Standarti", meta.get("cash_flow_standard", ""), "Boshlang'ich + Tushum - Chiqim = Yakuniy"),
            ("DSCR Metodologiyasi", meta.get("dscr_methodology", ""), "Operatsion kassa oqimining qarzga xizmat ko'rsatishga nisbati"),
            ("Valyuta", meta.get("currency", "UZS"), "O'zbekiston so'mi"),
            ("Huquqiy Ogohlantirish", dossier.regulatory_disclaimer_uz, "Tijorat banki rasmiy qarori emas, tahliliy dosye")
        ]

        for r_idx, (col1, col2, col3) in enumerate(s8_rows, start=3):
            ws8.cell(row=r_idx, column=1, value=_sanitize_cell_text(col1))
            ws8.cell(row=r_idx, column=2, value=_sanitize_cell_text(col2))
            ws8.cell(row=r_idx, column=3, value=_sanitize_cell_text(col3))
            for c in range(1, 4):
                cell = ws8.cell(row=r_idx, column=c)
                cell.font = font_regular
                cell.border = thin_border

        auto_fit_columns(ws8)

        # Save workbook to BytesIO
        stream = BytesIO()
        wb.save(stream)
        xlsx_bytes = stream.getvalue()

        if output_path:
            with open(output_path, "wb") as f:
                f.write(xlsx_bytes)

        return xlsx_bytes
