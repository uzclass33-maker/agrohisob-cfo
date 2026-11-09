"""
AgroHisob CFO - Agricultural Land Lease Collateral API Router (Assignment 6, Module A)
Endpoints for VMQ-613 legal screening, indicative DCF valuation, sensitivity analysis,
and collateral preparation document checklist.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.collateral.document_checklist import build_collateral_checklist
from app.collateral.eligibility import screen_land_lease_collateral
from app.collateral.schemas import (
    CollateralDocumentChecklist,
    CollateralPreparationSummary,
    CollateralSensitivityAnalysis,
    IndicativeValuationRequest,
    IndicativeValuationResult,
    LandLeaseProfile,
    VMQ613ScreeningResult,
)
from app.collateral.sensitivity import run_collateral_sensitivity_analysis
from app.collateral.service import CollateralService, get_default_land_lease_profile
from app.collateral.valuation import calculate_indicative_lease_valuation

router = APIRouter(prefix="/collateral", tags=["Agricultural Collateral Intelligence (VMQ-613)"])


@router.get("/profile/default", response_model=LandLeaseProfile)
def get_default_profile(
    organization_id: str = Query(default="scenario-small-farmer", description="Organization ID or scenario key")
):
    """
    Muayyan tashkilot yoki ssenariy uchun yer ijara huquqi standart profilini olish.
    """
    try:
        return get_default_land_lease_profile(organization_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profilni yuklashda xatolik: {str(e)}")


@router.post("/eligibility", response_model=VMQ613ScreeningResult)
def evaluate_vmq613_eligibility(profile: LandLeaseProfile):
    """
    VMQ-613 talablari (5 yillik bufer, davlat ro'yxati, taqiqlar, ikkilamchi ijara)
    bo'yicha qat'iy kalendar asosida huquqiy screening o'tkazish.
    """
    try:
        return screen_land_lease_collateral(profile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Huquqiy tahlilda xatolik: {str(e)}")


@router.post("/valuation/illustrative", response_model=IndicativeValuationResult)
def calculate_illustrative_valuation(request: IndicativeValuationRequest):
    """
    Cheklangan ijara muddati va bonitet bali asosida indikativ DCF baholash (terminal qiymatsiz).
    """
    try:
        return calculate_indicative_lease_valuation(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Indikativ baholashda xatolik: {str(e)}")


@router.post("/scenarios", response_model=CollateralSensitivityAnalysis)
def calculate_sensitivity_scenarios(request: IndicativeValuationRequest):
    """
    Ko'p ssenariyli sezgirlik tahlili (Bazaviy, Optimistik, Pessimistik) - haqiqiy qayta hisob.
    """
    try:
        return run_collateral_sensitivity_analysis(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Sezgirlik tahlilida xatolik: {str(e)}")


@router.post("/checklist", response_model=CollateralDocumentChecklist)
def get_checklist(profile: LandLeaseProfile):
    """
    VMQ-613 va bank talablari bo'yicha 9 ta me'yoriy hujjatdan iborat tayyorgarlik cheklisti.
    """
    try:
        return build_collateral_checklist(profile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cheklist tuzishda xatolik: {str(e)}")


@router.post("/summary", response_model=CollateralPreparationSummary)
def get_full_collateral_summary(profile: LandLeaseProfile):
    """
    Yer ijara huquqi garovi bo'yicha to'liq tayyorgarlik xulosasi:
    screening, DCF baholash, sezgirlik tahlili, hujjatlar ro'yxati va yuridik ogohlantirish.
    """
    try:
        return CollateralService.evaluate_collateral(profile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Garov xulosasini tayyorlashda xatolik: {str(e)}")
