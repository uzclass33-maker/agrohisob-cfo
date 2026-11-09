"""
Automated live verification script for Assignment 3 audit.
Tests the running FastAPI server (or TestClient if daemon is offline) and Next.js frontend.
"""

import os
import json
import urllib.request
import pytest
from fastapi.testclient import TestClient
from app.main import app

test_client = TestClient(app)

def _is_live_server_running(url: str = "http://127.0.0.1:8000/health") -> bool:
    try:
        with urllib.request.urlopen(url, timeout=0.5) as resp:
            return resp.status == 200
    except Exception:
        return False

def test_live_fastapi_server_endpoints():
    if _is_live_server_running():
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
    else:
        # Fallback to TestClient in CI / offline environments
        r1 = test_client.get("/health")
        assert r1.status_code == 200
        assert r1.json()["status"] == "healthy"

        r2 = test_client.get("/ready")
        assert r2.status_code == 200
        assert r2.json()["status"] == "ready"


def test_live_nextjs_frontend_routes():
    if not _is_live_server_running("http://localhost:3000"):
        pytest.skip("Next.js live server is not running on port 3000 (CI environment)")

    routes = ["/", "/demo", "/dashboard", "/data-import", "/scenario-analysis", "/credit-report", "/collateral-subsidies"]
    for r in routes:
        with urllib.request.urlopen(f"http://localhost:3000{r}") as resp:
            assert resp.status == 200
