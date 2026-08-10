# Privacy

DeutschFlow stores only content the user explicitly selects/saves: German text, optional translation/grammar/notes/topic, bounded source sentence, page title, URL/domain, cards, and review history. Source URLs can reveal browsing interests.

It does not store page HTML, complete browsing history, audio, cookies, analytics, advertising identifiers, or telemetry. No remote translation fallback exists. The extension talks to the loopback service; Argos processes text locally. Installing Argos language data may require a one-time, user-triggered download from the model distributor, never an automatic server action.

Extension configuration and the token live in `chrome.storage.local`. Server token/database default to `~/.deutschflow/api.token` and `~/.deutschflow/deutschflow.db`. JSON export excludes secrets. Use Settings → **Delete all learning data**, then remove extension-local data/browser extension and the remaining `~/.deutschflow` token/database files if complete removal is desired.

The service binds only to loopback and is not designed for internet exposure. Audio and later-phase features are not implemented.

