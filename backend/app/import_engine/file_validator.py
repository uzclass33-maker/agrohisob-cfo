"""
AgroHisob CFO - File Security & Format Validator
Validates incoming file streams for size, magic bytes, encoding, macro hazards, and computes cryptographic hashes.
"""

import hashlib
import io
import zipfile
from typing import Tuple
from pydantic import BaseModel
from app.import_engine.exceptions import (
    FileValidationError,
    FileSizeLimitExceededError,
    UnsupportedFormatError,
    CorruptedFileError,
)

MAX_ALLOWED_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 Megabytes


class FileValidationResult(BaseModel):
    is_valid: bool
    file_name: str
    file_size_bytes: int
    extension: str
    sha256_hash: str
    detected_encoding: str
    mime_type: str


class FileValidator:
    """Enterprise-grade file validator ensuring strict security and compliance."""

    ALLOWED_EXTENSIONS = {".csv", ".xlsx"}
    ZIP_MAGIC = b"PK\x03\x04"

    @classmethod
    def compute_sha256(cls, content: bytes) -> str:
        """Computes deterministic SHA-256 cryptographic digest."""
        hasher = hashlib.sha256()
        hasher.update(content)
        return hasher.hexdigest()

    @classmethod
    def detect_text_encoding(cls, content: bytes) -> str:
        """Detects text encoding for CSV files, handling BOM, UTF-8, and Cyrillic encodings."""
        if content.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        
        # Test UTF-8 first
        try:
            content.decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            pass

        # Test Windows-1251 / CP1251 (common in Uzbekistan 1C / Bank exports)
        try:
            content.decode("cp1251")
            return "cp1251"
        except UnicodeDecodeError:
            pass

        # Fallback to latin-1 (lossless byte mapping)
        return "latin-1"

    @classmethod
    def validate(cls, file_name: str, content: bytes, max_size_bytes: int = MAX_ALLOWED_FILE_SIZE_BYTES) -> FileValidationResult:
        """
        Validates an uploaded file.
        Raises domain FileValidationError subclasses if invalid.
        """
        if not file_name:
            raise FileValidationError("Fayl nomi ko'rsatilmadi.")

        file_size = len(content)
        if file_size == 0:
            raise FileValidationError("Fayl bo'sh (0 bayt). Ma'lumot mavjud emas.")

        if file_size > max_size_bytes:
            raise FileSizeLimitExceededError(
                f"Fayl hajmi ({file_size / (1024*1024):.2f} MB) ruxsat etilgan "
                f"{max_size_bytes / (1024*1024):.0f} MB chegarasidan oshib ketdi."
            )

        # Check extension
        lower_name = file_name.lower().strip()
        matched_ext = None
        for ext in cls.ALLOWED_EXTENSIONS:
            if lower_name.endswith(ext):
                matched_ext = ext
                break

        if not matched_ext:
            raise UnsupportedFormatError(
                f"Fayl formati noto'g'ri: '{file_name}'. Faqat .xlsx va .csv formatlariga ruxsat berilgan."
            )

        sha256_hash = cls.compute_sha256(content)

        if matched_ext == ".xlsx":
            # Verify ZIP magic bytes
            if not content.startswith(cls.ZIP_MAGIC):
                raise CorruptedFileError("Excel (.xlsx) faylining sarlavha baytlari (magic bytes) noto'g'ri yoki fayl shikastlangan.")

            # Verify it is a valid zip and inspect for macro risks
            try:
                with zipfile.ZipFile(io.BytesIO(content)) as zf:
                    namelist = zf.namelist()
                    # Security check: check for macro payload files
                    for n in namelist:
                        if "vbaProject.bin" in n or n.endswith(".vba"):
                            raise FileValidationError(
                                "Xavfsizlik ogohlantirishi: Excel faylida bajariluvchi makroslar (VBA) aniqlandi. "
                                "Makrosli fayllarni import qilish taqiqlangan.",
                                code="MACRO_CONTAINED"
                            )
            except zipfile.BadZipFile:
                raise CorruptedFileError("Excel (.xlsx) faylini ZIP konteyner sifatida ochib bo'lmadi (buzilgan fayl).")

            return FileValidationResult(
                is_valid=True,
                file_name=file_name,
                file_size_bytes=file_size,
                extension=".xlsx",
                sha256_hash=sha256_hash,
                detected_encoding="binary",
                mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        else:
            # CSV file
            encoding = cls.detect_text_encoding(content)
            # Try decoding sample
            try:
                decoded = content.decode(encoding)
                if not decoded.strip():
                    raise FileValidationError("CSV faylida ko'rinadigan matn mavjud emas.")
            except Exception as e:
                raise CorruptedFileError(f"CSV faylini dekodlashda xatolik yuz berdi: {str(e)}")

            return FileValidationResult(
                is_valid=True,
                file_name=file_name,
                file_size_bytes=file_size,
                extension=".csv",
                sha256_hash=sha256_hash,
                detected_encoding=encoding,
                mime_type="text/csv",
            )
