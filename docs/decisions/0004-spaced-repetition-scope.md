# ADR 0004: Spaced-repetition scope

Status: accepted

Phase 1 uses a deterministic, simplified SM-2-inspired scheduler. New cards begin due immediately. Again, Hard, Good, and Easy map to progressively longer intervals, with lapse tracking and bounded intervals. The scheduler accepts an explicit UTC clock and stores every transition.

It is neither Anki-compatible nor FSRS and is not claimed to be scientifically optimal.

