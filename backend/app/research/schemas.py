from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class SourceClassification(str, Enum):
    VERIFIED_INTERVIEW = "VERIFIED_INTERVIEW"
    UNVERIFIED_NOTE = "UNVERIFIED_NOTE"
    SYNTHETIC_DEMO = "SYNTHETIC_DEMO"
    SECONDARY_RESEARCH = "SECONDARY_RESEARCH"
    FOUNDER_ASSUMPTION = "FOUNDER_ASSUMPTION"

class CustomerSegment(str, Enum):
    FARMER = "FARMER"
    EXPORTER = "EXPORTER"
    SME = "SME"
    CLUSTER = "CLUSTER"
    ACCOUNTANT_CFO = "ACCOUNTANT_CFO"

class InterviewStatus(str, Enum):
    PLANNED = "PLANNED"
    SCHEDULED = "SCHEDULED"
    CONDUCTED = "CONDUCTED"
    CANCELLED = "CANCELLED"

class InterviewRecordCreate(BaseModel):
    study_id: str = Field(default="study-agroventures-2026", description="Study ID")
    code: str = Field(..., description="Unique interview identifier, e.g. INT-FARM-01")
    customer_segment: CustomerSegment
    source_classification: SourceClassification = Field(default=SourceClassification.UNVERIFIED_NOTE)
    interview_status: InterviewStatus = Field(default=InterviewStatus.PLANNED)
    participant_role: str = Field(..., description="Job role, e.g. Chief Accountant, Farm Owner")
    region: str = Field(..., description="Region in Uzbekistan")
    consent_recorded: bool = Field(default=False)
    date: Optional[str] = None
    validated_problems: List[str] = Field(default_factory=list)
    unverified_assumptions: List[str] = Field(default_factory=list)
    evidence_references: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

class InterviewRecord(InterviewRecordCreate):
    id: str
    created_at: str

class ResearchStudy(BaseModel):
    id: str
    title: str
    description: str
    target_count: int
    created_at: str
    status: str

class ResearchSummary(BaseModel):
    total_records: int
    verified_interviews: int
    unverified_notes: int
    synthetic_demo_records: int
    secondary_research_count: int
    founder_assumptions: int
    segment_distribution: dict
    top_validated_problems: List[dict]
    open_assumptions: List[dict]
