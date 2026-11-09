"""
AgroHisob CFO - Collateral & Subsidy Database Models (Assignment 6)
Persists land lease profiles, collateral assessments, subsidy registries, and assessments.
"""

from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.core import generate_uuid


class LandLeaseProfileModel(Base):
    __tablename__ = "land_lease_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    cadastral_number = Column(String(50), nullable=False)
    region = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    area_hectares = Column(Numeric(10, 2), nullable=False)
    lease_start_date = Column(Date, nullable=False)
    lease_end_date = Column(Date, nullable=False)
    is_state_registered = Column(Boolean, default=True)
    has_judicial_dispute = Column(Boolean, default=False)
    is_already_pledged = Column(Boolean, default=False)
    has_sublease_permission = Column(Boolean, default=True)
    soil_bonitet_score = Column(Integer, default=65)
    main_crop_type = Column(String(100), nullable=False, default="Paxta")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CollateralAssessmentModel(Base):
    __tablename__ = "collateral_assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    land_lease_profile_id = Column(String(36), ForeignKey("land_lease_profiles.id", ondelete="SET NULL"), nullable=True)
    assessment_date = Column(Date, nullable=False)
    is_vmq613_eligible = Column(Boolean, nullable=False)
    overall_status = Column(String(50), nullable=False)
    indicative_market_value_uzs = Column(Numeric(18, 2), nullable=False)
    max_pledge_value_uzs = Column(Numeric(18, 2), nullable=False)
    ltv_percentage = Column(Numeric(5, 2), default=50.0)
    readiness_percentage = Column(Numeric(5, 2), default=0.0)
    assessment_payload_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SubsidyProgramModel(Base):
    __tablename__ = "subsidy_programs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    program_code = Column(String(50), unique=True, nullable=False, index=True)
    program_name_uz = Column(String(255), nullable=False)
    managing_authority_uz = Column(String(255), nullable=False)
    legal_source_code = Column(String(50), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    verification_status = Column(String(50), default="VERIFIED_ACTIVE")
    payload_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SubsidyAssessmentModel(Base):
    __tablename__ = "subsidy_assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_date = Column(Date, nullable=False)
    total_potential_subsidy_uzs = Column(Numeric(18, 2), nullable=False)
    immediate_cash_inflow_potential_uzs = Column(Numeric(18, 2), nullable=False)
    conditional_future_inflow_uzs = Column(Numeric(18, 2), nullable=False)
    results_payload_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
