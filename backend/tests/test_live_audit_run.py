"""
Automated live verification script for Assignment 3 audit.
Tests the live running FastAPI server and Next.js frontend.
"""

import os
import json
import urllib.request
import pytest
from app.import_engine.schemas import DocumentTypeEnum
from app.import_engine.import_service import ImportService


def test_live_fastapi_server_endpoints():
    # 1. Health
    with urllib.request.urlopen("http://127.0.0.1:8000/health") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data["status"] == "healthy"

    # 2. Readiness
    with urllib.request.urlopen("http://127.0.0.1:8000/ready") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data["status"] == "ready"

    # 3. Finance loans schedule
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/finance/loans/schedule",
        data=json.dumps({
            "principal": 50000000,
            "annual_interest_rate_pct": 18.0,
            "start_date": "2026-01-01",
            "term_months": 12,
            "repayment_type": "ANNUITY"
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode())
        assert "schedule" in res
        assert len(res["schedule"]) == 12

    # 4. Finance DSCR
    req_dscr = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/finance/dscr/calculate",
        data=json.dumps({
            "operating_cash_inflows": 150000000,
            "operating_cash_outflows": 80000000,
            "debt_service_principal": 35000000,
            "debt_service_interest": 15000000
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_dscr) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode())
        assert float(res["dscr"]) == 1.4
        assert res["status_tier"] == "MODERATE"


def test_live_nextjs_frontend_routes():
    routes = ["/", "/demo", "/dashboard", "/data-import", "/scenario-analysis", "/credit-report"]
    for r in routes:
        with urllib.request.urlopen(f"http://localhost:3000{r}") as resp:
            assert resp.status == 200
