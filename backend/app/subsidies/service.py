"""
AgroHisob CFO - Agricultural Subsidy Intelligence Service (Assignment 6, Module B)
Facade service orchestrating program matching, detailed calculators, and financial impact synthesis.
"""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from app.subsidies.calculators import calculate_pf82_compensation, calculate_pq47_subsidy
from app.subsidies.program_matcher import match_subsidy_programs
from app.subsidies.rule_registry import get_subsidy_program, list_subsidy_programs
from app.subsidies.schemas import (
    PF82CalculationRequest,
    PF82CalculationResult,
    PQ47CalculationRequest,
    PQ47CalculationResult,
    SubsidyEligibilityStatusEnum,
    SubsidyFinancialImpactResponse,
    SubsidyMatchItem,
    SubsidyMatchRequest,
    SubsidyProgram,
)


class SubsidyService:
    @staticmethod
    def get_all_programs() -> List[SubsidyProgram]:
        return list_subsidy_programs()

    @staticmethod
    def get_program(code: str) -> Optional[SubsidyProgram]:
        return get_subsidy_program(code)

    @staticmethod
    def calculate_pq47(req: PQ47CalculationRequest) -> PQ47CalculationResult:
        return calculate_pq47_subsidy(req)

    @staticmethod
    def calculate_pf82(req: PF82CalculationRequest) -> PF82CalculationResult:
        return calculate_pf82_compensation(req)

    @staticmethod
    def match(req: SubsidyMatchRequest) -> List[SubsidyMatchItem]:
        return match_subsidy_programs(req)

    @classmethod
    def calculate_financial_impact(cls, req: SubsidyMatchRequest) -> SubsidyFinancialImpactResponse:
        matched_items = cls.match(req)

        # Sum indicative amounts only for POTENTIALLY_ELIGIBLE programs
        total_potential = Decimal("0.00")
        for item in matched_items:
            if item.eligibility_status == SubsidyEligibilityStatusEnum.POTENTIALLY_ELIGIBLE:
                if item.indicative_support_amount_uzs:
                    total_potential += item.indicative_support_amount_uzs

        # Phase 1 (50% upfront upon verification) vs Phase 2 (50% post-season)
        phase_1 = (total_potential * Decimal("0.50")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        phase_2 = total_potential - phase_1

        eval_date_str = (req.assessment_date or date.today()).isoformat()

        cash_flow_impact = (
            "Kassa oqimi ta'siri: Potentsial subsidiyalar tarixiy pul mablag'lariga qo'shilmaydi. "
            f"Tizim ishga tushirilgach 1-bosqichda kutilayotgan tushum: {phase_1:,.0f} UZS. "
            f"Mavsum yakunida 2-bosqich shartli tushumi: {phase_2:,.0f} UZS. "
            "Ushbu mablag'lar mavsumiy operatsion xarajatlar yukini sezilarli darajada pasaytiradi."
        )

        dscr_impact = (
            "Qarz qoplash koeffitsiyenti (DSCR) ta'siri: PF-82 va PQ-47 bo'yicha foiz subsidiyalari "
            "(4% dan 10 foiz bandigacha) fermer xo'jaligining yillik qarzga xizmat ko'rsatish "
            "yukini (Debt Service) kamaytiradi va natijada DSCR ko'rsatkichini 0.15 - 0.35 punktga oshirish imkonini beradi."
        )

        disclaimer = (
            "YURIDIK RAD ETISH (DISCLAIMER): Mazkur tahlil O'zbekiston Respublikasi PQ-47 va PF-82 qarorlari "
            "talablari asosida tuzilgan indikativ modellashtirish natijasidir. U davlat organlari tomonidan "
            "mablag' ajratilishini kafolatlamaydi va rasmiy byudjet qarori o'rnini bosmaydi."
        )

        return SubsidyFinancialImpactResponse(
            organization_id=req.organization_id,
            organization_name="Fermer xo'jaligi",
            assessment_date=eval_date_str,
            matched_programs=matched_items,
            total_potential_subsidy_uzs=total_potential,
            immediate_cash_inflow_potential_uzs=phase_1,
            conditional_future_inflow_uzs=phase_2,
            impact_on_cash_flow_uz=cash_flow_impact,
            impact_on_dscr_uz=dscr_impact,
            statutory_disclaimer_uz=disclaimer,
        )
