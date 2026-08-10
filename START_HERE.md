# Start here

DeutschFlow helps you turn German text that you deliberately select in Chrome or Opera into a private, local vocabulary collection and review cards. It does not translate whole pages, watch your browsing, or send selected text to a cloud service by default.

## Run DeutschFlow on Windows

Prerequisites: install [Python 3.12 or later](https://www.python.org/downloads/) and Node.js 24 LTS, version 24.15 or later. During Python installation, enable **Add Python to PATH**. The locked browser-test toolchain also supports Node.js 26 or later.

1. Double-click `SETUP.bat` once. It creates the local environment, installs the project dependencies, and builds the extension.
2. Double-click `RUN.bat`. Keep its window open while using DeutschFlow.
3. Open `chrome://extensions` in Chrome or `opera://extensions` in Opera.
4. Enable **Developer mode**, choose **Load unpacked**, and select the `apps/extension/dist` folder shown by `RUN.bat`.
5. Open DeutschFlow, go to **Settings**, choose **Start pairing**, and then **Complete pairing** with the displayed code.

The browser requires step 3 once because unpacked extensions cannot safely install themselves.

## Try the 60-second workflow

1. Open an ordinary German-language `http` or `https` webpage.
2. Select a short German word or phrase.
3. Right-click and choose **DeutschFlow: Learn selection**.
4. Review the captured sentence, optionally add a translation or notes, and save it.
5. Find the entry under **Wordbook**, then open **Review**.

Without an optional Argos German-to-English package, DeutschFlow clearly reports that translation is unavailable. Saving and reviewing manually entered material still works. DeutschFlow never downloads a translation model automatically.

## What you should see

- A DeutschFlow side panel, or a packaged extension tab if side panels are unavailable.
- The exact text you selected and a bounded nearby sentence when the page permits access.
- Learn, Wordbook, Review, and Settings views backed by local storage.
- A terminal window showing the local service at `http://127.0.0.1:8765`.

Learning data is stored under your user profile in `.deutschflow`. JSON and CSV exports are initiated from the extension; the repository's `artifacts/` folder is reserved for development outputs.

## Something went wrong?

Double-click `DOCTOR.bat`. It checks Python, Node.js, the local environment, installed dependencies, the extension build, writable output, Git information, and whether the service is already running. Its `WARN` messages are informational; `ERROR` messages require action.

See [troubleshooting](docs/troubleshooting.md) for pairing, translation-provider, browser-page, and database help.

## Tests

Double-click `TEST.bat` to run backend lint/tests, extension type checking/tests, and the production build. Browser interaction still requires the manual workflow above.

## Linux and macOS

Run `./setup.sh`, then `./run.sh`. Use `./doctor.sh` for diagnostics and `./test.sh` for verification. If a downloaded archive did not preserve executable permissions, run `chmod +x setup.sh run.sh doctor.sh test.sh scripts/*.sh` once.

## Advanced and developer usage

The simple launchers are thin wrappers. They do not replace the normal commands:

```powershell
.\scripts\dev-server.ps1
npm run dev:extension
.\scripts\verify.ps1
```

Read [README.md](README.md) for architecture, Argos setup, direct commands, privacy details, and known limitations. Local edits appear immediately in GitHub Desktop, but GitHub is updated only after you deliberately review, commit, and push them.
