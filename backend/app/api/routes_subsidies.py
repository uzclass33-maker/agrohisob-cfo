"""
AgroHisob CFO - Agricultural Subsidy Intelligence API Router (Assignment 6, Module B)
Endpoints for subsidy program discovery, PQ-47 water-saving calculator,
PF-82 cotton & wheat interest compensation, and financial impact synthesis.
"""

from typing import List
from fastapi import APIRouter, HTTPException

from app.subsidies.schemas import (
    PF82CalculationRequest,
    PF82CalculationResult,
    PQ47CalculationRequest,
    PQ47CalculationResult,
    SubsidyFinancialImpactResponse,
    SubsidyMatchItem,
    SubsidyMatchRequest,
    SubsidyProgram,
)
from app.subsidies.service import SubsidyService

router = APIRouter(prefix="/subsidies", tags=["Agricultural Subsidy Intelligence (PQ-47 & PF-82)"])


@router.get("/programs", response_model=List[SubsidyProgram])
def list_programs():
    """
    PQ-47 va PF-82 bo'yicha tasdiqlangan qishloq xo'jaligi davlat subsidiyalari dasturlari reestri.
    """
    return SubsidyService.get_all_programs()


@router.get("/programs/{program_code}", response_model=SubsidyProgram)
def get_program_by_code(program_code: str):
    """
    Dastur kodi bo'yicha aniq subsidiya dasturi ma'lumotlarini olish.
    """
    prog = SubsidyService.get_program(program_code)
    if not prog:
        raise HTTPException(
            status_code=404,
            detail=f"Subsidiya dasturi topilmadi: {program_code}",
        )
    return prog


@router.post("/match", response_model=List[SubsidyMatchItem])
def match_programs(request: SubsidyMatchRequest):
    """
    Fermer xo'jaligi parametrlari (hudud, ekinlar, sug'orish tizimi) asosida
    barcha subsidiya dasturlari bo'yicha 5 ta deterministik holatda moslik tahlili.
    """
    try:
        return SubsidyService.match(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Moslik tahlilida xatolik: {str(e)}")


@router.post("/calculate/pq47", response_model=PQ47CalculationResult)
def calculate_pq47(request: PQ47CalculationRequest):
    """
    PQ-47 Qarori bo'yicha suv tejovchi (tomchilatib) sug'orish subsidiyasini
    ekin stavkalari, hududiy koeffitsiyent (1.2x) va 50/50 bosqichma-bosqich to'lov asosida hisoblash.
    """
    try:
        return SubsidyService.calculate_pq47(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PQ-47 hisob-kitobida xatolik: {str(e)}")


@router.post("/calculate/pf82", response_model=PF82CalculationResult)
def calculate_pf82(request: PF82CalculationRequest):
    """
    PF-82 Farmoni bo'yicha paxta va g'alla kreditlari uchun 10 foiz bandi kompensatsiyasini
    haqiqiy qoldiq va intizomli so'ndirilgan kunlar bo'yicha hisoblash.
    """
    try:
        return SubsidyService.calculate_pf82(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PF-82 hisob-kitobida xatolik: {str(e)}")


@router.post("/financial-impact", response_model=SubsidyFinancialImpactResponse)
def calculate_financial_impact(request: SubsidyMatchRequest):
    """
    Fermer xo'jaligi uchun subsidiyalarning kassa oqimi va DSCR ko'rsatkichiga
    indikativ moliyaviy ta'sirini baholash (tarixiy kassa bilan aralashtirmagan holda).
    """
    try:
        return SubsidyService.calculate_financial_impact(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Moliyaviy ta'sir tahlilida xatolik: {str(e)}")
