"""
AgroHisob CFO - Unit Tests for Regulatory Sources Registry (Assignment 6)
"""

from fastapi.testclient import TestClient
from app.main import app
from app.regulatory.legal_sources import (
    REGULATORY_SOURCES,
    get_regulatory_source,
    list_regulatory_sources,
)

client = TestClient(app)


def test_regulatory_sources_registry_completeness():
    sources = list_regulatory_sources()
    assert len(sources) >= 3

    codes = [s.document_code for s in sources]
    assert "VMQ-613" in codes
    assert "PQ-47" in codes
    assert "PF-82" in codes


def test_regulatory_source_lookup():
    vmq = get_regulatory_source("VMQ-613")
    assert vmq is not None
    assert "lex.uz" in vmq.official_lex_url
    assert vmq.verification_status.value == "VERIFIED_ACTIVE"
    assert "clause_8" in vmq.key_clauses_summary_uz

    pq47 = get_regulatory_source("PQ-47")
    assert pq47 is not None
    assert "8036872" in pq47.official_lex_url

    pf82 = get_regulatory_source("PF-82")
    assert pf82 is not None
    assert "8187068" in pf82.official_lex_url


def test_regulatory_api_endpoints():
    res = client.get("/api/v1/regulatory/sources")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    res_single = client.get("/api/v1/regulatory/sources/VMQ-613")
    assert res_single.status_code == 200
    assert res_single.json()["document_code"] == "VMQ-613"

    res_404 = client.get("/api/v1/regulatory/sources/NON_EXISTENT")
    assert res_404.status_code == 404
