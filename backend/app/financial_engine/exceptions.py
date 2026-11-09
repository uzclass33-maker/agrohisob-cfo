"""
Exceptions for AgroHisob CFO Financial Calculation Engine.
Strict, explainable errors for financial invariants and parameter boundaries.
"""

class FinancialCalculationError(Exception):
    """Base exception for all financial calculation engine errors."""
    def __init__(self, message: str, code: str = "FINANCIAL_CALCULATION_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code

class InvalidLoanParametersError(FinancialCalculationError):
    """Raised when loan amortization parameters violate mathematical or financial rules."""
    def __init__(self, message: str):
        super().__init__(message, code="INVALID_LOAN_PARAMETERS")

class DivisionByZeroError(FinancialCalculationError):
    """Raised when a calculation would result in division by zero without a fallback."""
    def __init__(self, message: str):
        super().__init__(message, code="DIVISION_BY_ZERO")

class NegativePrincipalError(FinancialCalculationError):
    """Raised when principal amount is negative or invalid."""
    def __init__(self, message: str):
        super().__init__(message, code="NEGATIVE_PRINCIPAL")

class CurrencyMismatchError(FinancialCalculationError):
    """Raised when transactions of incompatible currencies are aggregated without exchange rate."""
    def __init__(self, message: str):
        super().__init__(message, code="CURRENCY_MISMATCH")
