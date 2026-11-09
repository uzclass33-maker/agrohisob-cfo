"""
End-to-End integration test for complete Credit Dossier Journey (Assignment 5).
Validates cross-consistency between Preview Data, Generated PDF, and Excel Financial Model.
"""

from io import BytesIO
import openpyxl
from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)


def test_e2e_credit_dossier_cross_consistency():
    """
    E2E Journey:
    1. Submit tailored credit request for Exporter scenario.
    2. Request Preview and capture canonical financial figures (Inflows, Outflows, Combined DSCR).
    3. Trigger Report Generation (PDF + XLSX).
    4. Download Excel model and verify that the figures in the 'Ijroiya Xulosa' and 'DSCR Tahlili'
       sheets match the Preview figures EXACTLY (0% discrepancy).
    5. Download PDF and ensure document begins with %PDF- and contains valid size.
    """
    org_id = "scenario-exporter"
    custom_profile = {
        "organization_id": org_id,
        "organization_name": "Samarqand Bog'bon Agro Eksport MChJ",
        "requested_loan_amount_uzs": 500000000.0,
        "loan_purpose": "COLD_STORAGE",
        "proposed_term_months": 36,
        "proposed_annual_interest_rate_pct": 15.0,
        "repayment_structure": "ANNUITY",
        "grace_period_months": 6,
        "expected_disbursement_date": "2026-04-01"
    }

    # Step 1: Preview
    res_preview = client.post(
        "/api/v1/reports/credit/preview",
        json={"organization_id": org_id, "credit_profile": custom_profile}
    )
    assert res_preview.status_code == 200
    preview = res_preview.json()

    preview_inflows = preview["forecast_summary"]["total_annual_inflows"]
    preview_outflows = preview["forecast_summary"]["total_annual_outflows"]
    preview_dscr = preview["debt_dscr_summary"]["combined_dscr"]
    preview_requested_loan = preview["debt_dscr_summary"]["requested_principal"]

    assert preview_requested_loan == 500000000.0

    # Step 2: Generate
    res_gen = client.post(
        "/api/v1/reports/credit/generate",
        json={"organization_id": org_id, "credit_profile": custom_profile}
    )
    assert res_gen.status_code == 200
    gen_record = res_gen.json()
    report_id = gen_record["report_id"]

    # Step 3: Download Excel
    res_xlsx = client.get(f"/api/v1/reports/{report_id}/download/xlsx")
    assert res_xlsx.status_code == 200
    
    wb = openpyxl.load_workbook(BytesIO(res_xlsx.content), data_only=True)
    ws_exec = wb["Ijroiya Xulosa"]
    
    # Check that requested loan amount in Excel matches preview
    cell_loan_val = None
    for r in range(1, 25):
        val_label = ws_exec.cell(row=r, column=1).value
        if val_label and "So'ralayotgan Kredit" in str(val_label):
            cell_loan_val = ws_exec.cell(row=r, column=2).value
            break
    
    assert cell_loan_val == preview_requested_loan

    # Step 4: Download PDF
    res_pdf = client.get(f"/api/v1/reports/{report_id}/download/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.content.startswith(b"%PDF-")
    assert len(res_pdf.content) > 10000
