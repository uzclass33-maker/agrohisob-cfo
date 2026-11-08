from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import SyntheticScenarioMeta
from app.services.synthetic_data import SCENARIO_METAS, get_scenario_by_id

router = APIRouter(prefix="/scenarios", tags=["Synthetic Scenarios"])

@router.get("", response_model=List[SyntheticScenarioMeta])
def list_synthetic_scenarios():
    """Returns list of all available synthetic agribusiness scenarios."""
    return SCENARIO_METAS

@router.get("/{scenario_id}")
def get_scenario_details(scenario_id: str):
    """Returns detailed financial parameters and debt schedules for a specific synthetic business."""
    try:
        scenario = get_scenario_by_id(scenario_id)
        return scenario
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Ssenariy topilmadi: '{scenario_id}'. Mavjud ssenariylar: scenario-small-farmer, scenario-exporter, scenario-cluster"
        )
