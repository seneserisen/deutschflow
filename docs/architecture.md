# Architecture

The extension owns browser interaction, ephemeral pending selection state, user settings, and presentation. The service owns translation-provider access, authentication, durable learning data, review scheduling, and interchange formats. The boundary is `/api/v1` JSON over loopback HTTP.

The service worker creates one selection-only context menu. On activation it saves a fallback from `selectionText`, then attempts a one-shot script injection using `activeTab` to obtain a bounded nearest block/sentence. It never stores page HTML. It opens Chrome's side panel when available or a packaged extension page otherwise.

FastAPI validates body and field lengths, authenticates protected calls, and uses SQLAlchemy with SQLite foreign keys enabled. Translation providers implement health, supported-pairs, and translate. Argos inspects installed packages; disabled mode is honest; fake mode is explicit development/testing only.

Material risks are recorded in `assumptions.md`. Native Messaging, morphology enrichment, local LLM translation, user-configured remote translation, browser-native translation, and dictionaries are future provider/transport options only.

