# Project status

Status: **implemented and automated-tested; browser-manual verification required**.

Implemented:

- Phase 1 browser selection workflow with bounded context and fallback
- local authenticated FastAPI/SQLite backend
- translation-provider interface, explicit test fake, optional Argos adapter, disabled behavior
- searchable/filterable/editable wordbook and contextual senses/occurrences
- deterministic review scheduler, due queue, shortcuts, and history
- versioned JSON/CSV export plus previewed transactional import
- privacy/permissions controls, tests, scripts, and documentation
- guided setup, run, test, and doctor launchers for Windows and supported Unix-like systems
- Ubuntu and Windows continuous verification through GitHub Actions
- hashed Python and locked Node dependency installations for repeatable setup

Not implemented:

- full-page translation or hover assistance
- video caption ingestion, tab-audio capture, live transcription, or dual subtitles
- shadowing, recording, pronunciation assessment, or writing correction
- AI-generated exercises, cloud synchronization/accounts, or mobile apps

Automated browser-extension loading is not configured. Chrome and Opera unpacked-extension acceptance checks remain manual and must not be inferred from a successful build.
