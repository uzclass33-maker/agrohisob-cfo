import copy
from typing import Dict, Any, List
from app.services.financial_engine import FinancialEngine
from app.models.schemas import StressTestRequest, StressTestResponse, MonthlyFinancialData

class ScenarioEngine:
    """
    Stress-testing and sensitivity simulation engine for agricultural portfolios.
    Models biological and climatic yield shocks, commodity price fluctuations,
    input cost inflations, and credit rate changes.
    """

    @staticmethod
    def run_stress_test(
        base_scenario: Dict[str, Any],
        params: StressTestRequest
    ) -> StressTestResponse:
        org_info = base_scenario["organization"]
        init_balance = float(base_scenario["initial_opening_balance"])

        # Calculate baseline first
        base_summary = FinancialEngine.calculate_12m_cash_flow(
            initial_opening_balance=init_balance,
            monthly_inflows_raw=copy.deepcopy(base_scenario["monthly_inflows"]),
            monthly_outflows_raw=copy.deepcopy(base_scenario["monthly_outflows"]),
            monthly_debt_service=list(base_scenario["monthly_debt_service"]),
            org_id=org_info["id"],
            org_name=org_info["name"]
        )

        # Apply stress factors
        # Combined revenue shock factor: (1 + yield_shock) * (1 + price_shock)
        revenue_multiplier = (1.0 + (params.yield_shock_pct / 100.0)) * (1.0 + (params.price_shock_pct / 100.0))
        cost_multiplier = 1.0 + (params.cost_shock_pct / 100.0)

        stressed_inflows: List[Dict[str, float]] = []
        for m_inflow in base_scenario["monthly_inflows"]:
            stressed_m = {}
            for cat, amt in m_inflow.items():
                if cat in ("CROP_SALES", "EXPORT_PROCEEDS"):
                    stressed_m[cat] = max(0.0, amt * revenue_multiplier)
                else:
                    stressed_m[cat] = amt  # Subsidies or non-market inflows untouched
            stressed_inflows.append(stressed_m)

        stressed_outflows: List[Dict[str, float]] = []
        for m_outflow in base_scenario["monthly_outflows"]:
            stressed_m = {}
            for cat, amt in m_outflow.items():
                if cat.startswith("DEBT_SERVICE"):
                    stressed_m[cat] = amt  # Debt principal/interest governed separately
                else:
                    stressed_m[cat] = max(0.0, amt * cost_multiplier)
            stressed_outflows.append(stressed_m)

        # Handle debt service interest rate override if provided
        stressed_debt_service = list(base_scenario["monthly_debt_service"])
        if params.interest_rate_override is not None:
            # Scale monthly payment proportional to interest rate delta
            base_rate = base_scenario["debt_schedule"][0]["annual_interest_rate"]
            rate_ratio = (params.interest_rate_override / base_rate) if base_rate > 0 else 1.0
            stressed_debt_service = [round(pmt * rate_ratio, 2) for pmt in stressed_debt_service]
            for m_outflow in stressed_outflows:
                if "DEBT_SERVICE" in m_outflow:
                    m_outflow["DEBT_SERVICE"] = round(m_outflow["DEBT_SERVICE"] * rate_ratio, 2)

        stressed_summary = FinancialEngine.calculate_12m_cash_flow(
            initial_opening_balance=init_balance,
            monthly_inflows_raw=stressed_inflows,
            monthly_outflows_raw=stressed_outflows,
            monthly_debt_service=stressed_debt_service,
            org_id=org_info["id"],
            org_name=org_info["name"]
        )

        dscr_delta_pct = 0.0
        if base_summary.annual_dscr > 0:
            dscr_delta_pct = round(
                ((stressed_summary.annual_dscr - base_summary.annual_dscr) / base_summary.annual_dscr) * 100.0,
                2
            )

        # Solvency assessment under stress
        if stressed_summary.months_in_deficit == 0 and stressed_summary.annual_dscr >= 1.25:
            solvency = "RESILIENT (To'liq Bardoshli)"
        elif stressed_summary.annual_dscr >= 1.0:
            solvency = "VULNERABLE (Xatarli - Kassa uzilishi ehtimoli bor)"
        else:
            solvency = "INSOLVENT_UNDER_STRESS (Defolt Xatari - Qayta moliyalashtirish talab etiladi)"

        return StressTestResponse(
            scenario_id=params.scenario_id,
            scenario_name=org_info["name"],
            baseline_annual_inflow=base_summary.total_annual_inflows,
            baseline_annual_outflow=base_summary.total_annual_outflows,
            baseline_dscr=base_summary.annual_dscr,
            stressed_annual_inflow=stressed_summary.total_annual_inflows,
            stressed_annual_outflow=stressed_summary.total_annual_outflows,
            stressed_dscr=stressed_summary.annual_dscr,
            dscr_change_pct=dscr_delta_pct,
            deficit_months_baseline=base_summary.months_in_deficit,
            deficit_months_stressed=stressed_summary.months_in_deficit,
            minimum_cash_baseline=base_summary.lowest_cash_point,
            minimum_cash_stressed=stressed_summary.lowest_cash_point,
            solvency_status=solvency,
            stressed_monthly_data=stressed_summary.monthly_data
        )
