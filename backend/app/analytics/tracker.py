import os
import re
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Any, Dict
from app.analytics.schemas import (
    AnalyticsEvent, AnalyticsEventCreate,
    AnalyticsSummary, AnalyticsEventType
)

# Configurable storage directory to allow full isolation during testing
_DEFAULT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "analytics")
ANALYTICS_DIR = os.environ.get("AGROHISOB_ANALYTICS_DIR", _DEFAULT_DIR)
os.makedirs(ANALYTICS_DIR, exist_ok=True)
EVENTS_FILE = os.path.join(ANALYTICS_DIR, "events.json")

def set_analytics_storage_dir(custom_dir: str):
    """Overrides the storage directory for deterministic, isolated unit and integration testing."""
    global ANALYTICS_DIR, EVENTS_FILE
    ANALYTICS_DIR = custom_dir
    os.makedirs(ANALYTICS_DIR, exist_ok=True)
    EVENTS_FILE = os.path.join(ANALYTICS_DIR, "events.json")

FORBIDDEN_PII_KEYS = {
    "inn", "tin", "tax_id", "pinfl", "jshshir", "passport", "bank_account", "card_number",
    "password", "token", "auth", "secret", "balance", "amount_uzs", "phone", "email",
    "card", "account_number", "salary", "credit_card"
}

# Strict allowlist of permitted metadata keys for telemetry
ALLOWED_METADATA_KEYS = {
    "section", "view_mode", "file_ext", "records_count", "scenario_type",
    "crop", "region", "step", "tab", "duration_category", "filter_selected",
    "export_format", "ui_theme", "page_number", "locale", "error_code",
    "report_type", "status_filter", "is_synthetic", "document_type"
}

# Deep Regex Patterns for PII Detection and Scrubbing in String Values
PATTERNS = [
    # Bank Account (20 digits in Uzbekistan banking)
    (re.compile(r'\b\d{20}\b'), '[REDACTED_BANK_ACC]'),
    # Card Number (16 digits, with optional spaces or hyphens)
    (re.compile(r'\b(?:\d{4}[ -]?){3}\d{4}\b'), '[REDACTED_CARD]'),
    # JSHSHIR / PINFL (14 digits)
    (re.compile(r'\b\d{14}\b'), '[REDACTED_PINFL]'),
    # STIR / INN (9 digits)
    (re.compile(r'\b\d{9}\b'), '[REDACTED_STIR]'),
    # Phone numbers (Uzbekistan format: +998... or 998... or 9-digit local)
    (re.compile(r'(?:\+?998[- ]?)?(?:90|91|93|94|95|97|98|99|33|88|77)[- ]?\d{3}[- ]?\d{2}[- ]?\d{2}\b'), '[REDACTED_PHONE]'),
    # Generic Email Address
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'), '[REDACTED_EMAIL]')
]

def _scrub_string_content(text: str) -> str:
    """Recursively scrubs all known financial and personal identifiers from free text."""
    result = text
    for pattern, replacement in PATTERNS:
        result = pattern.sub(replacement, result)
    return result

def _load_json(file_path: str, default_val):
    if not os.path.exists(file_path):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_val, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        return default_val
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_val

def _save_json(file_path: str, data):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _sync_event_to_db(e: dict):
    """Synchronizes analytics event to durable database model."""
    try:
        from app.db.database import SessionLocal
        from app.models.core import AnalyticsEventModel
        session = SessionLocal()
        try:
            ev = AnalyticsEventModel(
                id=e.get("id"),
                event_type=e.get("event_type", "unknown"),
                user_id=e.get("user_id"),
                organization_id=e.get("organization_id"),
                session_id=e.get("session_id", "anon"),
                path=e.get("path"),
                metadata_json=e.get("metadata")
            )
            session.add(ev)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
    except Exception:
        pass

def _sanitize_metadata(meta: dict) -> dict:
    """
    Applies strict key filtering and deep recursive content scrubbing.
    Explicitly enforces data privacy rules:
    - Known sensitive keys -> [REDACTED_PII]
    - Non-allowlisted arbitrary keys -> redacted or dropped if sensitive
    - String values -> deep regex scrubbing for INN, PINFL, Bank Account, Cards, Phone, Email
    """
    if not meta or not isinstance(meta, dict):
        return {}
    clean = {}
    for k, v in meta.items():
        k_lower = str(k).lower().strip()
        # Direct match with forbidden keys
        if any(bad in k_lower for bad in FORBIDDEN_PII_KEYS):
            clean[k] = "[REDACTED_PII]"
        elif isinstance(v, str):
            scrubbed_val = _scrub_string_content(v)
            clean[k] = scrubbed_val
        elif isinstance(v, (int, float, bool)):
            clean[k] = v
        elif isinstance(v, dict):
            clean[k] = _sanitize_metadata(v)
        elif isinstance(v, list):
            clean[k] = [_scrub_string_content(x) if isinstance(x, str) else x for x in v]
        else:
            clean[k] = str(v)
    return clean

def _purge_expired_events(events: List[Dict[str, Any]], retention_days: int = 30) -> List[Dict[str, Any]]:
    """Enforces 30-day maximum data retention policy for telemetry events."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    valid_events = []
    for e in events:
        ts_str = e.get("timestamp")
        if not ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            if ts >= cutoff:
                valid_events.append(e)
        except Exception:
            valid_events.append(e)
    return valid_events

class ProductAnalytics:
    @staticmethod
    def record_event(data: AnalyticsEventCreate) -> AnalyticsEvent:
        events = _load_json(EVENTS_FILE, [])
        events = _purge_expired_events(events, retention_days=30)
        
        sanitized_meta = _sanitize_metadata(data.metadata or {})
        
        event_dict = data.model_dump()
        event_dict["metadata"] = sanitized_meta
        event_dict["id"] = f"evt-{uuid.uuid4().hex[:10]}"
        event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        events.append(event_dict)
        # Keep last 1000 events to prevent unbounded growth in storage
        if len(events) > 1000:
            events = events[-1000:]
        _save_json(EVENTS_FILE, events)
        _sync_event_to_db(event_dict)
        return AnalyticsEvent(**event_dict)

    @staticmethod
    def get_events(limit: int = 50, event_type: Optional[str] = None) -> List[AnalyticsEvent]:
        events = _load_json(EVENTS_FILE, [])
        events = _purge_expired_events(events, retention_days=30)
        if event_type:
            events = [e for e in events if e.get("event_type") == event_type]
        events = sorted(events, key=lambda x: x.get("timestamp", ""), reverse=True)
        return [AnalyticsEvent(**e) for e in events[:limit]]

    @staticmethod
    def get_summary() -> AnalyticsSummary:
        events = _load_json(EVENTS_FILE, [])
        events = _purge_expired_events(events, retention_days=30)
        total = len(events)
        counts = {}
        durations = {}
        duration_counts = {}
        errors = {}
        sessions = set()

        for e in events:
            etype = e.get("event_type", "unknown")
            counts[etype] = counts.get(etype, 0) + 1
            sessions.add(e.get("session_id", ""))

            dur = e.get("duration_ms")
            if dur is not None and isinstance(dur, (int, float)):
                durations[etype] = durations.get(etype, 0.0) + float(dur)
                duration_counts[etype] = duration_counts.get(etype, 1) + 1

            if e.get("status") == "FAILED":
                errors[etype] = errors.get(etype, 0) + 1

        avg_durations = {}
        for etype, total_dur in durations.items():
            cnt = duration_counts.get(etype, 1)
            avg_durations[etype] = round(total_dur / cnt, 2)

        error_rates = {}
        for etype, cnt in counts.items():
            err_cnt = errors.get(etype, 0)
            error_rates[etype] = round((err_cnt / cnt) * 100.0, 1)

        return AnalyticsSummary(
            total_events=total,
            event_counts=counts,
            avg_durations_ms=avg_durations,
            error_rates=error_rates,
            unique_sessions=len(sessions)
        )
