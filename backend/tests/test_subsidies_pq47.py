"""
AgroHisob CFO - Unit Tests for PQ-47 Water-Saving Subsidies (Assignment 6, Module B)
"""

from decimal import Decimal
from app.subsidies.calculators import calculate_pq47_subsidy
from app.subsidies.schemas import PQ47CalculationRequest


def test_pq47_cotton_standard_rate():
    req = PQ47CalculationRequest(
        crop_type="Paxta",
        area_hectares=25.0,
        technology_type="DRIP_IRRIGATION",
        region="Andijon viloyati",
        district="Asaka tumani",
        installation_cost_uzs=Decimal("250000000.00"),
        financed_via_bank_loan=False,
    )

    res = calculate_pq47_subsidy(req)
    assert res.is_eligible is True
    # Cotton rate = 8,000,000 UZS/ha
    assert res.base_rate_per_ha_uzs == Decimal("8000000.00")
    assert res.regional_coefficient == 1.0
    # 25 ha * 8M = 200,000,000 UZS
    assert res.estimated_total_subsidy_uzs == Decimal("200000000.00")

    # 50/50 phased disbursement
    assert res.phase_1_initial_disbursement_uzs == Decimal("100000000.00")
    assert res.phase_2_conditional_disbursement_uzs == Decimal("100000000.00")
    assert res.phase_1_initial_disbursement_uzs + res.phase_2_conditional_disbursement_uzs == res.estimated_total_subsidy_uzs


def test_pq47_orchard_rate():
    req = PQ47CalculationRequest(
        crop_type="Intensiv bog'",
        area_hectares=10.0,
        technology_type="DRIP_IRRIGATION",
        region="Samarqand viloyati",
        district="Urgut tumani",
        installation_cost_uzs=Decimal("150000000.00"),
        financed_via_bank_loan=False,
    )

    res = calculate_pq47_subsidy(req)
    # Orchard rate = 11,000,000 UZS/ha under official norms
    assert res.base_rate_per_ha_uzs == Decimal("11000000.00")
    assert res.estimated_total_subsidy_uzs == Decimal("110000000.00")
    assert res.legal_source == "O'zbekiston Respublikasi Prezidentining 2026-yil 5-fevraldagi PQ-47-son qarori 3-bandi"
    assert "indikativ" in res.statutory_disclaimer_uz.lower()


def test_pq47_regional_coefficient_water_scarce():
    # Priority region: Qoraqalpog'iston (1.25x multiplier under PQ-47 3-band)
    req = PQ47CalculationRequest(
        crop_type="Paxta",
        area_hectares=20.0,
        technology_type="DRIP_IRRIGATION",
        region="Qoraqalpog'iston Respublikasi",
        district="To'rtko'l tumani",
        installation_cost_uzs=Decimal("200000000.00"),
        financed_via_bank_loan=False,
    )

    res = calculate_pq47_subsidy(req)
    assert res.regional_coefficient == 1.25
    # Base: 8M * 1.25 = 10.0M UZS/ha
    assert res.effective_rate_per_ha_uzs == Decimal("10000000.00")
    # 20 ha * 10.0M = 200M UZS
    assert res.estimated_total_subsidy_uzs == Decimal("200000000.00")


def test_pq47_interest_rate_compensation():
    # Bank loan: 200M UZS loan principal, 4 percentage points compensation
    req = PQ47CalculationRequest(
        crop_type="Paxta",
        area_hectares=20.0,
        technology_type="DRIP_IRRIGATION",
        region="Andijon viloyati",
        district="Asaka tumani",
        installation_cost_uzs=Decimal("200000000.00"),
        financed_via_bank_loan=True,
        loan_principal_uzs=Decimal("200000000.00"),
        annual_interest_rate_pct=Decimal("14.00"),
    )

    res = calculate_pq47_subsidy(req)
    assert res.interest_compensation_pct_points == Decimal("4.00")
    # 200M * 4% = 8,000,000 UZS annual interest relief
    assert res.interest_compensation_annual_uzs == Decimal("8000000.00")
