from datetime import datetime, timezone

import pytest

from deutschflow.review.scheduler import schedule_review

NOW = datetime(2026, 1, 2, 12, tzinfo=timezone.utc)


def test_rating_intervals_are_ordered():
    results = {rating: schedule_review(rating=rating, interval_days=0, ease=2.5, repetitions=0, lapses=0, now=NOW)
               for rating in ("again", "hard", "good", "easy")}
    assert results["again"].interval_days < results["hard"].interval_days
    assert results["hard"].interval_days <= results["good"].interval_days
    assert results["good"].interval_days < results["easy"].interval_days
    assert results["again"].lapses == 1


def test_scheduler_is_deterministic_and_bounded():
    left = schedule_review(rating="easy", interval_days=3000, ease=3, repetitions=20, lapses=1, now=NOW)
    right = schedule_review(rating="easy", interval_days=3000, ease=3, repetitions=20, lapses=1, now=NOW)
    assert left == right
    assert left.interval_days == 3650


def test_scheduler_requires_utc_aware_clock():
    with pytest.raises(ValueError):
        schedule_review(rating="good", interval_days=1, ease=2.5, repetitions=1, lapses=0, now=datetime(2026, 1, 1))


def test_scheduler_rejects_unknown_rating():
    with pytest.raises(ValueError):
        schedule_review(rating="perfect", interval_days=1, ease=2.5, repetitions=1, lapses=0, now=NOW)

