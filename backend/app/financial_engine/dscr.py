"""
Debt Service Coverage Ratio (DSCR) Calculation Module.
Deterministic, explainable coverage calculation with CFADS breakdown
and standard illustrative risk bands.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple

from app.financial_engine.schemas import (
    DSCRCalculationRequest, DSCRCalculationResponse, DSCRThresholdBand
)

TWO_PLACES = Decimal("0.01")
THREE_PLACES = Decimal("0.001")

ILLUSTRATIVE_THRESHOLDS: List[DSCRThresholdBand] = [
    DSCRThresholdBand(tier="INSUFFICIENT", label_uz="Yetarsiz qoplash (DSCR < 1.0x)", min_value=None, max_value=Decimal("1.00")),
    DSCRThresholdBand(tier="LIMITED", label_uz="Cheklangan qoplash (1.0x <= DSCR < 1.2x)", min_value=Decimal("1.00"), max_value=Decimal("1.20")),
    DSCRThresholdBand(tier="MODERATE", label_uz="Mo'tadil qoplash (1.2x <= DSCR < 1.5x)", min_value=Decimal("1.20"), max_value=Decimal("1.50")),
    DSCRThresholdBand(tier="STRONG", label_uz="Barqaror va mustahkam qoplash (DSCR >= 1.5x)", min_value=Decimal("1.50"), max_value=None),
]

def round_money(val: Decimal) -> Decimal:
    return val.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def round_ratio(val: Decimal) -> Decimal:
    return val.quantize(THREE_PLACES, rounding=ROUND_HALF_UP)

def calculate_dscr(req: DSCRCalculationRequest) -> DSCRCalculationResponse:
    """
    Calculates explainable DSCR:
    CFADS = Operating Cash Inflows - Operating Cash Outflows
    Total Debt Service = Principal Payments + Interest Payments
    DSCR = CFADS / Total Debt Service
    """
    cfads = round_money(req.operating_cash_inflows - req.operating_cash_outflows)
    total_debt_service = round_money(req.debt_service_principal + req.debt_service_interest)

    if total_debt_service == Decimal("0.00"):
        return DSCRCalculationResponse(
            operating_cash_inflows=round_money(req.operating_cash_inflows),
            operating_cash_outflows=round_money(req.operating_cash_outflows),
            cfads=cfads,
            total_debt_service=Decimal("0.00"),
            dscr=None,
            has_debt=False,
            status_tier="NO_DEBT",
            status_label_uz="Qarz majburiyati yo'q",
            interpretation_uz="Tanlangan davrda qarz to'lovlari mavjud emas. Korxona o'z mablag'lari hisobiga ishlamoqda.",
            is_acceptable=True,
            thresholds_applied=ILLUSTRATIVE_THRESHOLDS,
            calculation_version="2.0.0"
        )

    # Compute DSCR ratio
    dscr_val = round_ratio(cfads / total_debt_service)

    if cfads <= Decimal("0.00"):
        tier = "INSUFFICIENT"
        label_uz = "Kritik yetarsiz (Manfiy yoki nol operatsion pul oqimi)"
        interpretation_uz = (
            f"Operatsion kassa oqimi manfiy ({cfads} UZS). Korxona asosiy faoliyatidan "
            f"qarzga xizmat ko'rsatish ({total_debt_service} UZS) uchun yetarli mablag' ishlab topmayapti."
        )
        is_acceptable = False
    elif dscr_val < Decimal("1.000"):
        tier = "INSUFFICIENT"
        label_uz = "Yetarsiz qoplash (DSCR < 1.0x)"
        interpretation_uz = (
            f"Kassa oqimi qarz to'lovlarining atigi {round_money(dscr_val * Decimal('100'))}% qismini qoplaydi. "
            f"Kassa uzilishi va defolt xatari yuqori."
        )
        is_acceptable = False
    elif dscr_val < Decimal("1.200"):
        tier = "LIMITED"
        label_uz = "Cheklangan / Xatarli qoplash (1.0x - 1.2x)"
        interpretation_uz = (
            f"DSCR {dscr_val}x — qarz to'lovlari zo'rg'a qoplanmoqda. Daromad biroz pasaysa yoki kutilmagan "
            f"xarajat chiqsa, likvidlik yetishmovchiligi yuzaga keladi."
        )
        is_acceptable = False
    elif dscr_val < Decimal("1.500"):
        tier = "MODERATE"
        label_uz = "Mo'tadil qoplash (1.2x - 1.5x)"
        interpretation_uz = (
            f"DSCR {dscr_val}x — qarzga xizmat ko'rsatish qobiliyati qoniqarli. Banklarning 1.25x lik "
            f"tavsiyaviy anderrayting talablariga mos keladi."
        )
        is_acceptable = True
    else:
        tier = "STRONG"
        label_uz = "Mustahkam va yuqori qoplash (DSCR >= 1.5x)"
        interpretation_uz = (
            f"DSCR {dscr_val}x — korxona operatsion kassa oqimi qarz to'lovlaridan ancha yuqori. "
            f"Qo'shimcha kredit jalb qilish va investitsion salohiyat mavjud."
        )
        is_acceptable = True

    return DSCRCalculationResponse(
        operating_cash_inflows=round_money(req.operating_cash_inflows),
        operating_cash_outflows=round_money(req.operating_cash_outflows),
        cfads=cfads,
        total_debt_service=total_debt_service,
        dscr=dscr_val,
        has_debt=True,
        status_tier=tier,
        status_label_uz=label_uz,
        interpretation_uz=interpretation_uz,
        is_acceptable=is_acceptable,
        thresholds_applied=ILLUSTRATIVE_THRESHOLDS,
        calculation_version="2.0.0"
    )
