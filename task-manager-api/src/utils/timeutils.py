"""Time helpers. now_utc() replaces the deprecated datetime.utcnow() while keeping naive-UTC
semantics (consistent with due_date values parsed via strptime)."""
from datetime import datetime, timezone


def now_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)
