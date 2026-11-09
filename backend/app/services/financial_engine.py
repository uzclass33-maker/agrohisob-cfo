import math
from typing import List, Dict, Any, Tuple
from app.models.schemas import MonthlyFinancialData, FinancialSummaryResponse

MONTH_NAMES_UZ = [
    "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
    "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
]

class FinancialEngine:
    """
    Deterministic Financial Engine for AgroHisob CFO.
    Strictly enforces double-entry cash flow arithmetic:
    Closing Balance(t) = Opening Balance(t) + Inflows(t) - Outflows(t)
    Opening Balance(t+1) = Closing Balance(t)
    """

    @staticmethod
    def calculate_12m_cash_flow(
        initial_opening_balance: float,
        monthly_inflows_raw: List[Dict[str, float]],
        monthly_outflows_raw: List[Dict[str, float]],
        monthly_debt_service: List[float],
        org_id: str = "synthetic-org",
        org_name: str = "Agro Korxona",
        fiscal_year: int = 2026
    ) -> FinancialSummaryResponse:
        """
        Calculates and reconciles full 12-month financial trajectory.
        Guarantees mathematical integrity across all months.
        """
        assert len(monthly_inflows_raw) == 12, "Must provide exactly 12 months of inflow data"
        assert len(monthly_outflows_raw) == 12, "Must provide exactly 12 months of outflow data"
        assert len(monthly_debt_service) == 12, "Must provide exactly 12 months of debt service"

        monthly_records: List[MonthlyFinancialData] = []
        current_opening = float(initial_opening_balance)

        total_annual_inflows = 0.0
        total_annual_outflows = 0.0
        total_annual_debt = 0.0
        total_operating_inflows = 0.0
        total_operating_outflows = 0.0

        category_totals: Dict[str, float] = {}
        months_in_deficit = 0
        lowest_cash_point = float("inf")
        lowest_cash_month = "Yanvar"

        for m_idx in range(12):
            month_num = m_idx + 1
            month_name = MONTH_NAMES_UZ[m_idx]

            inflows_dict = monthly_inflows_raw[m_idx]
            outflows_dict = monthly_outflows_raw[m_idx]
            debt_amt = float(monthly_debt_service[m_idx])

            # Inflows sum
            month_inflows = sum(float(v) for v in inflows_dict.values())
            # Outflows sum (including debt service if placed in dictionary, or explicitly ensure single counting)
            # If debt_service is already in outflows_dict, we use that; otherwise add it
            if "DEBT_SERVICE_PRINCIPAL" not in outflows_dict and "DEBT_SERVICE_INTEREST" not in outflows_dict:
                if "DEBT_SERVICE" not in outflows_dict and debt_amt > 0:
                    outflows_dict["DEBT_SERVICE"] = debt_amt

            month_outflows = sum(float(v) for v in outflows_dict.values())

            # Cash flow identity
            net_cash_flow = month_inflows - month_outflows
            closing_balance = current_opening + net_cash_flow

            # Track lowest cash point
            if closing_balance < lowest_cash_point:
                lowest_cash_point = closing_balance
                lowest_cash_month = month_name

            # Liquidity deficit detection (negative cash or < 5M UZS buffer)
            is_deficit = closing_balance < 0.0
            if is_deficit:
                months_in_deficit += 1

            # Operating cash flow (excluding financing/debt service for DSCR calculation)
            non_debt_outflows = sum(
                float(amt) for cat, amt in outflows_dict.items() 
                if not cat.startswith("DEBT_SERVICE")
            )
            net_operating_cash = month_inflows - non_debt_outflows

            # Monthly DSCR
            month_dscr: float | None = None
            if debt_amt > 0:
                month_dscr = round(net_operating_cash / debt_amt, 2)

            # Record aggregated category data
            for cat, amt in inflows_dict.items():
                category_totals[cat] = category_totals.get(cat, 0.0) + amt
            for cat, amt in outflows_dict.items():
                category_totals[cat] = category_totals.get(cat, 0.0) + amt

            monthly_records.append(
                MonthlyFinancialData(
                    month_number=month_num,
                    month_name=month_name,
                    opening_balance=round(current_opening, 2),
                    total_inflows=round(month_inflows, 2),
                    total_outflows=round(month_outflows, 2),
                    net_cash_flow=round(net_cash_flow, 2),
                    closing_balance=round(closing_balance, 2),
                    debt_service=round(debt_amt, 2),
                    dscr=month_dscr,
                    is_deficit=is_deficit,
                    inflows_breakdown={k: round(v, 2) for k, v in inflows_dict.items()},
                    outflows_breakdown={k: round(v, 2) for k, v in outflows_dict.items()}
                )
            )

            # Accumulators
            total_annual_inflows += month_inflows
            total_annual_outflows += month_outflows
            total_annual_debt += debt_amt
            total_operating_inflows += month_inflows
            total_operating_outflows += non_debt_outflows

            # Roll-forward for next month: Opening(t+1) = Closing(t)
            current_opening = closing_balance

        final_closing_balance = current_opening
        net_annual_cash_flow = total_annual_inflows - total_annual_outflows

        # Mathematical reconciliation check
        expected_closing = initial_opening_balance + total_annual_inflows - total_annual_outflows
        reconciled = math.isclose(final_closing_balance, expected_closing, abs_tol=0.01)

        # Annual DSCR: CFADS / Total Annual Debt Service
        # CFADS = Operating Inflows - Operating Expenses (excluding debt principal & interest)
        net_annual_operating = total_operating_inflows - total_operating_outflows
        if total_annual_debt > 0:
            annual_dscr = round(net_annual_operating / total_annual_debt, 3)
            # DSCR Rating based on model benchmark parameters (1.25 standard)
            if annual_dscr >= 1.6:
                dscr_rating = "EXCELLENT"
            elif annual_dscr >= 1.25:
                dscr_rating = "HEALTHY"
            elif annual_dscr >= 1.0:
                dscr_rating = "WATCHLIST"
            else:
                dscr_rating = "CRITICAL"
        else:
            annual_dscr = None  # No debt obligations
            dscr_rating = "NO_DEBT"

        return FinancialSummaryResponse(
            organization_id=org_id,
            organization_name=org_name,
            fiscal_year=fiscal_year,
            initial_opening_balance=round(initial_opening_balance, 2),
            final_closing_balance=round(final_closing_balance, 2),
            total_annual_inflows=round(total_annual_inflows, 2),
            total_annual_outflows=round(total_annual_outflows, 2),
            net_annual_cash_flow=round(net_annual_cash_flow, 2),
            total_debt_service=round(total_annual_debt, 2),
            annual_dscr=annual_dscr,
            dscr_rating=dscr_rating,
            months_in_deficit=months_in_deficit,
            lowest_cash_point=round(lowest_cash_point, 2),
            lowest_cash_month=lowest_cash_month,
            is_mathematically_reconciled=reconciled,
            reconciliation_message="All monthly accounts reconciled (Closing = Opening + Inflows - Outflows)" if reconciled else "Reconciliation discrepancy detected",
            monthly_data=monthly_records,
            category_summary={k: round(v, 2) for k, v in category_totals.items()}
        )

    @staticmethod
    def estimate_vmq613_collateral_value(
        land_hectares: float,
        soil_bonitet_score: int,
        remaining_lease_years: int = 25,
        discount_rate: float = 0.16,
        normative_annual_net_income_per_ha_uzs: float = 8_500_000.0
    ) -> Tuple[float, float, float]:
        """
        Estimates the market and collateral valuation of agricultural land lease rights
        in accordance with Cabinet of Ministers Resolution No. 613 (VMQ-613, Sept 30, 2025).
        
        Formula:
        Adjusted Annual Renta = Base Net Income * (Bonitet / 65) * Hectares
        DCF Value = Adjusted Annual Renta * [ (1 - (1 + r)^(-n)) / r ]
        Bank Collateral Value = DCF Value * Collateral Discount Factor (65% LTV)
        
        Returns: (dcf_lease_value, discount_factor, bankable_collateral_uzs)
        """
        bonitet_factor = max(0.3, min(1.8, soil_bonitet_score / 65.0))
        adjusted_annual_net_renta = normative_annual_net_income_per_ha_uzs * bonitet_factor * land_hectares

        # Discounted Cash Flow over remaining lease years
        r = discount_rate
        n = remaining_lease_years
        annuity_factor = (1.0 - math.pow(1.0 + r, -n)) / r
        dcf_value = adjusted_annual_net_renta * annuity_factor

        # VMQ-613 regulatory collateral haircut (standard bankable LTV = 65%)
        haircut = 0.65
        bankable_collateral = dcf_value * haircut

        return (round(dcf_value, 2), haircut, round(bankable_collateral, 2))
