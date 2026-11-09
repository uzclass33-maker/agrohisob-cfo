from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class AnalyticsEventType(str, Enum):
    DEMO_STARTED = "demo_started"
    IMPORT_STARTED = "import_started"
    IMPORT_COMPLETED = "import_completed"
    IMPORT_FAILED = "import_failed"
    DASHBOARD_VIEWED = "dashboard_viewed"
    FORECAST_GENERATED = "forecast_generated"
    SCENARIO_CALCULATED = "scenario_calculated"
    REPORT_GENERATED = "report_generated"
    REPORT_DOWNLOADED = "report_downloaded"
    FEEDBACK_SUBMITTED = "feedback_submitted"

class AnalyticsEventCreate(BaseModel):
    event_type: AnalyticsEventType
    session_id: str = Field(..., description="Safe anonymous session identifier")
    organization_id: Optional[str] = Field(default="org-default", description="Anonymized organization context")
    duration_ms: Optional[int] = Field(default=None, description="Action duration in milliseconds")
    status: str = Field(default="SUCCESS", description="SUCCESS, FAILED, CANCELLED")
    error_category: Optional[str] = Field(default=None, description="Categorical error type, no sensitive payload")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Safe metadata (e.g. scenario_type, file_extension)")

class AnalyticsEvent(AnalyticsEventCreate):
    id: str
    timestamp: str

class AnalyticsSummary(BaseModel):
    total_events: int
    event_counts: Dict[str, int]
    avg_durations_ms: Dict[str, float]
    error_rates: Dict[str, float]
    unique_sessions: int
