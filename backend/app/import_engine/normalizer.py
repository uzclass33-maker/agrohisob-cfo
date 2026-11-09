"""
AgroHisob CFO - Financial Normalizer
Handles locale-aware numeric conversion, multi-format date resolution, INN/STIR extraction,
MXIK code cleanup, and string sanitization according to Uzbekistan accounting formats.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import re
from typing import Any, Optional, Tuple
from app.import_engine.exceptions import InvalidRowError


EXCEL_EPOCH = datetime(1899, 12, 30)


class Normalizer:
    """Robust, deterministic normalizer for accounting values in UZS."""

    @classmethod
    def clean_text(cls, val: Any) -> str:
        """Removes excess whitespace, non-printable characters, and normalizes quotes."""
        if val is None:
            return ""
        s = str(val).strip()
        # Replace non-breaking space and various Unicode spaces with standard space
        s = re.sub(r"[\xa0\u2000-\u200b\u202f]", " ", s)
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    @classmethod
    def parse_amount(cls, val: Any) -> Optional[Decimal]:
        """
        Parses monetary amount string into a Decimal with 2 decimal places.
        Handles:
          - '1 250 000,50'
          - '1,250,000.50'
          - '1.250.000,50'
          - '1250000-00'
          - '1250000'
          - '(500.00)' -> Decimal('-500.00')
          - None, '', '-' -> None
        """
        if val is None:
            return None

        # If already Decimal or int/float
        if isinstance(val, (int, float, Decimal)):
            try:
                dec = Decimal(str(val))
                return dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except Exception:
                return None

        s = cls.clean_text(val)
        if not s or s in ("-", "—", "–", "0", "0.00", "0,00", "null", "none"):
            if s in ("0", "0.00", "0,00"):
                return Decimal("0.00")
            return None

        # Check for parentheses indicating negative: (100) -> -100
        is_negative = False
        if s.startswith("(") and s.endswith(")"):
            is_negative = True
            s = s[1:-1].strip()
        elif s.startswith("-"):
            is_negative = True
            s = s[1:].strip()

        # Remove currency words
        s = re.sub(r"(?i)\b(so'm|som|сум|uzs|usd|rub|eur)\b", "", s).strip()

        # Remove all whitespace
        s = s.replace(" ", "")

        # If string contains both comma and dot, e.g. 1,250,000.50 vs 1.250.000,50
        if "," in s and "." in s:
            last_comma = s.rfind(",")
            last_dot = s.rfind(".")
            if last_dot > last_comma:
                # Comma is thousand sep, dot is decimal (e.g. 1,250,000.50)
                s = s.replace(",", "")
            else:
                # Dot is thousand sep, comma is decimal (e.g. 1.250.000,50)
                s = s.replace(".", "").replace(",", ".")
        elif "," in s:
            # Only comma present. If there are 2 decimal digits at end, it's decimal point
            parts = s.split(",")
            if len(parts) == 2 and len(parts[1]) in (1, 2, 3):
                s = parts[0] + "." + parts[1]
            else:
                # e.g., '1,250,000'
                s = s.replace(",", "")
        
        # Remove any stray characters except digits, dot, and minus
        s = re.sub(r"[^\d.]", "", s)

        if not s or s == ".":
            return None

        try:
            amount = Decimal(s)
            if is_negative:
                amount = -amount
            return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except InvalidOperation:
            return None

    @classmethod
    def parse_date(cls, val: Any) -> Optional[date]:
        """
        Parses date from multiple representations:
          - datetime.date or datetime.datetime objects
          - Excel serial date integers/floats (e.g. 45350)
          - String formats: 'YYYY-MM-DD', 'DD.MM.YYYY', 'DD/MM/YYYY', 'DD-MM-YYYY', 'YYYY.MM.DD'
        """
        if val is None:
            return None

        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, date):
            return val

        # Handle numeric Excel serial date
        if isinstance(val, (int, float)):
            try:
                # Excel leap year bug: day 60 is Feb 29 1900 which did not exist
                days = float(val)
                if days > 60:
                    days -= 1
                parsed_dt = EXCEL_EPOCH + timedelta(days=days)
                return parsed_dt.date()
            except Exception:
                return None

        s = cls.clean_text(val)
        if not s:
            return None

        # If string is a float/integer representing serial date
        if re.match(r"^\d{4,5}(\.\d+)?$", s):
            try:
                days = float(s)
                if days > 60:
                    days -= 1
                parsed_dt = EXCEL_EPOCH + timedelta(days=days)
                return parsed_dt.date()
            except Exception:
                pass

        # Try standard string date formats
        date_formats = [
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y.%m.%d",
            "%Y/%m/%d",
            "%Y-%m-%d %H:%M:%S",
            "%d.%m.%Y %H:%M:%S",
            "%d.%m.%Y %H:%M",
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue

        return None

    @classmethod
    def parse_inn(cls, val: Any) -> Optional[str]:
        """
        Normalizes Uzbekistan Taxpayer Identification Number (INN / STIR).
        Valid Uzbekistan INN consists of 9 digits.
        """
        if val is None:
            return None
        s = cls.clean_text(val)
        digits = re.sub(r"\D", "", s)
        if len(digits) == 9:
            return digits
        elif len(digits) > 9 and digits.endswith("000"):
            # Some old systems padded INN with 000
            return digits[:9]
        elif 8 <= len(digits) <= 14:
            # Return raw digits if reasonable length
            return digits
        return None

    @classmethod
    def parse_mxik(cls, val: Any) -> Optional[str]:
        """
        Normalizes MXIK (IKPU) code.
        Can be 17 digits (e.g. 01111000001000000) or dot-separated (e.g. 01.11.10.001).
        """
        if val is None:
            return None
        s = cls.clean_text(val)
        if not s:
            return None
        # Remove non-alphanumeric except dots
        cleaned = re.sub(r"[^\d.]", "", s)
        if cleaned:
            return cleaned
        return None

    @classmethod
    def parse_bank_account(cls, val: Any) -> Optional[str]:
        """Normalizes 20-digit bank account number."""
        if val is None:
            return None
        s = cls.clean_text(val)
        digits = re.sub(r"\D", "", s)
        if len(digits) == 20:
            return digits
        return digits if len(digits) >= 10 else None
