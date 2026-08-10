# Local API v1

Base URL: `http://127.0.0.1:8765`. Protected endpoints require `Authorization: Bearer <local token>`. Errors have `{ "error": { "code", "message" } }` and never expose stack traces.

| Method | Path | Auth | Purpose |
|---|---|---:|---|
| GET | `/api/v1/health` | no | Minimal service/provider availability |
| POST | `/api/v1/pairing/start` | no | Create a five-minute loopback pairing code |
| POST | `/api/v1/pairing/complete` | no | Exchange code for local token |
| GET | `/api/v1/providers` | yes | Provider health and installed pairs |
| POST | `/api/v1/translate` | yes | Translate a bounded selection |
| POST/GET | `/api/v1/items` | yes | Create or search/filter items |
| GET/PATCH/DELETE | `/api/v1/items/{id}` | yes | Read, edit, suspend, or delete |
| GET | `/api/v1/review/due` | yes | Ordered due cards, excluding suspended items |
| POST | `/api/v1/review/{card_id}` | yes | Persist a rating and schedule transition |
| GET | `/api/v1/export/json` | yes | Versioned full learning-data export |
| GET | `/api/v1/export/csv` | yes | Human-readable vocabulary export |
| POST | `/api/v1/import/preview` | yes | Validate and count without writing |
| POST | `/api/v1/import/apply` | yes | Transactional import with duplicate policy |
| DELETE | `/api/v1/data` | yes | Delete all learning data |

Stable codes include `PAIRING_REQUIRED`, `INVALID_TOKEN`, `SELECTION_TOO_LONG`, `TRANSLATION_PROVIDER_UNAVAILABLE`, `LANGUAGE_PAIR_UNAVAILABLE`, `ITEM_NOT_FOUND`, `DUPLICATE_ITEM`, `IMPORT_MALFORMED`, and `REQUEST_TOO_LARGE`.

