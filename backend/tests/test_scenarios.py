import copy
import pytest
from app.services.synthetic_data import SCENARIOS_MAP, SCENARIO_METAS, get_scenario_by_id
from app.services.financial_engine import FinancialEngine

def test_three_synthetic_scenarios_exist_and_labeled():
    """Confirms all 3 required synthetic scenarios are registered and labeled as synthetic."""
    assert len(SCENARIO_METAS) == 3
    keys = {s.key for s in SCENARIO_METAS}
    assert "small_farmer" in keys
    assert "exporter" in keys
    assert "cluster" in keys

    for s in SCENARIO_METAS:
        assert s.is_synthetic is True
        assert s.hectares > 0
        assert s.initial_cash_uzs > 0
        assert s.annual_revenue_estimate_uzs > 0

def test_all_scenarios_internal_consistency():
    """
    Validates that each of the 3 synthetic agribusiness scenarios
    passes full mathematical reconciliation without any discrepancies.
    """
    for scenario_id, data in SCENARIOS_MAP.items():
        assert len(data["monthly_inflows"]) == 12
        assert len(data["monthly_outflows"]) == 12
        assert len(data["monthly_debt_service"]) == 12

        summary = FinancialEngine.calculate_12m_cash_flow(
            initial_opening_balance=data["initial_opening_balance"],
            monthly_inflows_raw=copy.deepcopy(data["monthly_inflows"]),
            monthly_outflows_raw=copy.deepcopy(data["monthly_outflows"]),
            monthly_debt_service=list(data["monthly_debt_service"]),
            org_id=data["organization"]["id"],
            org_name=data["organization"]["name"]
        )

        assert summary.is_mathematically_reconciled is True, f"Scenario {scenario_id} failed reconciliation!"
        assert summary.total_annual_inflows > 0
        assert summary.total_annual_outflows > 0

        # Roll-forward check across all 12 periods
        for i in range(1, 12):
            assert summary.monthly_data[i].opening_balance == summary.monthly_data[i - 1].closing_balance

def test_small_farmer_seasonality_and_deficit_detection():
    """Small farmer should exhibit spring cash flow tightness (April/May) due to planting expenses."""
    farmer = get_scenario_by_id("scenario-small-farmer")
    summary = FinancialEngine.calculate_12m_cash_flow(
        initial_opening_balance=farmer["initial_opening_balance"],
        monthly_inflows_raw=copy.deepcopy(farmer["monthly_inflows"]),
        monthly_outflows_raw=copy.deepcopy(farmer["monthly_outflows"]),
        monthly_debt_service=list(farmer["monthly_debt_service"])
    )

    # In April or May, net cash flow is negative due to planting expenses without harvest
    apr = summary.monthly_data[3]
    may = summary.monthly_data[4]
    assert apr.net_cash_flow < 0
    assert may.net_cash_flow < 0
