"""
AgroHisob CFO - Regulatory Knowledge Base API Router (Assignment 6)
Exposes official Uzbekistan legal sources (VMQ-613, PQ-47, PF-82) with Lex.uz citations.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.regulatory.legal_sources import (
    RegulatorySourceRecord,
    get_regulatory_source,
    list_regulatory_sources,
)

router = APIRouter(prefix="/regulatory", tags=["Regulatory & Legal Sources"])


@router.get("/sources", response_model=List[RegulatorySourceRecord])
def get_all_sources(verified_only: bool = Query(default=True)):
    """
    O'zbekiston Respublikasi me'yoriy-huquqiy hujjatlari (VMQ-613, PQ-47, PF-82)
    va Lex.uz rasmiy manbalari reestri.
    """
    sources = list_regulatory_sources()
    if verified_only:
        sources = [s for s in sources if "VERIFIED" in str(s.verification_status)]
    return sources


@router.get("/sources/{source_code}", response_model=RegulatorySourceRecord)
def get_source_by_code(source_code: str):
    """
    Muayyan me'yoriy hujjat ma'lumotlarini qidirish (masalan, VMQ-613, PQ-47, PF-82).
    """
    source = get_regulatory_source(source_code)
    if not source:
        raise HTTPException(
            status_code=404,
            detail=f"Me'yoriy hujjat topilmadi: {source_code}",
        )
    return source
