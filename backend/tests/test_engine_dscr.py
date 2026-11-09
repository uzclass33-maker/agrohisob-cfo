import pytest
from decimal import Decimal
from app.financial_engine.schemas import DSCRCalculationRequest
from app.financial_engine.dscr import calculate_dscr

def test_dscr_strong_coverage():
    """CFADS 30M, Debt Service 15M -> DSCR = 2.0x (STRONG)."""
    req = DSCRCalculationRequest(
        operating_cash_inflows=Decimal("50000000.00"),
        operating_cash_outflows=Decimal("20000000.00"),
        debt_service_principal=Decimal("10000000.00"),
        debt_service_interest=Decimal("5000000.00")
    )
    res = calculate_dscr(req)
    assert res.cfads == Decimal("30000000.00")
    assert res.total_debt_service == Decimal("15000000.00")
    assert res.dscr == Decimal("2.000")
    assert res.status_tier == "STRONG"
    assert res.is_acceptable is True

def test_dscr_moderate_coverage():
    """CFADS 13M, Debt Service 10M -> DSCR = 1.300x (MODERATE)."""
    req = DSCRCalculationRequest(
        operating_cash_inflows=Decimal("25000000.00"),
        operating_cash_outflows=Decimal("12000000.00"),
        debt_service_principal=Decimal("8000000.00"),
        debt_service_interest=Decimal("2000000.00")
    )
    res = calculate_dscr(req)
    assert res.dscr == Decimal("1.300")
    assert res.status_tier == "MODERATE"
    assert res.is_acceptable is True

def test_dscr_limited_coverage():
    """CFADS 11M, Debt Service 10M -> DSCR = 1.100x (LIMITED)."""
    req = DSCRCalculationRequest(
        operating_cash_inflows=Decimal("20000000.00"),
        operating_cash_outflows=Decimal("9000000.00"),
        debt_service_principal=Decimal("8000000.00"),
        debt_service_interest=Decimal("2000000.00")
    )
    res = calculate_dscr(req)
    assert res.dscr == Decimal("1.100")
    assert res.status_tier == "LIMITED"
    assert res.is_acceptable is False

def test_dscr_insufficient_coverage():
    """CFADS 8M, Debt Service 10M -> DSCR = 0.800x (INSUFFICIENT)."""
    req = DSCRCalculationRequest(
        operating_cash_inflows=Decimal("20000000.00"),
        operating_cash_outflows=Decimal("12000000.00"),
        debt_service_principal=Decimal("8000000.00"),
        debt_service_interest=Decimal("2000000.00")
    )
    res = calculate_dscr(req)
    assert res.dscr == Decimal("0.800")
    assert res.status_tier == "INSUFFICIENT"
    assert res.is_acceptable is False

def test_dscr_zero_debt_service():
    """Debt Service is 0.00 -> Should return has_debt=False and dscr=None, avoiding ZeroDivisionError."""
    req = DSCRCalculationRequest(
        operating_cash_inflows=Decimal("15000000.00"),
        operating_cash_outflows=Decimal("5000000.00"),
        debt_service_principal=Decimal("0.00"),
        debt_service_interest=Decimal("0.00")
    )
    res = calculate_dscr(req)
    assert res.has_debt is False
    assert res.dscr is None
    assert res.status_tier == "NO_DEBT"
    assert res.is_acceptable is True

def test_dscr_negative_cfads():
    """Operating Outflows exceed Inflows -> CFADS < 0 -> DSCR is negative, is_acceptable = False."""
    req = DSCRCalculationRequest(
        operating_cash_inflows=Decimal("10000000.00"),
        operating_cash_outflows=Decimal("15000000.00"),
        debt_service_principal=Decimal("5000000.00"),
        debt_service_interest=Decimal("1000000.00")
    )
    res = calculate_dscr(req)
    assert res.cfads == Decimal("-5000000.00")
    assert res.status_tier == "INSUFFICIENT"
    assert res.is_acceptable is False
