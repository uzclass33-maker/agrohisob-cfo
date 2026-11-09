import os
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from app.analytics.schemas import (
    AnalyticsEvent, AnalyticsEventCreate,
    AnalyticsSummary, AnalyticsEventType
)

ANALYTICS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "analytics")
os.makedirs(ANALYTICS_DIR, exist_ok=True)

EVENTS_FILE = os.path.join(ANALYTICS_DIR, "events.json")

FORBIDDEN_PII_KEYS = {
    "inn", "tin", "tax_id", "pinfl", "passport", "bank_account", "card_number",
    "password", "token", "auth", "secret", "balance", "amount_uzs", "phone", "email"
}

def _load_json(file_path: str, default_val):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_val, f, indent=2, ensure_ascii=False)
        return default_val
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_val

def _save_json(file_path: str, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _sanitize_metadata(meta: dict) -> dict:
    """Strips any sensitive or PII fields that violate data privacy policy."""
    if not meta:
        return {}
    clean = {}
    for k, v in meta.items():
        k_lower = k.lower()
        if any(bad in k_lower for bad in FORBIDDEN_PII_KEYS):
            clean[k] = "[REDACTED_PII]"
        elif isinstance(v, (int, float, str, bool)):
            clean[k] = v
    return clean

class ProductAnalytics:
    @staticmethod
    def record_event(data: AnalyticsEventCreate) -> AnalyticsEvent:
        events = _load_json(EVENTS_FILE, [])
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
        return AnalyticsEvent(**event_dict)

    @staticmethod
    def get_events(limit: int = 50, event_type: Optional[str] = None) -> List[AnalyticsEvent]:
        events = _load_json(EVENTS_FILE, [])
        if event_type:
            events = [e for e in events if e.get("event_type") == event_type]
        events = sorted(events, key=lambda x: x.get("timestamp", ""), reverse=True)
        return [AnalyticsEvent(**e) for e in events[:limit]]

    @staticmethod
    def get_summary() -> AnalyticsSummary:
        events = _load_json(EVENTS_FILE, [])
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
                duration_counts[etype] = duration_counts.get(etype, 0) + 1

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
