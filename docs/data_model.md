# Data model

`settings` stores non-secret server learning preferences. `learning_items` stores canonical/original text, editable grammar data, status, topic, and notes while preserving capitalization plus normalized exact-match fields. `meanings` separates contextual senses. `occurrences` stores each selected encounter and source metadata. `flashcards` stores meaningful card templates. One `review_state` controls each card's current schedule; append-only `review_events` preserve transitions.

Items cascade to their meanings, occurrences, cards, states, and review events. Timestamps are written in UTC and serialized with an offset; the extension renders them in browser-local time.

Exact duplicate detection normalizes whitespace and compares text/translation case-insensitively. It does not lemmatize or fuzzy-merge. The caller must choose to attach an occurrence or create a separate sense.

JSON schema version is `1`. Exports include non-secret settings, all entity groups, `exported_at`, and application version. Imports map exported card IDs to new local IDs so review state/history is retained.

