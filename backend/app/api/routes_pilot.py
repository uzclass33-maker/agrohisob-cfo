from fastapi import APIRouter
from app.pilot.schemas import PilotDashboardResponse
from app.pilot.service import PilotService

router = APIRouter(prefix="/pilot", tags=["Pilot Validation Dashboard"])

@router.get("/dashboard", response_model=PilotDashboardResponse)
def get_pilot_dashboard():
    """
    Returns the real-time pilot validation status, KPI tracking metrics,
    and strictly separates synthetic demo profiles from real pilot customers.
    """
    return PilotService.get_dashboard_summary()
