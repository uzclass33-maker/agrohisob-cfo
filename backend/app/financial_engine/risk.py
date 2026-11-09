"""
Liquidity Risk Detection Module.
Deterministic, explainable warnings for cash deficits, buffer breaches,
seasonal gaps, and debt repayment pressure.
"""

from decimal import Decimal
from typing import List, Dict, Optional
from app.financial_engine.schemas import LiquidityAlert, AlertSeverity

def detect_monthly_liquidity_risks(
    month_number: int,
    month_name: str,
    opening_balance: Decimal,
    inflows: Decimal,
    operating_outflows: Decimal,
    debt_service: Decimal,
    closing_balance: Decimal,
    min_buffer_uzs: Decimal = Decimal("10000000.00"),
    dscr: Optional[Decimal] = None
) -> List[LiquidityAlert]:
    """
    Evaluates financial conditions for a specific month and returns active deterministic warnings.
    """
    alerts: List[LiquidityAlert] = []
    total_outflows = operating_outflows + debt_service

    # 1. Negative Cash Balance Alert (CRITICAL)
    if closing_balance < Decimal("0.00"):
        deficit_amt = abs(closing_balance)
        alerts.append(
            LiquidityAlert(
                warning_type="NEGATIVE_CASH",
                severity=AlertSeverity.CRITICAL,
                affected_month=month_name,
                month_number=month_number,
                relevant_figures={
                    "closing_balance": closing_balance,
                    "deficit_amount": deficit_amt,
                    "total_outflows": total_outflows
                },
                rule_triggered="Closing Balance < 0.00 UZS",
                explanation_uz=(
                    f"{month_name} oyida kassa balansi manfiy ({closing_balance:,.2f} UZS) bo'lib qoladi. "
                    f"Korxonada to'lov qobiliyati yetishmovchiligi (defitsit) yuzaga kelmoqda."
                ),
                suggested_action_uz=(
                    f"Kamida {deficit_amt:,.2f} UZS miqdorida qisqa muddatli aylanma kredit yoki avans mablag'i "
                    f"jalb qilish, yoxud favqulodda xarajatlarni kechiktirish tavsiya etiladi."
                )
            )
        )
    # 2. Low Cash Buffer Alert (HIGH / MEDIUM)
    elif closing_balance < min_buffer_uzs:
        alerts.append(
            LiquidityAlert(
                warning_type="LOW_BUFFER",
                severity=AlertSeverity.HIGH if closing_balance < (min_buffer_uzs / Decimal("2")) else AlertSeverity.MEDIUM,
                affected_month=month_name,
                month_number=month_number,
                relevant_figures={
                    "closing_balance": closing_balance,
                    "min_buffer_threshold": min_buffer_uzs,
                    "buffer_shortfall": min_buffer_uzs - closing_balance
                },
                rule_triggered=f"0 <= Closing Balance < Min Buffer ({min_buffer_uzs:,.2f} UZS)",
                explanation_uz=(
                    f"{month_name} oyidagi kassa qoldig'i ({closing_balance:,.2f} UZS) xavfsiz minimal zaxira "
                    f"buferidan ({min_buffer_uzs:,.2f} UZS) pastga tushib ketadi."
                ),
                suggested_action_uz="Kutilmagan agro-iqlimiy yoki logistika xatarlari uchun zaxira fondini to'ldirish maqsadga muvofiq."
            )
        )

    # 3. Debt Service Pressure Alert
    if debt_service > Decimal("0.00"):
        if dscr is not None and dscr < Decimal("1.000"):
            alerts.append(
                LiquidityAlert(
                    warning_type="DEBT_SERVICE_PRESSURE",
                    severity=AlertSeverity.CRITICAL if dscr <= Decimal("0.500") else AlertSeverity.HIGH,
                    affected_month=month_name,
                    month_number=month_number,
                    relevant_figures={
                        "monthly_dscr": dscr,
                        "monthly_debt_service": debt_service,
                        "operating_inflows": inflows,
                        "operating_outflows": operating_outflows
                    },
                    rule_triggered="Monthly DSCR < 1.00x",
                    explanation_uz=(
                        f"{month_name} oyida operatsion kassa oqimi oylik qarz to'lovlarini ({debt_service:,.2f} UZS) "
                        f"to'liq qoplay olmaydi (DSCR = {dscr}x)."
                    ),
                    suggested_action_uz="Bank bilan qarz to'lovlarini mavsumiy hosil oylariga restrukturizatsiya qilish bo'yicha muzokara o'tkazish tavsiya etiladi."
                )
            )
        elif dscr is not None and dscr < Decimal("1.250"):
            alerts.append(
                LiquidityAlert(
                    warning_type="DEBT_SERVICE_PRESSURE",
                    severity=AlertSeverity.MEDIUM,
                    affected_month=month_name,
                    month_number=month_number,
                    relevant_figures={
                        "monthly_dscr": dscr,
                        "monthly_debt_service": debt_service
                    },
                    rule_triggered="1.00x <= Monthly DSCR < 1.25x",
                    explanation_uz=(
                        f"{month_name} oyida qarz to'lovlari kassa oqimiga nisbatan yuqori bosim o'tkazmoqda (DSCR = {dscr}x)."
                    ),
                    suggested_action_uz="Qarz to'lov muddatlarini nazorat qilish va xarajatlarni optimallashtirish tavsiya etiladi."
                )
            )

    # 4. Seasonal Cash Gap Alert
    if inflows == Decimal("0.00") and total_outflows > (opening_balance / Decimal("2")):
        alerts.append(
            LiquidityAlert(
                warning_type="SEASONAL_GAP",
                severity=AlertSeverity.MEDIUM,
                affected_month=month_name,
                month_number=month_number,
                relevant_figures={
                    "inflows": inflows,
                    "total_outflows": total_outflows,
                    "opening_balance": opening_balance
                },
                rule_triggered="Inflows == 0 and Outflows > 50% Opening Balance",
                explanation_uz=(
                    f"{month_name} oyida qishloq xo'jaligi mavsumiyligi sababli tushumlar nolga teng, xarajatlar esa "
                    f"boshlang'ich qoldiqning yarmidan ko'prog'ini sarflamoqda."
                ),
                suggested_action_uz="Mavsumiy ekish xarajatlarini bo'lib to'lash yoki yetkazib beruvchilar bilan kechiktirilgan to'lov shartlarini kelishish lozim."
            )
        )

    return alerts
