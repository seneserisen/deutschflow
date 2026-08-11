# DeutschFlow

[![Verify](https://github.com/seneserisen/deutschflow/actions/workflows/ci.yml/badge.svg)](https://github.com/seneserisen/deutschflow/actions/workflows/ci.yml)

DeutschFlow is a local-first Chrome/Opera learning assistant for turning German text you explicitly select into contextual vocabulary and review cards. It encourages reading first and help on demand; it does not translate whole pages or monitor browsing.

## Phase 1 status

Implemented in this repository: a Manifest V3 extension, safe selection/context capture, side-panel and fallback UI, loopback FastAPI service, token pairing, optional Argos adapter, local SQLite wordbook, conservative duplicate handling, deterministic review queue, JSON/CSV export, transactional JSON import, tests, and documentation.

Not implemented: full-page or hover translation, caption/video ingestion, audio capture, transcription, dual subtitles, shadowing, pronunciation assessment, writing correction, cloud sync, accounts, telemetry, or mobile apps. See [project status](docs/project_status.md) and the roadmap.

## 60-second local start

For a guided, low-technical-skill setup, begin with [START_HERE.md](START_HERE.md). On Windows, the basic workflow is `SETUP.bat` once and then `RUN.bat`; `DOCTOR.bat` provides readable diagnostics and `TEST.bat` runs the complete automated verification suite.

## Walkthrough

1. Start the local service and pair the extension in **Settings**.
2. Select German text on an ordinary webpage.
3. Right-click and choose **DeutschFlow: Learn selection**.
4. The **Learn** view shows the exact selection, bounded source sentence, local translation status, editable grammar details, notes, and topic.
5. Save it, resolve an exact duplicate as a new occurrence or separate sense, then search/filter it and edit its translation or grammar details in **Wordbook**.
6. Open **Review**, reveal or type an answer, and grade with Again/Hard/Good/Easy (keys 1–4).
7. Export JSON for round-trip backup or CSV for a spreadsheet.

## Architecture and privacy

```text
explicit selection → MV3 extension → http://127.0.0.1:43131 → FastAPI
                                                        ├─ SQLite
                                                        └─ local provider (Argos/disabled)
```

Protected API calls require a random bearer token stored in `~/.deutschflow/api.token` and `chrome.storage.local`. The database defaults to `~/.deutschflow/deutschflow.db`. Selected text is never sent to a remote service by default, complete page HTML/history is not collected, and no remote fallback exists. Source URLs are stored because they are part of the learning record and may reveal interests. Read [privacy](docs/privacy.md) and [permissions](docs/permissions.md).

## Requirements

- Python 3.12 or later (the automated run also passes on Python 3.14)
- Node.js 24 LTS (24.15 or later) and npm; the locked toolchain also supports Node.js 26+
- Chrome; current Opera is expected to load MV3 extensions but its side-panel behavior may differ
- Optional: Argos Translate and a user-installed local language package

## Local setup (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e ".\apps\server"
npm ci
```

The root launchers use the hashed `requirements-dev.lock` and `package-lock.json` files for repeatable Python and Node installations. The commands above remain available for developers working directly with the workspace.

Start the server:

```powershell
.\scripts\dev-server.ps1
```

Build the extension:

```powershell
npm run build
```

The service refuses a configured non-loopback host. Its portfolio-assigned URL is `http://127.0.0.1:43131`.

## Load unpacked in Chrome

1. Run the extension build.
2. Open `chrome://extensions`.
3. Enable **Developer mode**.
4. Choose **Load unpacked** and select `apps/extension/dist`.
5. Open DeutschFlow, go to **Settings**, choose **Start pairing**, then **Complete pairing** with the displayed six-digit code. The server also prints it locally.
6. Open a normal `http`/`https` page, select text, and use the context-menu action.

Chrome blocks injection on pages such as `chrome://settings` and the extension gallery. DeutschFlow retains the menu-provided selection and shows a clear context-unavailable message in that case.

## Opera manual loading

Open `opera://extensions`, enable developer mode, choose **Load unpacked**, and select `apps/extension/dist`. Opera builds can differ in `chrome.sidePanel` support; DeutschFlow feature-detects it and opens `panel.html` in an extension tab when unavailable. Manual Chrome and Opera checks remain required on each target browser version.

## Argos translation setup

The base service remains usable without Argos: saving and review work, but the UI reports that translation setup is required. No fake or remote translation is substituted.

Install the optional Python adapter explicitly:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".\apps\server[argos]"
```

Then use the official Argos package index/CLI or desktop application to deliberately install a German → English package. DeutschFlow never downloads packages at startup or in tests. Restart the server and use **Check backend**. Other pairs, including German/Turkish, appear only if a compatible local package is actually installed.

For deterministic development fixtures only, start with `DEUTSCHFLOW_PROVIDER=fake`; never use its output as language instruction.

## Verification

```powershell
.\scripts\verify.ps1
```

Individual commands:

```powershell
.\.venv\Scripts\ruff.exe check apps/server
.\.venv\Scripts\python.exe -m pytest apps/server/tests
npm run typecheck
npm run test:extension
npm run build
```

GNU Make equivalents are available as `make setup`, `make dev-server`, `make dev-extension`, `make test`, `make lint`, and `make verify` when `python` resolves to the prepared environment.

## Known limitations

- Browser loading and interaction require a manual check; unit/build success does not prove store/browser behavior.
- The built manifest grants only the portfolio-assigned `127.0.0.1:43131` origin. A different port requires a corresponding manifest permission adjustment and rebuild.
- Pairing is development-friendly local protection, not internet-grade authentication.
- Argos quality and installed pair availability are external to DeutschFlow.
- Sentence extraction is deliberately heuristic and bounded.
- SQLite schema creation is appropriate for this first local release; later schema changes need migrations.
- The scheduler is simplified SM-2-inspired logic, not Anki or FSRS compatibility.
- Imported schema version 1 data is validated structurally and applied transactionally; duplicate policy is skip or create-new.

See [troubleshooting](docs/troubleshooting.md), [architecture](docs/architecture.md), and the [Phase 2 roadmap](docs/roadmap/phase-2-reading-assistant.md).

Contributor setup and the deliberate local-to-GitHub workflow are documented in [development](docs/development.md).
