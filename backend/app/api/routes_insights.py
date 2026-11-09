"""
AgroHisob CFO - AI-CFO Insights API Router
Provides structured, explainable financial insights and decision support
utilizing Layer A Deterministic Rule Engine and optional Layer B Privacy-First LLM explanation.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.financial_engine.schemas import AIInsightsResponse, FinancialInsight
from app.financial_engine.insights import InsightsEngine
from app.api.routes_dashboard import _build_forecast_request
from app.financial_engine import calculate_seasonal_forecast


router = APIRouter(prefix="/insights", tags=["AI-CFO Financial Insights (Assignment 4)"])


class InsightExplainRequest(BaseModel):
    organization_id: str = "scenario-small-farmer"
    insight_id: Optional[str] = None
    request_llm: bool = False


@router.get("", response_model=AIInsightsResponse)
@router.get("/", response_model=AIInsightsResponse)
def get_insights(
    organization_id: str = Query("scenario-small-farmer", description="Organization or Scenario ID"),
    request_llm: bool = Query(False, description="Whether to request optional LLM enrichment")
):
    """
    Retrieves evidence-based financial intelligence and structured insights
    derived authoritatively from the Financial Engine.
    """
    try:
        forecast_req = _build_forecast_request(organization_id, 2026)
        forecast_res = calculate_seasonal_forecast(forecast_req)
        return InsightsEngine.synthesize_insights(forecast_res, request_llm=request_llm)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI-CFO tahliliy xulosasini shakllantirishda xatolik: {str(e)}"
        )


@router.post("/explain", response_model=AIInsightsResponse)
def explain_insight(request: InsightExplainRequest):
    """
    Provides an expanded explanation for a specific insight or the entire organization portfolio.
    Enforces factual claim validation and zero-failure deterministic fallback.
    """
    try:
        forecast_req = _build_forecast_request(request.organization_id, 2026)
        forecast_res = calculate_seasonal_forecast(forecast_req)
        response = InsightsEngine.synthesize_insights(forecast_res, request_llm=request.request_llm)

        if request.insight_id:
            # Filter specifically to target insight
            matching = [i for i in response.insights if i.insight_id == request.insight_id]
            if matching:
                response.insights = matching

        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tushuntirish shakllantirishda xatolik: {str(e)}"
        )
