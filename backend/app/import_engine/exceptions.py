"""
AgroHisob CFO - Smart Import Engine Custom Exceptions
Provides granular, domain-specific exception types for financial data ingestion.
"""

class ImportEngineError(Exception):
    """Base exception for all import engine errors."""
    def __init__(self, message: str, code: str = "IMPORT_ERROR", details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class FileValidationError(ImportEngineError):
    """Raised when file validation (size, extension, mime, security) fails."""
    def __init__(self, message: str, code: str = "FILE_VALIDATION_ERROR", details: dict | None = None):
        super().__init__(message, code=code, details=details)


class UnsupportedFormatError(FileValidationError):
    """Raised when the uploaded file extension or mime type is not supported."""
    def __init__(self, message: str = "Fayl formati qo'llab-quvvatlanmaydi. Faqat .csv va .xlsx formatlari qabul qilinadi."):
        super().__init__(message, code="UNSUPPORTED_FORMAT")


class FileSizeLimitExceededError(FileValidationError):
    """Raised when the uploaded file exceeds size limits (e.g., 10MB)."""
    def __init__(self, message: str = "Fayl hajmi ruxsat etilgan maksimal chegaradan (10MB) oshib ketdi."):
        super().__init__(message, code="FILE_SIZE_LIMIT_EXCEEDED")


class CorruptedFileError(FileValidationError):
    """Raised when a file cannot be parsed or read due to corruption or encoding issues."""
    def __init__(self, message: str = "Fayl shikastlangan yoki uni o'qib bo'lmadi."):
        super().__init__(message, code="CORRUPTED_FILE")


class DuplicateFileError(ImportEngineError):
    """Raised when a file with identical SHA-256 hash was already imported."""
    def __init__(self, message: str = "Ushbu fayl avval to'liq import qilingan (takroriy fayl aniqlandi).", file_hash: str | None = None):
        super().__init__(message, code="DUPLICATE_FILE", details={"sha256": file_hash})


class UnmappedColumnError(ImportEngineError):
    """Raised when mandatory columns cannot be mapped from source spreadsheet."""
    def __init__(self, message: str = "Majburiy ustunlar aniqlanmadi yoki moslashtirilmadi.", missing_columns: list[str] | None = None):
        super().__init__(message, code="UNMAPPED_COLUMN", details={"missing_columns": missing_columns or []})


class InvalidRowError(ImportEngineError):
    """Raised when row normalization or validation encounters critical issues."""
    def __init__(self, message: str, row_index: int, field_name: str | None = None):
        super().__init__(message, code="INVALID_ROW", details={"row_index": row_index, "field": field_name})


class LedgerSeparationViolationError(ImportEngineError):
    """Raised when an invoice document attempts to directly alter cash balances."""
    def __init__(self, message: str = "Invoys hujjatlari (E-faktura) to'g'ridan-to'g'ri kassa/bank qoldig'iga kiritilishi taqiqlangan."):
        super().__init__(message, code="LEDGER_SEPARATION_VIOLATION")
