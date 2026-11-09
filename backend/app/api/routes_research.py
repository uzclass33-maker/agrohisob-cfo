from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.auth.dependencies import require_admin_or_researcher
from app.auth.models import AuthenticatedUser
from app.research.schemas import (
    ResearchStudy, InterviewRecord, InterviewRecordCreate,
    ResearchSummary
)
from app.research.tracker import ResearchTracker

router = APIRouter(prefix="/research", tags=["Customer Research Tracker"])

@router.get("/studies", response_model=List[ResearchStudy])
def list_studies(user: AuthenticatedUser = Depends(require_admin_or_researcher)):
    """Returns active customer discovery studies. Restricted to admin / researcher."""
    return ResearchTracker.get_studies()

@router.post("/studies", response_model=ResearchStudy, status_code=status.HTTP_201_CREATED)
def create_study(
    title: str,
    description: str,
    target_count: int = 15,
    user: AuthenticatedUser = Depends(require_admin_or_researcher)
):
    """Creates a new structured customer research study. Restricted to admin / researcher."""
    return ResearchTracker.create_study(title=title, description=description, target_count=target_count)

@router.get("/interviews", response_model=List[InterviewRecord])
def list_interviews(
    study_id: Optional[str] = Query(None, description="Filter by study ID"),
    classification: Optional[str] = Query(None, description="Filter by source classification"),
    user: AuthenticatedUser = Depends(require_admin_or_researcher)
):
    """Lists raw interview records with explicit source classification. Restricted to admin / researcher."""
    return ResearchTracker.get_interviews(study_id=study_id, classification=classification)

@router.post("/interviews", response_model=InterviewRecord, status_code=status.HTTP_201_CREATED)
def add_interview_record(
    record: InterviewRecordCreate,
    user: AuthenticatedUser = Depends(require_admin_or_researcher)
):
    """Adds a new customer discovery or assumption record. Restricted to admin / researcher."""
    return ResearchTracker.add_interview(record)

@router.get("/summary", response_model=ResearchSummary)
def get_research_summary():
    """Returns aggregated research findings, cleanly separating verified vs synthetic/assumption records. Publicly safe."""
    return ResearchTracker.get_summary()
