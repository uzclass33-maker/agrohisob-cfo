import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Integer, Numeric, DateTime, 
    ForeignKey, Text, JSON, Date
)
from sqlalchemy.orm import relationship
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    inn = Column(String(9), unique=True, nullable=False, index=True) # STIR
    legal_type = Column(String(50), nullable=False) # FERMER_XOJALIGI, MCHJ, AGRO_KLASTER
    region = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    land_hectares = Column(Numeric(10, 2), nullable=False)
    cadastre_number = Column(String(50), nullable=True)
    soil_bonitet_score = Column(Integer, default=65)
    main_crop_type = Column(String(100), nullable=False)
    has_drip_irrigation = Column(Boolean, default=False)
    has_cold_storage = Column(Boolean, default=False)
    cold_storage_capacity_tons = Column(Numeric(10, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    financial_periods = relationship("FinancialPeriod", back_populates="organization", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="organization", cascade="all, delete-orphan")
    imported_files = relationship("ImportedFile", back_populates="organization", cascade="all, delete-orphan")
    debt_schedules = relationship("DebtSchedule", back_populates="organization", cascade="all, delete-orphan")
    forecasts = relationship("FinancialForecast", back_populates="organization", cascade="all, delete-orphan")
    reports = relationship("GeneratedReport", back_populates="organization", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    role = Column(String(50), nullable=False, default="CHIEF_ACCOUNTANT") # CFO, CHIEF_ACCOUNTANT, AUDITOR
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")

class FinancialPeriod(Base):
    __tablename__ = "financial_periods"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=False)
    month_number = Column(Integer, nullable=False) # 1 to 12
    opening_balance = Column(Numeric(18, 2), nullable=False)
    total_inflows = Column(Numeric(18, 2), nullable=False, default=0.0)
    total_outflows = Column(Numeric(18, 2), nullable=False, default=0.0)
    closing_balance = Column(Numeric(18, 2), nullable=False)
    is_closed = Column(Boolean, default=False)
    is_reconciled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="financial_periods")
    transactions = relationship("Transaction", back_populates="period")

class ImportedFile(Base):
    __tablename__ = "imported_files"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    original_file_name = Column(String(255), nullable=False)
    stored_file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False) # SOLIQ_EFAKTURA_EXCEL, BANK_STATEMENT_CSV
    file_hash_sha256 = Column(String(64), nullable=False)
    row_count = Column(Integer, default=0)
    parse_status = Column(String(50), default="PENDING")
    validation_errors_json = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="imported_files")
    transactions = relationship("Transaction", back_populates="imported_file")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    period_id = Column(String(36), ForeignKey("financial_periods.id", ondelete="SET NULL"), nullable=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    imported_file_id = Column(String(36), ForeignKey("imported_files.id", ondelete="SET NULL"), nullable=True)
    transaction_date = Column(Date, nullable=False)
    direction = Column(String(10), nullable=False) # INFLOW, OUTFLOW
    amount = Column(Numeric(18, 2), nullable=False)
    category = Column(String(50), nullable=False) # CROP_SALES, SEEDS, FERTILIZER, FUEL, etc.
    counterparty_name = Column(String(255), nullable=False)
    counterparty_inn = Column(String(9), nullable=True)
    mxik_code = Column(String(20), nullable=True)
    document_number = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="transactions")
    period = relationship("FinancialPeriod", back_populates="transactions")
    imported_file = relationship("ImportedFile", back_populates="transactions")

class DebtSchedule(Base):
    __tablename__ = "debt_schedules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    lender_name = Column(String(150), nullable=False)
    loan_type = Column(String(50), nullable=False)
    contract_number = Column(String(100), nullable=False)
    principal_amount = Column(Numeric(18, 2), nullable=False)
    outstanding_balance = Column(Numeric(18, 2), nullable=False)
    annual_interest_rate = Column(Numeric(5, 2), nullable=False)
    monthly_payment_total = Column(Numeric(18, 2), nullable=False)
    monthly_principal = Column(Numeric(18, 2), nullable=False)
    monthly_interest = Column(Numeric(18, 2), nullable=False)
    start_date = Column(Date, nullable=False)
    maturity_date = Column(Date, nullable=False)
    collateral_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="debt_schedules")

class FinancialForecast(Base):
    __tablename__ = "financial_forecasts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_name = Column(String(150), nullable=False)
    forecast_year = Column(Integer, nullable=False)
    yield_shock_pct = Column(Numeric(5, 2), default=0.0)
    price_shock_pct = Column(Numeric(5, 2), default=0.0)
    cost_shock_pct = Column(Numeric(5, 2), default=0.0)
    projected_annual_inflow = Column(Numeric(18, 2), nullable=False)
    projected_annual_outflow = Column(Numeric(18, 2), nullable=False)
    net_operating_cash_flow = Column(Numeric(18, 2), nullable=False)
    projected_dscr = Column(Numeric(6, 3), nullable=False)
    months_in_deficit = Column(Integer, default=0)
    lowest_cash_balance = Column(Numeric(18, 2), nullable=False)
    monthly_breakdown_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="forecasts")

class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    report_type = Column(String(50), nullable=False)
    report_title = Column(String(255), nullable=False)
    overall_credit_score = Column(Integer, nullable=True)
    credit_rating_tier = Column(String(10), nullable=False)
    annual_dscr = Column(Numeric(6, 3), nullable=False)
    vmq613_estimated_collateral_uzs = Column(Numeric(18, 2), nullable=True)
    report_payload_json = Column(JSON, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="reports")
