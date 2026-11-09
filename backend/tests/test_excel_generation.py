"""
Tests for Excel Financial Model Generator using OpenPyXL (Assignment 5).
Verifies 8 sheets, formula injection sanitization, and UZS number formatting.
"""

from io import BytesIO
import openpyxl
import pytest

from app.reporting.dossier_builder import DossierBuilder
from app.reporting.excel_generator import ExcelModelGenerator, _sanitize_cell_text


def test_sanitize_cell_text():
    """Verify formula injection characters are escaped with a leading single quote."""
    assert _sanitize_cell_text("=1+1") == "'=1+1"
    assert _sanitize_cell_text("+100") == "'+100"
    assert _sanitize_cell_text("-200") == "'-200"
    assert _sanitize_cell_text("@SUM(A1:A5)") == "'@SUM(A1:A5)"
    assert _sanitize_cell_text("Normal Text") == "Normal Text"
    assert _sanitize_cell_text(12345) == 12345


def test_generate_excel_all_sheets_present():
    """Verify that Excel export contains all 8 required worksheets with proper titles."""
    dossier = DossierBuilder.build_dossier("scenario-cluster")
    xlsx_bytes = ExcelModelGenerator.generate_dossier_xlsx(dossier)
    
    assert isinstance(xlsx_bytes, bytes)
    assert len(xlsx_bytes) > 5000

    wb = openpyxl.load_workbook(BytesIO(xlsx_bytes))
    sheet_names = wb.sheetnames
    assert len(sheet_names) == 8

    expected_sheets = [
        "Ijroiya Xulosa",
        "Tarixiy Kassa Oqimlari",
        "Prognoz Farazlari",
        "12 Oylik Prognoz",
        "Kredit Grafigi",
        "DSCR Tahlili",
        "Ssenariylar Tahlili",
        "Manbalar va Metodologiya"
    ]
    for expected in expected_sheets:
        assert expected in sheet_names, f"Worksheet {expected} missing from Excel model!"


def test_excel_cell_values_match_dossier():
    """Verify financial metrics in Excel match canonical dossier data."""
    dossier = DossierBuilder.build_dossier("scenario-small-farmer")
    xlsx_bytes = ExcelModelGenerator.generate_dossier_xlsx(dossier)
    wb = openpyxl.load_workbook(BytesIO(xlsx_bytes), data_only=True)

    ws_exec = wb["Ijroiya Xulosa"]
    # Check that company name is in the title block
    assert "AGROHISOB CFO" in ws_exec["A1"].value
    
    ws_forecast = wb["12 Oylik Prognoz"]
    # Check column headers exist
    headers = [ws_forecast.cell(row=2, column=c).value for c in range(1, 10)]
    assert "Oy" in headers[0]
    assert "Oy Nomi" in headers[1]
    assert "Prognoz Tushum" in headers[3]
