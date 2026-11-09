"""
AgroHisob CFO - Agricultural Subsidy Program Matcher (Assignment 6, Module B)
Matches farm characteristics against all active subsidy programs in the registry.
"""

from typing import List

from app.subsidies.eligibility import evaluate_subsidy_eligibility
from app.subsidies.rule_registry import list_subsidy_programs
from app.subsidies.schemas import SubsidyEligibilityStatusEnum, SubsidyMatchItem, SubsidyMatchRequest


def match_subsidy_programs(req: SubsidyMatchRequest) -> List[SubsidyMatchItem]:
    """
    Evaluates farm profile against all registered subsidy programs and returns sorted results.
    """
    programs = list_subsidy_programs()
    matched_items: List[SubsidyMatchItem] = []

    for prog in programs:
        status, label, reasons, missing, amount = evaluate_subsidy_eligibility(prog, req)
        matched_items.append(
            SubsidyMatchItem(
                program=prog,
                eligibility_status=status,
                eligibility_label_uz=label,
                indicative_support_amount_uzs=amount if amount > 0 else None,
                match_reasons_uz=reasons,
                missing_conditions_uz=missing,
            )
        )

    # Sort: POTENTIALLY_ELIGIBLE first, then MORE_INFORMATION_REQUIRED, etc.
    status_priority = {
        SubsidyEligibilityStatusEnum.POTENTIALLY_ELIGIBLE: 1,
        SubsidyEligibilityStatusEnum.MORE_INFORMATION_REQUIRED: 2,
        SubsidyEligibilityStatusEnum.NOT_ELIGIBLE_UNDER_VERIFIED_RULE: 3,
        SubsidyEligibilityStatusEnum.OUTSIDE_EFFECTIVE_PERIOD: 4,
        SubsidyEligibilityStatusEnum.RULE_NOT_VERIFIED: 5,
    }

    matched_items.sort(key=lambda x: status_priority.get(x.eligibility_status, 99))
    return matched_items
