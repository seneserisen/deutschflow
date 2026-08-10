# ADR 0001: Local-first architecture

Status: accepted

DeutschFlow stores learning data in a local SQLite database and translates through an explicitly configured local provider. The extension sends only a user-selected excerpt and bounded context to a service on `127.0.0.1`. No telemetry, cloud account, remote database, or remote fallback is part of Phase 1.

This minimizes disclosure and lets the product continue saving material when translation is unavailable. Source URLs remain sensitive local data and are exportable/deletable by the user.

