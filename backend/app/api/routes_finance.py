from fastapi import APIRouter, HTTPException, status
from app.financial_engine.schemas import (
    CashFlowAnalysisRequest, CashFlowAnalysisResponse,
    LoanScheduleRequest, LoanScheduleResponse,
    DSCRCalculationRequest, DSCRCalculationResponse,
    SeasonalForecastRequest, SeasonalForecastResponse,
    ScenarioAnalysisRequest, ScenarioComparisonResponse
)
from app.financial_engine.exceptions import (
    FinancialCalculationError, InvalidLoanParametersError,
    NegativePrincipalError, CurrencyMismatchError
)
from app.financial_engine import (
    process_historical_cashflow,
    calculate_loan_schedule,
    calculate_dscr,
    calculate_seasonal_forecast,
    run_scenario_analysis
)

router = APIRouter(prefix="/finance", tags=["Financial Calculation Engine (Assignment 2)"])

@router.post("/cashflow/analyze", response_model=CashFlowAnalysisResponse)
def analyze_cashflow_endpoint(request: CashFlowAnalysisRequest):
    """
    Analyzes historical cash transactions and computes 12-month roll-forward cash flow.
    Enforces Closing(t) = Opening(t) + Inflows(t) - Outflows(t).
    """
    try:
        return process_historical_cashflow(request)
    except CurrencyMismatchError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except FinancialCalculationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Kassa hisob-kitobida kutilmagan xatolik: {str(e)}")

@router.post("/forecast", response_model=SeasonalForecastResponse)
def generate_seasonal_forecast_endpoint(request: SeasonalForecastRequest):
    """
    Computes a forward-looking 12-month agricultural cash-flow projection
    incorporating harvest schedules, collection delays, and input seasonality.
    """
    try:
        return calculate_seasonal_forecast(request)
    except FinancialCalculationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Prognoz hisob-kitobida kutilmagan xatolik: {str(e)}")

@router.post("/loans/schedule", response_model=LoanScheduleResponse)
def calculate_loan_schedule_endpoint(request: LoanScheduleRequest):
    """
    Computes loan repayment schedule (Annuity or Equal Principal)
    with exact zero remaining principal reconciliation.
    """
    try:
        return calculate_loan_schedule(request)
    except (InvalidLoanParametersError, NegativePrincipalError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except FinancialCalculationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Kredit jadvalini hisoblashda kutilmagan xatolik: {str(e)}")

@router.post("/dscr/calculate", response_model=DSCRCalculationResponse)
def calculate_dscr_endpoint(request: DSCRCalculationRequest):
    """
    Calculates explainable Debt Service Coverage Ratio (DSCR)
    based on Cash Flow Available for Debt Service (CFADS).
    """
    try:
        return calculate_dscr(request)
    except FinancialCalculationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DSCR hisob-kitobida kutilmagan xatolik: {str(e)}")

@router.post("/scenarios/analyze", response_model=ScenarioComparisonResponse)
def analyze_scenarios_endpoint(request: ScenarioAnalysisRequest):
    """
    Performs scenario and sensitivity analysis by completely recalculating
    underlying cash flows under Base, Optimistic, Pessimistic, or Custom adjustments.
    """
    try:
        return run_scenario_analysis(request)
    except FinancialCalculationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ssenariylarni tahlil qilishda kutilmagan xatolik: {str(e)}")
