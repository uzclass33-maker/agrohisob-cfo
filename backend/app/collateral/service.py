"""
AgroHisob CFO - Collateral Intelligence Service Facade (Assignment 6, Module A)
Provides unified service methods for screening, valuation, sensitivity analysis,
and preparation summaries.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
import uuid
from typing import Optional

from app.collateral.document_checklist import build_collateral_checklist
from app.collateral.eligibility import screen_land_lease_collateral
from app.collateral.schemas import (
    CollateralPreparationSummary,
    IndicativeValuationRequest,
    IndicativeValuationResult,
    LandLeaseProfile,
)
from app.collateral.sensitivity import run_collateral_sensitivity_analysis
from app.collateral.valuation import calculate_indicative_lease_valuation
from app.reporting.credit_profile import get_default_credit_profile


def get_default_land_lease_profile(org_id: str) -> LandLeaseProfile:
    """Pre-populates a canonical land lease profile based on organization."""
    credit_prof = get_default_credit_profile(org_id)
    org_key = org_id.lower()

    if "exporter" in org_key:
        return LandLeaseProfile(
            organization_id=org_id,
            organization_name=credit_prof.organization_name,
            land_reference="18:05:02:01:03:0115",
            region="Samarqand viloyati",
            district="Urgut tumani",
            area_hectares=120.0,
            land_category="Sug'oriladigan bog'dorchilik va uzumchilik yeri",
            lease_start_date=date(2018, 5, 1),
            lease_expiration_date=date(2048, 5, 1),  # 30 years
            proposed_loan_maturity_date=date(2029, 5, 1),  # 3 years
            proposed_loan_amount_uzs=credit_prof.requested_loan_amount_uzs,
            is_registered_in_cadastre=True,
            registration_number="REG-SAM-2018-0912",
            has_legal_restrictions=False,
            is_disputed=False,
            is_terminated=False,
            is_secondary_lease=False,
            has_sublease_authority_permission=False,
            soil_bonitet_score=72,
            main_crop_type="Gilos va xo'raki uzum",
            normative_annual_net_benefit_per_ha_uzs=Decimal("12000000.00"),
            discount_rate_pct=Decimal("16.00"),
            target_ltv_pct=Decimal("65.00"),
            has_independent_appraisal=True,
            independent_appraisal_value_uzs=Decimal("7800000000.00")
        )
    elif "cluster" in org_key:
        return LandLeaseProfile(
            organization_id=org_id,
            organization_name=credit_prof.organization_name,
            land_reference="19:01:06:02:04:0884",
            region="Qashqadaryo viloyati",
            district="Qarshi tumani",
            area_hectares=2500.0,
            land_category="Sug'oriladigan paxta va g'allachilik massivi",
            lease_start_date=date(2020, 1, 1),
            lease_expiration_date=date(2050, 1, 1),  # 30 years
            proposed_loan_maturity_date=date(2028, 1, 1),  # 2 years
            proposed_loan_amount_uzs=credit_prof.requested_loan_amount_uzs,
            is_registered_in_cadastre=True,
            registration_number="REG-QASH-2020-0045",
            has_legal_restrictions=False,
            is_disputed=False,
            is_terminated=False,
            is_secondary_lease=False,
            has_sublease_authority_permission=False,
            soil_bonitet_score=66,
            main_crop_type="Bug'doy va paxta",
            normative_annual_net_benefit_per_ha_uzs=Decimal("7500000.00"),
            discount_rate_pct=Decimal("15.00"),
            target_ltv_pct=Decimal("65.00"),
            has_independent_appraisal=False,
            independent_appraisal_value_uzs=None
        )
    else:
        # Default: Small farmer
        return LandLeaseProfile(
            organization_id="scenario-small-farmer",
            organization_name="Andijon Baraka Fermer Xo'jaligi",
            land_reference="17:03:04:02:01:0429",
            region="Andijon viloyati",
            district="Asaka tumani",
            area_hectares=65.0,
            land_category="Sug'oriladigan qishloq xo'jaligi yeri",
            lease_start_date=date(2021, 3, 1),
            lease_expiration_date=date(2051, 3, 1),
            proposed_loan_maturity_date=date(2028, 3, 1),
            proposed_loan_amount_uzs=credit_prof.requested_loan_amount_uzs,
            is_registered_in_cadastre=True,
            registration_number="REG-AND-2021-0842",
            has_legal_restrictions=False,
            is_disputed=False,
            is_terminated=False,
            is_secondary_lease=False,
            has_sublease_authority_permission=False,
            soil_bonitet_score=68,
            main_crop_type="Paxta va ertachi sabzavot",
            normative_annual_net_benefit_per_ha_uzs=Decimal("8500000.00"),
            discount_rate_pct=Decimal("16.00"),
            target_ltv_pct=Decimal("65.00"),
            has_independent_appraisal=False,
            independent_appraisal_value_uzs=None
        )


class CollateralService:
    """Service facade for land lease collateral intelligence."""

    @classmethod
    def evaluate_collateral(
        cls,
        profile: LandLeaseProfile,
        valuation_req: Optional[IndicativeValuationRequest] = None
    ) -> CollateralPreparationSummary:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        summary_id = f"col-{uuid.uuid4().hex[:10]}"

        # 1. Legal screening under VMQ-613
        screening = screen_land_lease_collateral(profile)

        # 2. Valuation request resolution
        if not valuation_req:
            remaining_years = max(1, (profile.lease_expiration_date - date.today()).days // 365)
            valuation_req = IndicativeValuationRequest(
                area_hectares=profile.area_hectares,
                soil_bonitet_score=profile.soil_bonitet_score,
                remaining_lease_years=remaining_years,
                normative_annual_net_benefit_per_ha_uzs=profile.normative_annual_net_benefit_per_ha_uzs,
                discount_rate_pct=profile.discount_rate_pct,
                annual_benefit_growth_pct=Decimal("2.00"),
                target_ltv_pct=profile.target_ltv_pct
            )

        # 3. DCF Indicative valuation
        valuation = calculate_indicative_lease_valuation(valuation_req)

        # 4. Multi-scenario sensitivity analysis
        sensitivity = run_collateral_sensitivity_analysis(valuation_req)

        # 5. Document checklist
        checklist = build_collateral_checklist(profile)

        disclaimer = (
            "RASMIY OGOHLANTIRISH VA HUQUQIY CHEKLOV:\n"
            "Mazkur hisobot O'zbekiston Respublikasi Vazirlar Mahkamasining 2025-yil 30-sentabrdagi 613-son qarori "
            "(VMQ-613) talablari asosida shakllantirilgan indikativ tayyorgarlik vositasidir. "
            "Ushbu tahlil «Baholash faoliyati to'g'risida»gi Qonunga muvofiq litsenziyaga ega mustaqil baholovchi "
            "tashkilotning rasmiy baholash hisoboti o'rnini bosmaydi va tijorat bankining qat'iy garov qabuli "
            "yoki kredit ajratish kafolati hisoblanmaydi."
        )

        return CollateralPreparationSummary(
            summary_id=summary_id,
            organization_id=profile.organization_id,
            organization_name=profile.organization_name,
            generation_date=now_str,
            profile=profile,
            screening=screening,
            valuation=valuation,
            sensitivity=sensitivity,
            checklist=checklist,
            regulatory_disclaimer_uz=disclaimer
        )
