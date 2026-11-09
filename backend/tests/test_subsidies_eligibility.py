"""
AgroHisob CFO - Unit Tests for Subsidy Program Matching & 5-Status Screening (Assignment 6, Module B)
"""

from datetime import date
from decimal import Decimal
from app.subsidies.eligibility import evaluate_subsidy_eligibility
from app.subsidies.program_matcher import match_subsidy_programs
from app.subsidies.rule_registry import get_subsidy_program
from app.subsidies.schemas import (
    SubsidyEligibilityStatusEnum,
    SubsidyMatchRequest,
)


def test_subsidy_potentially_eligible_status():
    prog = get_subsidy_program("PQ47-DRIP-COTTON")
    assert prog is not None

    req = SubsidyMatchRequest(
        organization_id="test-org",
        region="Andijon viloyati",
        district="Asaka tumani",
        crop_types=["Paxta", "Bug'doy"],
        land_hectares=50.0,
        has_drip_irrigation=True,
        has_bank_debt=True,
    )

    status, label, reasons, missing, amount = evaluate_subsidy_eligibility(prog, req)
    assert status == SubsidyEligibilityStatusEnum.POTENTIALLY_ELIGIBLE
    assert amount == Decimal("8000000.00") * Decimal("50.0")
    assert len(reasons) >= 2


def test_subsidy_not_eligible_crop_mismatch():
    prog = get_subsidy_program("PF82-COTTON-INTEREST")
    assert prog is not None

    req = SubsidyMatchRequest(
        organization_id="test-org",
        region="Samarqand viloyati",
        district="Urgut tumani",
        crop_types=["Olma", "Uzum"],  # Neither cotton nor wheat
        land_hectares=30.0,
        has_drip_irrigation=True,
        has_bank_debt=True,
    )

    status, label, reasons, missing, amount = evaluate_subsidy_eligibility(prog, req)
    assert status == SubsidyEligibilityStatusEnum.NOT_ELIGIBLE_UNDER_VERIFIED_RULE
    assert len(missing) >= 1


def test_subsidy_more_information_required_missing_hectares():
    prog = get_subsidy_program("PQ47-DRIP-COTTON")
    assert prog is not None

    req = SubsidyMatchRequest(
        organization_id="test-org",
        region="Andijon viloyati",
        district="Asaka tumani",
        crop_types=["Paxta"],
        land_hectares=0.0,  # Zero hectares
        has_drip_irrigation=True,
        has_bank_debt=True,
    )

    status, label, reasons, missing, amount = evaluate_subsidy_eligibility(prog, req)
    assert status == SubsidyEligibilityStatusEnum.MORE_INFORMATION_REQUIRED


def test_subsidy_outside_effective_period():
    prog = get_subsidy_program("PF82-COTTON-INTEREST")
    assert prog is not None

    # PF-82 effective from 2026-05-08. Testing assessment date prior to effective date.
    req = SubsidyMatchRequest(
        organization_id="test-org",
        region="Andijon viloyati",
        district="Asaka tumani",
        crop_types=["Paxta"],
        land_hectares=50.0,
        has_drip_irrigation=True,
        has_bank_debt=True,
        assessment_date=date(2026, 1, 15),  # Before 2026-05-08
    )

    status, label, reasons, missing, amount = evaluate_subsidy_eligibility(prog, req)
    assert status == SubsidyEligibilityStatusEnum.OUTSIDE_EFFECTIVE_PERIOD


def test_program_matcher_sorting():
    req = SubsidyMatchRequest(
        organization_id="test-org",
        region="Andijon viloyati",
        district="Asaka tumani",
        crop_types=["Paxta"],
        land_hectares=65.0,
        has_drip_irrigation=True,
        has_bank_debt=True,
        assessment_date=date(2026, 6, 1),
    )

    matches = match_subsidy_programs(req)
    assert len(matches) >= 5

    # First matches must be POTENTIALLY_ELIGIBLE
    first = matches[0]
    assert first.eligibility_status == SubsidyEligibilityStatusEnum.POTENTIALLY_ELIGIBLE
