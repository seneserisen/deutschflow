# Assumptions and risks

- Python 3.12 is the target, while compatible newer Python versions may run the service.
- Chrome is the primary browser. Opera may lack or vary the `sidePanel` API, so an extension-page fallback is required.
- Argos is optional and its packages are installed only by an explicit user action outside server startup.
- A pairing code printed to the local terminal is acceptable for the development-friendly local pairing flow.
- Browser automation may be unavailable; build/tests do not substitute for manual unpacked-extension checks.
- SQLite schema creation is sufficient for the first local release; future schema changes require a migration plan.
- Localhost HTTP and a bearer token reduce accidental local access but are not authentication for a network-exposed service.

