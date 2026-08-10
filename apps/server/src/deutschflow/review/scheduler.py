from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class Schedule:
    due_at: datetime
    interval_days: float
    ease: float
    repetitions: int
    lapses: int


def schedule_review(
    *, rating: str, interval_days: float, ease: float, repetitions: int, lapses: int, now: datetime
) -> Schedule:
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    now = now.astimezone(timezone.utc)
    if rating == "again":
        new_interval, new_ease, new_repetitions, new_lapses = 10 / 1440, max(1.3, ease - 0.2), 0, lapses + 1
    elif rating == "hard":
        new_interval = max(1.0, interval_days * 1.2 if interval_days else 1.0)
        new_ease, new_repetitions, new_lapses = max(1.3, ease - 0.15), repetitions + 1, lapses
    elif rating == "good":
        new_interval = 1.0 if repetitions == 0 else max(interval_days + 1, interval_days * ease)
        new_ease, new_repetitions, new_lapses = ease, repetitions + 1, lapses
    elif rating == "easy":
        new_interval = 4.0 if repetitions == 0 else max(interval_days + 2, interval_days * (ease + 0.5))
        new_ease, new_repetitions, new_lapses = min(3.0, ease + 0.15), repetitions + 1, lapses
    else:
        raise ValueError("rating must be again, hard, good, or easy")
    new_interval = min(3650.0, new_interval)
    return Schedule(now + timedelta(days=new_interval), new_interval, new_ease, new_repetitions, new_lapses)

