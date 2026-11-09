from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.services.synthetic_data import SCENARIOS_MAP, SCENARIO_METAS, get_scenario_by_id
from app.services.financial_engine import FinancialEngine

router = APIRouter(prefix="/demo", tags=["Demo Organizations & Cash Flow"])

@router.get("/organizations")
def list_demo_organizations() -> List[Dict[str, Any]]:
    """Returns list of all available synthetic agribusiness demo organizations."""
    results = []
    for meta in SCENARIO_METAS:
        raw = SCENARIOS_MAP.get(meta.id, {})
        org = raw.get("organization", {})
        results.append({
            "id": meta.id,
            "key": meta.key,
            "name": meta.name,
            "category": meta.category,
            "category_label": meta.category_label,
            "region": meta.region,
            "district": meta.district,
            "land_hectares": meta.hectares,
            "soil_bonitet_score": org.get("soil_bonitet_score", 65),
            "main_crop": meta.main_crop,
            "has_drip_irrigation": org.get("has_drip_irrigation", False),
            "has_cold_storage": org.get("has_cold_storage", False),
            "initial_cash_uzs": meta.initial_cash_uzs,
            "annual_revenue_estimate_uzs": meta.annual_revenue_estimate_uzs,
            "debt_load_uzs": meta.debt_load_uzs,
            "description": meta.description,
            "key_dynamics": meta.key_dynamics,
            "is_synthetic": True,
            "is_demo": True,
            "currency": "UZS"
        })
    return results

@router.get("/organizations/{org_id}")
def get_demo_organization_details(org_id: str) -> Dict[str, Any]:
    """Returns full parameter set and metadata for a specific demo organization."""
    try:
        scenario = get_scenario_by_id(org_id)
        return {
            "organization": scenario["organization"],
            "initial_opening_balance": scenario["initial_opening_balance"],
            "debt_schedule": scenario.get("debt_schedule", []),
            "monthly_debt_service": scenario.get("monthly_debt_service", []),
            "currency": "UZS",
            "is_demo": True,
            "data_source_type": "SYNTHETIC_BENCHMARK"
        }
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Tashkilot topilmadi: '{org_id}'. Mavjud demo tashkilotlar: scenario-small-farmer, scenario-exporter, scenario-cluster"
        )

@router.get("/organizations/{org_id}/cashflow")
def get_demo_organization_cashflow(org_id: str) -> Dict[str, Any]:
    """
    Computes and returns the deterministic 12-month cash flow trajectory for the demo organization.
    Strictly guarantees:
    Closing Balance(t) = Opening Balance(t) + Inflows(t) - Outflows(t)
    Opening Balance(t+1) = Closing Balance(t)
    """
    try:
        scenario = get_scenario_by_id(org_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Tashkilot topilmadi: '{org_id}'"
        )

    summary = FinancialEngine.calculate_12m_cash_flow(
        initial_opening_balance=scenario["initial_opening_balance"],
        monthly_inflows_raw=scenario["monthly_inflows"],
        monthly_outflows_raw=scenario["monthly_outflows"],
        monthly_debt_service=scenario["monthly_debt_service"],
        org_id=scenario["organization"]["id"],
        org_name=scenario["organization"]["name"],
        fiscal_year=2024
    )

    return {
        "organization_id": summary.organization_id,
        "organization_name": summary.organization_name,
        "currency": "UZS",
        "reporting_period": "2024",
        "total_inflows": summary.total_annual_inflows,
        "total_outflows": summary.total_annual_outflows,
        "net_cash_flow": summary.net_annual_cash_flow,
        "opening_balance": summary.initial_opening_balance,
        "closing_balance": summary.final_closing_balance,
        "total_debt_service": summary.total_debt_service,
        "annual_dscr": summary.annual_dscr,
        "dscr_rating": summary.dscr_rating,
        "months_in_deficit": summary.months_in_deficit,
        "lowest_cash_point": summary.lowest_cash_point,
        "lowest_cash_month": summary.lowest_cash_month,
        "is_mathematically_reconciled": summary.is_mathematically_reconciled,
        "monthly_breakdown": [
            {
                "month_number": m.month_number,
                "month_name": m.month_name,
                "opening_balance": m.opening_balance,
                "total_inflows": m.total_inflows,
                "total_outflows": m.total_outflows,
                "net_cash_flow": m.net_cash_flow,
                "closing_balance": m.closing_balance,
                "debt_service": m.debt_service,
                "dscr": m.dscr,
                "is_deficit": m.is_deficit,
                "inflows_breakdown": m.inflows_breakdown,
                "outflows_breakdown": m.outflows_breakdown
            }
            for m in summary.monthly_data
        ],
        "calculation_version": "1.0.0",
        "data_source_type": "SYNTHETIC_BENCHMARK"
    }
