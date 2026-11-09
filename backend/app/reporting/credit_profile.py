"""
AgroHisob CFO - Credit Profile Service
Handles validation, default instantiation, and loan parameter verification for Agribusiness credit dossiers.
"""

from decimal import Decimal
from typing import List, Tuple
from app.reporting.report_schemas import CreditProfile, LoanPurposeEnum
from app.services.synthetic_data import SMALL_FARMER_DATA, EXPORTER_DATA, CLUSTER_DATA


def validate_credit_profile(profile: CreditProfile) -> Tuple[bool, List[str]]:
    """
    Validates credit profile for mandatory financial parameters, bounds and data consistency.
    Returns (is_valid, validation_errors).
    """
    errors: List[str] = []

    if profile.requested_loan_amount_uzs <= Decimal("0.00"):
        errors.append("So'ralayotgan kredit summasi 0 dan katta bo'lishi shart.")

    if profile.proposed_term_months < 1:
        errors.append("Kredit muddati kamida 1 oy bo'lishi kerak.")
    elif profile.proposed_term_months > 120:
        errors.append("Kredit muddati 120 oydan oshmasligi kerak.")

    if profile.proposed_annual_interest_rate_pct < Decimal("0.00"):
        errors.append("Yillik foiz stavkasi manfiy bo'lishi mumkin emas.")
    elif profile.proposed_annual_interest_rate_pct > Decimal("50.00"):
        errors.append("Yillik foiz stavkasi 50% dan yuqori bo'lishi mumkin emas.")

    if profile.grace_period_months >= profile.proposed_term_months:
        errors.append("Imtiyozli davr kreditning umumiy muddatidan kam bo'lishi shart.")

    if profile.land_hectares <= 0:
        errors.append("Ekin maydoni 0 dan katta bo'lishi shart.")

    if not profile.organization_name.strip():
        errors.append("Korxona nomi bo'sh bo'lishi mumkin emas.")

    return len(errors) == 0, errors


def get_default_credit_profile(org_id: str) -> CreditProfile:
    """Pre-populates a canonical credit profile tailored to the organization's business activity."""
    org_key = org_id.lower()
    if "exporter" in org_key:
        return CreditProfile(
            organization_id="scenario-exporter",
            organization_name="«Samarqand Agro Eksport» MChJ",
            organization_type="MCHJ",
            business_activity="Meva-sabzavot eksporti va zamonaviy muzlatkich omborxona",
            region="Samarqand viloyati",
            district="Urgut tumani",
            inn="308112490",
            operating_years=12,
            reporting_currency="UZS",
            land_hectares=120.0,
            main_crop_types=["Gilos", "Xo'raki uzum", "Mayiz"],
            harvest_months=[5, 6, 8, 9, 10],
            sales_months=[5, 6, 7, 8, 9, 10, 11],
            customer_segments="Rossiya va Yevroosiyo xalqaro tarmoqlari, ichki ulgurji bozor",
            requested_loan_amount_uzs=Decimal("800000000.00"),
            loan_purpose=LoanPurposeEnum.WORKING_CAPITAL,
            proposed_term_months=36,
            proposed_annual_interest_rate_pct=Decimal("21.50"),
            repayment_structure="ANNUITY",
            grace_period_months=6,
            expected_disbursement_date="2026-04-01"
        )
    elif "cluster" in org_key:
        return CreditProfile(
            organization_id="scenario-cluster",
            organization_name="«Qashqadaryo Paxta-G'alla Klasteri»",
            organization_type="AGRO_KLASTER",
            business_activity="Vertikal integratsiyalashgan paxta-to'qimachilik va g'alla klasteri",
            region="Qashqadaryo viloyati",
            district="Qarshi tumani",
            inn="309554210",
            operating_years=6,
            reporting_currency="UZS",
            land_hectares=2500.0,
            main_crop_types=["Bug'doy", "Paxta"],
            harvest_months=[6, 7, 9, 10, 11],
            sales_months=[6, 7, 8, 9, 10, 11, 12],
            customer_segments="Ip-kalava fabrikalari, un kombinatlari, davlat zaxirasi",
            requested_loan_amount_uzs=Decimal("4000000000.00"),
            loan_purpose=LoanPurposeEnum.MACHINERY_EQUIPMENT,
            proposed_term_months=48,
            proposed_annual_interest_rate_pct=Decimal("14.00"),
            repayment_structure="EQUAL_PRINCIPAL",
            grace_period_months=6,
            expected_disbursement_date="2026-03-01"
        )
    else:
        # Default: Small farmer
        return CreditProfile(
            organization_id="scenario-small-farmer",
            organization_name="Andijon Baraka Fermer Xo'jaligi",
            organization_type="FERMER_XOJALIGI",
            business_activity="Paxtachilik va ertachi poliz/sabzavot yetishtirish",
            region="Andijon viloyati",
            district="Asaka tumani",
            inn="304819205",
            operating_years=8,
            reporting_currency="UZS",
            land_hectares=65.0,
            main_crop_types=["Paxta", "Mavsumiy Sabzavotlar"],
            harvest_months=[6, 7, 9, 10, 11],
            sales_months=[6, 7, 8, 9, 10, 11, 12],
            customer_segments="Tuman klasteri, mahalliy dehqon bozorlari",
            requested_loan_amount_uzs=Decimal("150000000.00"),
            loan_purpose=LoanPurposeEnum.AGRICULTURAL_INPUTS,
            proposed_term_months=24,
            proposed_annual_interest_rate_pct=Decimal("14.00"),
            repayment_structure="ANNUITY",
            grace_period_months=3,
            expected_disbursement_date="2026-03-01"
        )
