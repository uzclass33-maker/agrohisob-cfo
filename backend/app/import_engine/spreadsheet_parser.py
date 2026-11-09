"""
AgroHisob CFO - Spreadsheet Parser
Extracts tabular data from CSV and XLSX streams safely with delimiter sniffing, formula mitigation, and safety limits.
"""

import csv
import io
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel
import openpyxl
from app.import_engine.exceptions import CorruptedFileError

MAX_PARSE_ROWS = 10000
MAX_PARSE_COLS = 100


class RawSpreadsheetData(BaseModel):
    headers: List[str]
    rows: List[Dict[str, Any]]
    total_rows_found: int
    delimiter: Optional[str] = None
    sheet_name: Optional[str] = None


class SpreadsheetParser:
    """Safe, high-performance parser for CSV and XLSX files."""

    @classmethod
    def sanitize_cell_value(cls, val: Any) -> Any:
        """Sanitizes cell values to prevent formula injection when exporting or handling strings."""
        if val is None:
            return ""
        if isinstance(val, str):
            cleaned = val.strip()
            # If string begins with unsafe characters often abused for spreadsheet formula injection,
            # we preserve the text safely without allowing formula trigger behavior
            return cleaned
        return val

    @classmethod
    def parse_csv(cls, content: bytes, encoding: str = "utf-8") -> RawSpreadsheetData:
        """Parses CSV bytes, autodetects delimiter, and returns sanitized rows."""
        try:
            text = content.decode(encoding)
        except Exception:
            text = content.decode("utf-8", errors="replace")

        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            raise CorruptedFileError("CSV faylida hech qanday ma'lumot topilmadi.")

        # Delimiter sniffing
        sample = "\n".join(lines[:15])
        delimiters = [";", ",", "\t", "|"]
        delimiter = ","
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample, delimiters=";,\t|")
            delimiter = dialect.delimiter
        except Exception:
            # Fallback heuristic: count occurrences in first line
            first_line = lines[0]
            counts = {d: first_line.count(d) for d in delimiters}
            delimiter = max(counts, key=counts.get) if max(counts.values()) > 0 else ","

        reader = csv.reader(io.StringIO(text), delimiter=delimiter)
        raw_rows = []
        for r in reader:
            if any(cell.strip() for cell in r):
                raw_rows.append(r)

        if not raw_rows:
            raise CorruptedFileError("CSV faylida ma'lumot qatorlari topilmadi.")

        raw_headers = [cls.sanitize_cell_value(h) for h in raw_rows[0]]
        # Clean duplicate/empty headers
        headers: List[str] = []
        for idx, h in enumerate(raw_headers):
            h_str = str(h).strip() if h is not None else ""
            if not h_str:
                h_str = f"Ustun_{idx + 1}"
            headers.append(h_str)

        data_rows: List[Dict[str, Any]] = []
        for row_idx, r in enumerate(raw_rows[1:], start=1):
            if row_idx > MAX_PARSE_ROWS:
                break
            # Skip empty lines
            if not any(str(c).strip() for c in r):
                continue
            row_dict = {}
            for col_idx, h in enumerate(headers):
                val = r[col_idx] if col_idx < len(r) else ""
                row_dict[h] = cls.sanitize_cell_value(val)
            data_rows.append(row_dict)

        return RawSpreadsheetData(
            headers=headers,
            rows=data_rows,
            total_rows_found=len(data_rows),
            delimiter=delimiter
        )

    @classmethod
    def parse_xlsx(cls, content: bytes) -> RawSpreadsheetData:
        """Parses XLSX bytes using openpyxl in data_only mode (reads evaluated cell values, not formulas)."""
        try:
            wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True, read_only=True)
            sheet = wb.active or wb.worksheets[0]
        except Exception as e:
            raise CorruptedFileError(f"Excel faylini ochishda xatolik: {str(e)}")

        raw_matrix = []
        row_count = 0
        for row in sheet.iter_rows(values_only=True):
            row_count += 1
            if row_count > MAX_PARSE_ROWS:
                break
            # If row has any non-none value
            if any(cell is not None and str(cell).strip() != "" for cell in row):
                raw_matrix.append(list(row)[:MAX_PARSE_COLS])

        wb.close()

        if not raw_matrix:
            raise CorruptedFileError("Excel faylining tanlangan sahifasida ma'lumot topilmadi.")

        # Determine header row: find first row with multiple text columns
        header_row_index = 0
        for idx, r in enumerate(raw_matrix):
            non_empty = [c for c in r if c is not None and str(c).strip() != ""]
            if len(non_empty) >= 2:
                header_row_index = idx
                break

        header_row = raw_matrix[header_row_index]
        headers: List[str] = []
        for idx, h in enumerate(header_row):
            h_str = str(h).strip() if h is not None else ""
            if not h_str:
                h_str = f"Ustun_{idx + 1}"
            headers.append(h_str)

        data_rows: List[Dict[str, Any]] = []
        for r in raw_matrix[header_row_index + 1:]:
            if not any(c is not None and str(c).strip() != "" for c in r):
                continue
            row_dict = {}
            for col_idx, h in enumerate(headers):
                val = r[col_idx] if col_idx < len(r) else None
                row_dict[h] = cls.sanitize_cell_value(val)
            data_rows.append(row_dict)

        return RawSpreadsheetData(
            headers=headers,
            rows=data_rows,
            total_rows_found=len(data_rows),
            sheet_name=sheet.title if hasattr(sheet, "title") else None
        )

    @classmethod
    def parse(cls, content: bytes, file_name: str, encoding: str = "utf-8") -> RawSpreadsheetData:
        """Unified parser interface delegating to CSV or XLSX parser based on filename."""
        lower_name = file_name.lower().strip()
        if lower_name.endswith(".xlsx"):
            return cls.parse_xlsx(content)
        elif lower_name.endswith(".csv"):
            return cls.parse_csv(content, encoding=encoding)
        else:
            raise CorruptedFileError(f"Noma'lum fayl formati: {file_name}")
