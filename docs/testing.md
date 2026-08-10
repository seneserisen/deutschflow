# Testing

Backend unit/integration tests cover provider states, validation/authentication, pairing, exact duplicates and separate senses, occurrences, card creation, all rating transitions, due/suspended behavior, UTC serialization, JSON/CSV export, preview/transactional import, review-state/history restoration, body limits, database initialization, and the end-to-end learning loop.

Extension unit tests cover whitespace/sentence extraction including nested elements and excessive selections, stable API error mapping, backend/provider unavailable states, pending state, duplicate-code mapping, review shortcuts/typing protection, domain handling, and side-panel fallback. Type checking and the Vite production build validate the packaged sources and Manifest V3 copy.

Manual browser checks are intentionally separate. Follow README steps on a normal fixture/web page and confirm select → context menu → panel → translate → save → wordbook → review. Do not report this passed unless performed in Chrome/Opera.

For a guided Windows check, run `TEST.bat`; on Linux/macOS, run `./test.sh`. These thin wrappers invoke the same repository verification as `scripts/verify.ps1` and `scripts/verify.sh`. `DOCTOR.bat`/`./doctor.sh` checks prerequisites and installation state but is not a substitute for tests or manual browser acceptance.

GitHub Actions runs the setup and verification wrappers on current Ubuntu and Windows runners with Python 3.12 and Node.js 24. CI validates clean dependency installation, linting, backend and extension tests, type checking, and the production build. It still cannot replace manual unpacked-extension checks in Chrome and Opera.
