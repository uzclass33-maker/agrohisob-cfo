"""
Unit tests for FileValidator in AgroHisob CFO Smart Import Engine.
"""

import io
import pytest
import zipfile
from app.import_engine.file_validator import FileValidator, MAX_ALLOWED_FILE_SIZE_BYTES
from app.import_engine.exceptions import (
    FileValidationError,
    FileSizeLimitExceededError,
    UnsupportedFormatError,
    CorruptedFileError,
)


def test_valid_csv_validation():
    content = b"Sana,Summa,Kontragent\n2026-03-12,5000000,Agro MChJ"
    res = FileValidator.validate("test_statement.csv", content)
    assert res.is_valid is True
    assert res.extension == ".csv"
    assert len(res.sha256_hash) == 64
    assert res.detected_encoding == "utf-8"


def test_valid_xlsx_validation():
    # Construct a minimal valid zip file representing an xlsx
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types></Types>")
        zf.writestr("xl/workbook.xml", "<workbook></workbook>")
    content = buf.getvalue()

    res = FileValidator.validate("test_invoice.xlsx", content)
    assert res.is_valid is True
    assert res.extension == ".xlsx"
    assert res.detected_encoding == "binary"


def test_unsupported_extension_rejected():
    content = b"PDF dummy content"
    with pytest.raises(UnsupportedFormatError):
        FileValidator.validate("statement.pdf", content)

    with pytest.raises(UnsupportedFormatError):
        FileValidator.validate("malware.exe", content)


def test_empty_file_rejected():
    with pytest.raises(FileValidationError) as exc_info:
        FileValidator.validate("empty.csv", b"")
    assert "bo'sh" in str(exc_info.value)


def test_file_size_limit_exceeded():
    huge_content = b"A" * (MAX_ALLOWED_FILE_SIZE_BYTES + 1024)
    with pytest.raises(FileSizeLimitExceededError):
        FileValidator.validate("huge.csv", huge_content)


def test_corrupted_xlsx_header():
    # Invalid magic bytes for xlsx
    content = b"NOT_A_ZIP_CONTAINER_EXCEL"
    with pytest.raises(CorruptedFileError):
        FileValidator.validate("corrupted.xlsx", content)


def test_macro_payload_rejection():
    # Valid zip but contains vbaProject.bin (macro payload)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("xl/vbaProject.bin", b"VBA_PAYLOAD_DUMMY")
    content = buf.getvalue()

    with pytest.raises(FileValidationError) as exc_info:
        FileValidator.validate("macro_enabled.xlsx", content)
    assert "makros" in str(exc_info.value).lower()
