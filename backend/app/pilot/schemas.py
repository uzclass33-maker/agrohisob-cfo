from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class PilotMetricItem(BaseModel):
    key: str
    name: str
    formula: str
    unit: str
    baseline: str
    target: str
    current_status: str
    verification_evidence: str

class PilotOrganization(BaseModel):
    id: str
    name: str
    segment: str
    is_synthetic: bool = True
    onboarding_status: str
    data_consent_signed: bool
    tasks_completed: int
    total_tasks: int

class PilotDashboardResponse(BaseModel):
    timestamp: str
    summary_notice: str
    actual_paying_customers: int = 0
    actual_active_pilots: int = 0
    planned_pilot_targets: int = 5
    verified_interviews_completed: int = 0
    planned_interviews: int = 19
    synthetic_demo_profiles_count: int = 3
    synthetic_demo_profiles: List[PilotOrganization]
    active_pilot_organizations: List[PilotOrganization]
    kpi_metrics: List[PilotMetricItem]
    data_security_status: str
    readiness_level: str
