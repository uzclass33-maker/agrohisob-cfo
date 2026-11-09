from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from app.auth.dependencies import require_admin
from app.auth.models import AuthenticatedUser
from app.analytics.schemas import (
    AnalyticsEvent, AnalyticsEventCreate,
    AnalyticsSummary
)
from app.analytics.tracker import ProductAnalytics

router = APIRouter(prefix="/analytics", tags=["Product Analytics"])

@router.post("/events", response_model=AnalyticsEvent, status_code=status.HTTP_201_CREATED)
def track_event(event: AnalyticsEventCreate):
    """
    Ingests a privacy-safe product analytics event.
    Automatically scrubs financial amounts, tax IDs, and sensitive tokens.
    """
    return ProductAnalytics.record_event(event)

@router.get("/events", response_model=List[AnalyticsEvent])
def list_events(
    limit: int = Query(50, ge=1, le=200),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    user: AuthenticatedUser = Depends(require_admin)
):
    """
    Retrieves recent anonymized product interaction events.
    Strictly restricted to system administrators (SUPER_ADMIN).
    """
    return ProductAnalytics.get_events(limit=limit, event_type=event_type)

@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary():
    """Returns aggregated product usage metrics, completion rates and duration metrics."""
    return ProductAnalytics.get_summary()
