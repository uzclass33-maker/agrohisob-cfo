import pytest
from decimal import Decimal
from app.financial_engine.risk import detect_monthly_liquidity_risks

def test_negative_cash_risk_trigger():
    """Detects critical alert when closing balance is below 0."""
    alerts = detect_monthly_liquidity_risks(
        month_number=4,
        month_name="Aprel",
        opening_balance=Decimal("5000000.00"),
        inflows=Decimal("0.00"),
        operating_outflows=Decimal("15000000.00"),
        debt_service=Decimal("2000000.00"),
        closing_balance=Decimal("-12000000.00"),
        min_buffer_uzs=Decimal("10000000.00")
    )
    assert len(alerts) >= 1
    crit_alert = next((a for a in alerts if a.warning_type == "NEGATIVE_CASH"), None)
    assert crit_alert is not None
    assert crit_alert.severity == "CRITICAL"
    assert crit_alert.relevant_figures["deficit_amount"] == Decimal("12000000.00")
    assert "Aprel" in crit_alert.explanation_uz

def test_low_buffer_risk_trigger():
    """Detects low buffer alert when closing balance is positive but below 10M buffer."""
    alerts = detect_monthly_liquidity_risks(
        month_number=5,
        month_name="May",
        opening_balance=Decimal("20000000.00"),
        inflows=Decimal("0.00"),
        operating_outflows=Decimal("16000000.00"),
        debt_service=Decimal("0.00"),
        closing_balance=Decimal("4000000.00"), # below 10M buffer
        min_buffer_uzs=Decimal("10000000.00")
    )
    buf_alert = next((a for a in alerts if a.warning_type == "LOW_BUFFER"), None)
    assert buf_alert is not None
    assert buf_alert.severity in ["HIGH", "MEDIUM"]
    assert "buferidan" in buf_alert.explanation_uz

def test_debt_service_pressure_trigger():
    """Detects debt service pressure when DSCR is below 1.0."""
    alerts = detect_monthly_liquidity_risks(
        month_number=6,
        month_name="Iyun",
        opening_balance=Decimal("50000000.00"),
        inflows=Decimal("15000000.00"),
        operating_outflows=Decimal("10000000.00"), # CFADS = 5M
        debt_service=Decimal("10000000.00"), # DSCR = 0.5x
        closing_balance=Decimal("45000000.00"),
        min_buffer_uzs=Decimal("10000000.00"),
        dscr=Decimal("0.500")
    )
    debt_alert = next((a for a in alerts if a.warning_type == "DEBT_SERVICE_PRESSURE"), None)
    assert debt_alert is not None
    assert debt_alert.severity in ["CRITICAL", "HIGH"]
    assert "DSCR = 0.500x" in debt_alert.explanation_uz

def test_healthy_conditions_no_false_alerts():
    """Verifies that no false warnings are generated when cash is high and DSCR >= 1.5."""
    alerts = detect_monthly_liquidity_risks(
        month_number=10,
        month_name="Oktabr",
        opening_balance=Decimal("100000000.00"),
        inflows=Decimal("250000000.00"),
        operating_outflows=Decimal("50000000.00"),
        debt_service=Decimal("20000000.00"),
        closing_balance=Decimal("280000000.00"),
        min_buffer_uzs=Decimal("10000000.00"),
        dscr=Decimal("10.000")
    )
    assert len(alerts) == 0
