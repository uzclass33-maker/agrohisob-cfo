"""
AgroHisob CFO - Unit Tests for VMQ-613 Land Lease Collateral Screening (Assignment 6, Module A)
"""

from datetime import date
from decimal import Decimal
from app.collateral.eligibility import screen_land_lease_collateral, _add_years_calendar_aware
from app.collateral.schemas import LandLeaseProfile


def test_calendar_aware_date_addition():
    # Normal year
    d1 = date(2026, 5, 10)
    assert _add_years_calendar_aware(d1, 5) == date(2031, 5, 10)

    # Leap year February 29th handling
    d_leap = date(2024, 2, 29)
    # 2029 is not a leap year, must safely roll to Feb 28
    assert _add_years_calendar_aware(d_leap, 5) == date(2029, 2, 28)
    # 2028 is a leap year
    assert _add_years_calendar_aware(d_leap, 4) == date(2028, 2, 29)


def test_vmq613_compliant_profile():
    profile = LandLeaseProfile(
        organization_id="test-org",
        organization_name="Test Fermer",
        land_reference="17:03:04:02:01:0429",
        region="Andijon viloyati",
        district="Asaka tumani",
        area_hectares=50.0,
        land_category="Sug'oriladigan yer",
        lease_start_date=date(2020, 1, 1),
        lease_expiration_date=date(2045, 1, 1),  # 25 years remaining
        proposed_loan_maturity_date=date(2028, 1, 1),  # Loan maturity in 2028 (buffer: 17 years > 5)
        proposed_loan_amount_uzs=Decimal("100000000.00"),
        is_registered_in_cadastre=True,
        has_legal_restrictions=False,
        is_disputed=False,
        is_terminated=False,
        is_secondary_lease=False,
        soil_bonitet_score=68,
        main_crop_type="Paxta",
        normative_annual_net_benefit_per_ha_uzs=Decimal("8000000.00"),
        discount_rate_pct=Decimal("16.00"),
        target_ltv_pct=Decimal("65.00"),
    )

    res = screen_land_lease_collateral(profile)
    assert res.is_eligible is True
    assert res.post_maturity_buffer_years >= 5
    assert len(res.defects) == 0


def test_vmq613_buffer_failure_less_than_5_years():
    # Loan maturity is 2030, lease expiration is 2032 (buffer is only 2 years < 5 years)
    profile = LandLeaseProfile(
        organization_id="test-org",
        organization_name="Test Fermer",
        land_reference="17:03:04:02:01:0429",
        region="Andijon viloyati",
        district="Asaka tumani",
        area_hectares=50.0,
        land_category="Sug'oriladigan yer",
        lease_start_date=date(2012, 1, 1),
        lease_expiration_date=date(2032, 1, 1),
        proposed_loan_maturity_date=date(2030, 1, 1),  # Expiration must be >= 2035-01-01
        proposed_loan_amount_uzs=Decimal("100000000.00"),
        is_registered_in_cadastre=True,
        has_legal_restrictions=False,
        is_disputed=False,
        is_terminated=False,
        is_secondary_lease=False,
        soil_bonitet_score=68,
        main_crop_type="Paxta",
        normative_annual_net_benefit_per_ha_uzs=Decimal("8000000.00"),
        discount_rate_pct=Decimal("16.00"),
        target_ltv_pct=Decimal("65.00"),
    )

    res = screen_land_lease_collateral(profile)
    assert res.is_eligible is False
    assert any("5 yillik bufer" in d for d in res.defects)


def test_vmq613_unregistered_cadastre_failure():
    profile = LandLeaseProfile(
        organization_id="test-org",
        organization_name="Test Fermer",
        land_reference="17:03:04:02:01:0429",
        region="Andijon viloyati",
        district="Asaka tumani",
        area_hectares=50.0,
        land_category="Sug'oriladigan yer",
        lease_start_date=date(2020, 1, 1),
        lease_expiration_date=date(2045, 1, 1),
        proposed_loan_maturity_date=date(2028, 1, 1),
        proposed_loan_amount_uzs=Decimal("100000000.00"),
        is_registered_in_cadastre=False,  # Not registered
        has_legal_restrictions=False,
        is_disputed=False,
        is_terminated=False,
        is_secondary_lease=False,
        soil_bonitet_score=68,
        main_crop_type="Paxta",
        normative_annual_net_benefit_per_ha_uzs=Decimal("8000000.00"),
        discount_rate_pct=Decimal("16.00"),
        target_ltv_pct=Decimal("65.00"),
    )

    res = screen_land_lease_collateral(profile)
    assert res.is_eligible is False
    assert any("davlat ro'yxatidan o'tkazilmagan" in d for d in res.defects)


def test_vmq613_secondary_lease_requires_permission():
    # Secondary lease without permission fails
    profile_no_perm = LandLeaseProfile(
        organization_id="test-org",
        organization_name="Test Fermer",
        land_reference="17:03:04:02:01:0429",
        region="Andijon viloyati",
        district="Asaka tumani",
        area_hectares=50.0,
        land_category="Sug'oriladigan yer",
        lease_start_date=date(2020, 1, 1),
        lease_expiration_date=date(2045, 1, 1),
        proposed_loan_maturity_date=date(2028, 1, 1),
        proposed_loan_amount_uzs=Decimal("100000000.00"),
        is_registered_in_cadastre=True,
        has_legal_restrictions=False,
        is_disputed=False,
        is_terminated=False,
        is_secondary_lease=True,
        has_sublease_authority_permission=False,  # Missing
        soil_bonitet_score=68,
        main_crop_type="Paxta",
        normative_annual_net_benefit_per_ha_uzs=Decimal("8000000.00"),
        discount_rate_pct=Decimal("16.00"),
        target_ltv_pct=Decimal("65.00"),
    )

    res = screen_land_lease_collateral(profile_no_perm)
    assert res.is_eligible is False
    assert any("Ikkilamchi ijara" in d for d in res.defects)

    # With permission passes
    profile_with_perm = profile_no_perm.model_copy(update={"has_sublease_authority_permission": True})
    res_perm = screen_land_lease_collateral(profile_with_perm)
    assert res_perm.is_eligible is True
