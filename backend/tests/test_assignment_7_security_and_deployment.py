import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import Settings
from app.db.database import normalize_database_url
from app.reporting.excel_generator import sanitize_excel_cell_value

client = TestClient(app)

def test_security_headers_middleware_applied():
    """Verify all corporate enterprise security headers and timing headers are attached to responses."""
    response = client.get("/health")
    assert response.status_code == 200
    headers = response.headers
    
    # Observability timing header
    assert "x-process-time" in headers
    assert headers["x-process-time"].endswith("s")
    
    # AppSec headers
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert headers.get("x-xss-protection") == "1; mode=block"
    assert headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert "geolocation=()" in headers.get("permissions-policy", "")

def test_postgresql_url_normalization():
    """Verify PostgreSQL connection strings are safely normalized to postgresql+psycopg2://."""
    # Standard Supabase postgresql://
    raw_supabase = "postgresql://postgres:secret@db.xyz.supabase.co:5432/postgres"
    normalized = normalize_database_url(raw_supabase)
    assert normalized == "postgresql+psycopg2://postgres:secret@db.xyz.supabase.co:5432/postgres"
    
    # Legacy postgres:// format (common on Render / Heroku)
    raw_render = "postgres://postgres:secret@dpg.render.com:5432/db"
    normalized_render = normalize_database_url(raw_render)
    assert normalized_render == "postgresql+psycopg2://postgres:secret@dpg.render.com:5432/db"
    
    # Already explicit driver
    raw_explicit = "postgresql+psycopg2://postgres:secret@localhost:5432/db"
    assert normalize_database_url(raw_explicit) == raw_explicit
    
    # Empty string returns fallback
    assert normalize_database_url("") == "sqlite:///./agrohisob_local.db"

def test_dynamic_cors_origins_parsing():
    """Verify comma-separated ALLOWED_ORIGINS string is properly parsed into a list."""
    custom_settings = Settings(
        CORS_ORIGINS_RAW="https://agrohisob.uz, https://preview.agrohisob-cfo.vercel.app, https://demo.bank.uz"
    )
    origins = custom_settings.CORS_ORIGINS
    assert len(origins) == 3
    assert "https://agrohisob.uz" in origins
    assert "https://preview.agrohisob-cfo.vercel.app" in origins
    assert "https://demo.bank.uz" in origins

def test_excel_formula_injection_defense():
    """Verify that dangerous Excel leading characters (=, +, -, @) are escaped with apostrophes."""
    dangerous_payloads = [
        "=SUM(A1:A10)",
        "+cmd|' /C calc'!A0",
        "-2+3*cmd|' /C notepad'!A0",
        "@SUM(1,2)"
    ]
    for payload in dangerous_payloads:
        sanitized = sanitize_excel_cell_value(payload)
        assert sanitized.startswith("'"), f"Failed to escape dangerous payload: {payload}"
    
    # Safe strings should not be modified
    assert sanitize_excel_cell_value("Agro-Export LLC") == "Agro-Export LLC"
    assert sanitize_excel_cell_value("Paxta yetishtirish xarajatlari") == "Paxta yetishtirish xarajatlari"
    assert sanitize_excel_cell_value(12500000) == 12500000

def test_production_security_validation_warning(caplog):
    """Verify production security validation warns on dev secrets in production environment."""
    prod_settings = Settings(
        ENVIRONMENT="production",
        DEBUG=True,
        SECRET_KEY="agrohisob-dev-secret-key-uzbekistan-2026-agrifintech"
    )
    with caplog.at_level("WARNING"):
        prod_settings.validate_production_security()
        assert any("SECURITY ALERT" in record.message for record in caplog.records)

def test_health_and_readiness_endpoints_for_monitoring():
    """Verify Kubernetes/Docker probes return 200 OK with expected JSON payloads."""
    health_res = client.get("/health")
    assert health_res.status_code == 200
    data = health_res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data
    
    ready_res = client.get("/ready")
    assert ready_res.status_code == 200
    ready_data = ready_res.json()
    assert ready_data["status"] == "ready"
    assert ready_data["database"] == "connected"
