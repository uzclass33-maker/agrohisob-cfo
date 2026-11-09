"""
Integration tests for Smart Financial Data Import API endpoints in AgroHisob CFO.
"""

import os
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.import_engine.import_service import ImportService


client = TestClient(app)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture(autouse=True)
def reset_service_state():
    ImportService.reset()


def test_upload_bank_statement_csv():
    csv_file_path = os.path.join(FIXTURES_DIR, "sample_bank_statement.csv")
    assert os.path.exists(csv_file_path), "sample_bank_statement.csv fixture must exist"

    with open(csv_file_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/v1/imports/upload",
        files={"file": ("sample_bank_statement.csv", file_bytes, "text/csv")},
        data={"document_type": "BANK_STATEMENT", "organization_id": "org-test-api-01"}
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["document_type"] == "BANK_STATEMENT"
    assert data["total_rows"] == 7
    assert data["valid_rows"] >= 5
    assert len(data["detected_mappings"]) >= 3
    assert "Cash Ledger" in data["accounting_notice"]


def test_upload_soliq_efaktura_xlsx():
    xlsx_file_path = os.path.join(FIXTURES_DIR, "sample_soliq_efaktura.xlsx")
    assert os.path.exists(xlsx_file_path), "sample_soliq_efaktura.xlsx fixture must exist"

    with open(xlsx_file_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/v1/imports/upload",
        files={"file": ("sample_soliq_efaktura.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"document_type": "E_FAKTURA", "organization_id": "org-test-api-02"}
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["document_type"] == "E_FAKTURA"
    assert data["total_rows"] == 5
    assert "Invoice Obligation Ledger" in data["accounting_notice"]


def test_duplicate_file_upload_rejected():
    csv_file_path = os.path.join(FIXTURES_DIR, "sample_bank_statement.csv")
    with open(csv_file_path, "rb") as f:
        file_bytes = f.read()

    # 1. Upload first time
    res1 = client.post(
        "/api/v1/imports/upload",
        files={"file": ("sample_bank_statement.csv", file_bytes, "text/csv")},
        data={"document_type": "BANK_STATEMENT", "organization_id": "org-test-dup"}
    )
    assert res1.status_code == 201
    batch_id = res1.json()["batch_id"]

    # Commit batch to record hash in registry
    res_commit = client.post(f"/api/v1/imports/{batch_id}/commit", json={"batch_id": batch_id, "organization_id": "org-test-dup"})
    assert res_commit.status_code == 200

    # 2. Upload identical file again -> must return 409 Conflict
    res2 = client.post(
        "/api/v1/imports/upload",
        files={"file": ("sample_bank_statement.csv", file_bytes, "text/csv")},
        data={"document_type": "BANK_STATEMENT", "organization_id": "org-test-dup"}
    )
    assert res2.status_code == 409
    assert "avvalroq import qilingan" in res2.json()["detail"]


def test_row_override_and_batch_commit():
    csv_file_path = os.path.join(FIXTURES_DIR, "sample_bank_statement.csv")
    with open(csv_file_path, "rb") as f:
        file_bytes = f.read()

    # 1. Upload
    res_upload = client.post(
        "/api/v1/imports/upload",
        files={"file": ("sample_bank_statement.csv", file_bytes, "text/csv")},
        data={"document_type": "BANK_STATEMENT", "organization_id": "org-test-commit"}
    )
    assert res_upload.status_code == 201
    preview = res_upload.json()
    batch_id = preview["batch_id"]
    first_row = preview["rows"][0]
    row_id = first_row["row_id"]

    # 2. Override category on first row
    res_override = client.patch(
        f"/api/v1/imports/{batch_id}/rows/{row_id}",
        json={"row_id": row_id, "category": "MACHINERY_SERVICES"}
    )
    assert res_override.status_code == 200
    updated_row = res_override.json()
    assert updated_row["classification"]["category"] == "MACHINERY_SERVICES"
    assert updated_row["classification"]["rule_source"] == "MANUAL_USER_OVERRIDE"

    # 3. Commit batch
    res_commit = client.post(
        f"/api/v1/imports/{batch_id}/commit",
        json={"batch_id": batch_id, "organization_id": "org-test-commit"}
    )
    assert res_commit.status_code == 200
    commit_res = res_commit.json()
    assert commit_res["status"] == "COMMITTED"
    assert commit_res["target_ledger"] == "CASH_TRANSACTION_LEDGER"
    assert commit_res["committed_count"] >= 5
    assert commit_res["updated_cash_balance"] is not None

    # 4. Check history
    res_hist = client.get("/api/v1/imports/history/list?organization_id=org-test-commit")
    assert res_hist.status_code == 200
    hist_items = res_hist.json()
    assert len(hist_items) >= 1
    assert hist_items[0]["batch_id"] == batch_id
