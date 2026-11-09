import os
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from app.research.schemas import (
    InterviewRecord, InterviewRecordCreate,
    ResearchStudy, ResearchSummary,
    SourceClassification, CustomerSegment, InterviewStatus
)

# Configurable storage directory to allow full isolation during testing
_DEFAULT_RESEARCH_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "research")
RESEARCH_DIR = os.environ.get("AGROHISOB_RESEARCH_DIR", _DEFAULT_RESEARCH_DIR)
os.makedirs(RESEARCH_DIR, exist_ok=True)

STUDIES_FILE = os.path.join(RESEARCH_DIR, "studies.json")
INTERVIEWS_FILE = os.path.join(RESEARCH_DIR, "interviews.json")

def set_research_storage_dir(custom_dir: str):
    """Overrides the storage directory for deterministic, isolated unit and integration testing."""
    global RESEARCH_DIR, STUDIES_FILE, INTERVIEWS_FILE
    RESEARCH_DIR = custom_dir
    os.makedirs(RESEARCH_DIR, exist_ok=True)
    STUDIES_FILE = os.path.join(RESEARCH_DIR, "studies.json")
    INTERVIEWS_FILE = os.path.join(RESEARCH_DIR, "interviews.json")
    init_default_research()

def _load_json(file_path: str, default_val):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_val, f, indent=2, ensure_ascii=False)
        return default_val
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_val

def _save_json(file_path: str, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _sync_interview_to_db(r: dict):
    """Saves interview record to durable database table."""
    try:
        from app.db.database import SessionLocal
        from app.models.core import ResearchInterviewModel, ResearchStudyModel
        session = SessionLocal()
        try:
            study_id = r.get("study_id", "study-agrohisob-2026")
            st = session.query(ResearchStudyModel).filter(ResearchStudyModel.id == study_id).first()
            if not st:
                st = ResearchStudyModel(
                    id=study_id,
                    title="O'zbekiston Agrar Buxgalteriyasi va Kassa Rejalashtirish Tadqiqoti 2026",
                    description="Fermerlar, eksportyorlar va klasterlar bilan tizimli intervyu",
                    target_count=19,
                    status="ACTIVE"
                )
                session.add(st)
                session.commit()

            rec = session.query(ResearchInterviewModel).filter(ResearchInterviewModel.id == r.get("id")).first()
            if not rec:
                rec = ResearchInterviewModel(
                    id=r.get("id"),
                    study_id=study_id,
                    code=r.get("code", "REC"),
                    customer_segment=r.get("customer_segment", "FARMER"),
                    source_classification=r.get("source_classification", "UNVERIFIED_NOTE"),
                    interview_status=r.get("interview_status", "PLANNED"),
                    participant_role=r.get("participant_role", ""),
                    region=r.get("region", "Toshkent"),
                    consent_recorded=r.get("consent_recorded", False),
                    interview_date=r.get("date"),
                    validated_problems=r.get("validated_problems", []),
                    unverified_assumptions=r.get("unverified_assumptions", []),
                    evidence_references=r.get("evidence_references", []),
                    notes=r.get("notes", "")
                )
                session.add(rec)
            else:
                rec.interview_status = r.get("interview_status", rec.interview_status)
                rec.validated_problems = r.get("validated_problems", rec.validated_problems)
                rec.unverified_assumptions = r.get("unverified_assumptions", rec.unverified_assumptions)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
    except Exception:
        pass


def init_default_research():
    studies = _load_json(STUDIES_FILE, [])
    if not studies:
        studies = [
            {
                "id": "study-agrohisob-2026",
                "title": "O'zbekiston Agrar Buxgalteriyasi va Kassa Rejalashtirish Tadqiqoti 2026",
                "description": "Fermerlar, eksportyorlar va klasterlar bilan 15-20 ta tizimli intervyu",
                "target_count": 19,
                "created_at": "2026-11-09T00:00:00Z",
                "status": "ACTIVE"
            }
        ]
        _save_json(STUDIES_FILE, studies)

    interviews = _load_json(INTERVIEWS_FILE, [])
    if not interviews:
        # Pre-populate planned target interview structure (STATUS: PLANNED, CLASSIFICATION: UNVERIFIED_NOTE / FOUNDER_ASSUMPTION)
        # Note: None of these are marked as VERIFIED_INTERVIEW until actually conducted!
        initial_targets = [
            {
                "id": "rec-target-01",
                "study_id": "study-agrohisob-2026",
                "code": "INT-FARM-01",
                "customer_segment": CustomerSegment.FARMER.value,
                "source_classification": SourceClassification.UNVERIFIED_NOTE.value,
                "interview_status": InterviewStatus.PLANNED.value,
                "participant_role": "Fermer xo'jaligi rahbari",
                "region": "Samarqand viloyati",
                "consent_recorded": False,
                "date": None,
                "validated_problems": [],
                "unverified_assumptions": ["Mavsumiy kassa uzilishi bahorda 30-40 kun davom etadi"],
                "evidence_references": [],
                "notes": "Tadqiqot rejasiga kiritilgan nishon respondent",
                "created_at": "2026-11-09T09:00:00Z"
            },
            {
                "id": "rec-target-02",
                "study_id": "study-agrohisob-2026",
                "code": "INT-EXP-01",
                "customer_segment": CustomerSegment.EXPORTER.value,
                "source_classification": SourceClassification.UNVERIFIED_NOTE.value,
                "interview_status": InterviewStatus.PLANNED.value,
                "participant_role": "Bosh buxgalter",
                "region": "Toshkent viloyati",
                "consent_recorded": False,
                "date": None,
                "validated_problems": [],
                "unverified_assumptions": ["Eksport subsidiyasini (PF-82) hisoblash 10 kundan ko'p vaqt oladi"],
                "evidence_references": [],
                "notes": "Meva-sabzavot eksportyori bosh buxgalteri bilan suhbat rejalashtirilgan",
                "created_at": "2026-11-09T09:00:00Z"
            },
            {
                "id": "rec-target-03",
                "study_id": "study-agrohisob-2026",
                "code": "INT-DEMO-01",
                "customer_segment": CustomerSegment.FARMER.value,
                "source_classification": SourceClassification.SYNTHETIC_DEMO.value,
                "interview_status": InterviewStatus.CONDUCTED.value,
                "participant_role": "Sintetik Demo Profil: Zarafshon Baraka",
                "region": "Navoiy viloyati",
                "consent_recorded": True,
                "date": "2026-11-08",
                "validated_problems": ["Sintetik sinov: sabzavot ekishda bahorgi yoqilg'i xarajati"],
                "unverified_assumptions": [],
                "evidence_references": ["synthetic-demo-db"],
                "notes": "MVP sinovi uchun sintetik profil. Real mijoz hisoblanmaydi.",
                "created_at": "2026-11-08T12:00:00Z"
            }
        ]
        _save_json(INTERVIEWS_FILE, initial_targets)

init_default_research()

class ResearchTracker:
    @staticmethod
    def get_studies() -> List[ResearchStudy]:
        init_default_research()
        data = _load_json(STUDIES_FILE, [])
        return [ResearchStudy(**s) for s in data]

    @staticmethod
    def create_study(title: str, description: str, target_count: int = 15) -> ResearchStudy:
        studies = _load_json(STUDIES_FILE, [])
        study = {
            "id": f"study-{uuid.uuid4().hex[:8]}",
            "title": title,
            "description": description,
            "target_count": target_count,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "ACTIVE"
        }
        studies.append(study)
        _save_json(STUDIES_FILE, studies)
        return ResearchStudy(**study)

    @staticmethod
    def get_interviews(study_id: Optional[str] = None, classification: Optional[str] = None) -> List[InterviewRecord]:
        init_default_research()
        records = _load_json(INTERVIEWS_FILE, [])
        if study_id:
            records = [r for r in records if r.get("study_id") == study_id]
        if classification:
            records = [r for r in records if r.get("source_classification") == classification]
        return [InterviewRecord(**r) for r in records]

    @staticmethod
    def add_interview(data: InterviewRecordCreate) -> InterviewRecord:
        records = _load_json(INTERVIEWS_FILE, [])
        rec_id = f"rec-{uuid.uuid4().hex[:8]}"
        record = data.model_dump()
        record["id"] = rec_id
        record["created_at"] = datetime.now(timezone.utc).isoformat()
        records.append(record)
        _save_json(INTERVIEWS_FILE, records)
        _sync_interview_to_db(record)
        return InterviewRecord(**record)

    @staticmethod
    def get_summary() -> ResearchSummary:
        records = _load_json(INTERVIEWS_FILE, [])
        verified = sum(1 for r in records if r.get("source_classification") == SourceClassification.VERIFIED_INTERVIEW.value)
        unverified = sum(1 for r in records if r.get("source_classification") == SourceClassification.UNVERIFIED_NOTE.value)
        synthetic = sum(1 for r in records if r.get("source_classification") == SourceClassification.SYNTHETIC_DEMO.value)
        secondary = sum(1 for r in records if r.get("source_classification") == SourceClassification.SECONDARY_RESEARCH.value)
        assumptions = sum(1 for r in records if r.get("source_classification") == SourceClassification.FOUNDER_ASSUMPTION.value)

        seg_dist = {}
        for r in records:
            seg = r.get("customer_segment", "UNKNOWN")
            seg_dist[seg] = seg_dist.get(seg, 0) + 1

        # Aggregate problems and assumptions
        problems_count = {}
        for r in records:
            # Only count problems from verified or secondary sources
            if r.get("source_classification") in [SourceClassification.VERIFIED_INTERVIEW.value, SourceClassification.SECONDARY_RESEARCH.value]:
                for p in r.get("validated_problems", []):
                    problems_count[p] = problems_count.get(p, 0) + 1

        top_problems = [{"problem": k, "count": v} for k, v in sorted(problems_count.items(), key=lambda x: x[1], reverse=True)[:5]]

        assumptions_list = []
        for r in records:
            for a in r.get("unverified_assumptions", []):
                assumptions_list.append({"assumption": a, "source": r.get("code")})

        return ResearchSummary(
            total_records=len(records),
            verified_interviews=verified,
            unverified_notes=unverified,
            synthetic_demo_records=synthetic,
            secondary_research_count=secondary,
            founder_assumptions=assumptions,
            segment_distribution=seg_dist,
            top_validated_problems=top_problems,
            open_assumptions=assumptions_list
        )
