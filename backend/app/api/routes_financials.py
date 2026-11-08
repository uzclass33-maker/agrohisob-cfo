import copy
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    FinancialCalculationRequest, FinancialSummaryResponse,
    StressTestRequest, StressTestResponse
)
from app.services.financial_engine import FinancialEngine
from app.services.scenario_engine import ScenarioEngine
from app.services.synthetic_data import get_scenario_by_id

router = APIRouter(prefix="/financials", tags=["Financial Engine"])

@router.post("/calculate", response_model=FinancialSummaryResponse)
def calculate_financials(req: FinancialCalculationRequest):
    """
    Executes real deterministic 12-month cash flow calculations.
    Ensures closing balance = opening balance + inflows - outflows across all 12 periods.
    """
    if req.scenario_id:
        try:
            scenario = get_scenario_by_id(req.scenario_id)
            org_info = scenario["organization"]
            
            # Use requested initial opening balance if provided, otherwise default to scenario base
            init_balance = req.initial_opening_balance if req.initial_opening_balance > 0 else scenario["initial_opening_balance"]
            
            inflows = copy.deepcopy(scenario["monthly_inflows"])
            outflows = copy.deepcopy(scenario["monthly_outflows"])
            debt = list(scenario["monthly_debt_service"])

            return FinancialEngine.calculate_12m_cash_flow(
                initial_opening_balance=init_balance,
                monthly_inflows_raw=inflows,
                monthly_outflows_raw=outflows,
                monthly_debt_service=debt,
                org_id=org_info["id"],
                org_name=org_info["name"]
            )
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail=f"Ssenariy topilmadi: {req.scenario_id}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Moliyaviy hisob-kitobda xatolik yuz berdi: {str(e)}"
            )

    # If raw monthly transactions provided
    if req.monthly_overrides and len(req.monthly_overrides) == 12:
        inflows = [m.get("inflows", {}) for m in req.monthly_overrides]
        outflows = [m.get("outflows", {}) for m in req.monthly_overrides]
        debt = [m.get("debt_service", 0.0) for m in req.monthly_overrides]

        return FinancialEngine.calculate_12m_cash_flow(
            initial_opening_balance=req.initial_opening_balance,
            monthly_inflows_raw=inflows,
            monthly_outflows_raw=outflows,
            monthly_debt_service=debt,
            org_id="custom-input",
            org_name="Maxsus Fermer Korxonasi"
        )

    raise HTTPException(
        status_code=422,
        detail="Iltimos, mavjud 'scenario_id' ni tanlang yoki to'liq 12 oylik ma'lumotlar to'plamini taqdim eting."
    )

@router.post("/stress-test", response_model=StressTestResponse)
def run_scenario_stress_test(req: StressTestRequest):
    """
    Runs stress-testing and sensitivity simulation on a business scenario.
    """
    try:
        scenario = get_scenario_by_id(req.scenario_id)
        return ScenarioEngine.run_stress_test(scenario, req)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Ssenariy topilmadi: {req.scenario_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Stress-test tahlilida xatolik yuz berdi: {str(e)}"
        )
