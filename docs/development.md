# Development workflow

DeutschFlow is an independent Git repository. Do not place another Git repository around it or combine it with unrelated portfolio projects.

## Local setup

Use `SETUP.bat` on Windows or `./setup.sh` on Linux/macOS for the reproducible, lockfile-based setup. The scripts create or reuse `.venv`, install hashed Python dependencies from `requirements-dev.lock`, install the editable backend without re-resolving dependencies, install Node dependencies with `npm ci`, and build the extension.

The Python lock is generated from `apps/server/pyproject.toml` with `pip-tools`. Dependency updates should deliberately regenerate the lock with hashes and pass verification on Python 3.12 before publication. Argos remains an explicit optional installation because its language packages must never be downloaded automatically.

Direct developer commands remain available:

```powershell
.\scripts\dev-server.ps1
npm run dev:extension
.\scripts\verify.ps1
```

The extension and service remain separate applications. Browser-facing code communicates with the backend only through the documented loopback `/api/v1` JSON interface.

## Before sharing changes

1. Run `TEST.bat` or the platform-equivalent verification script.
2. Perform the manual Chrome/Opera check when browser behavior or packaging changed.
3. Review the complete diff.
4. Recheck extension permissions, secrets, unsafe HTML usage, and fake-provider scope.
5. Confirm generated `dist`, environment, database, token, and artifact files remain ignored.

## GitHub Desktop workflow

GitHub Desktop sees saved local changes immediately, but GitHub does not receive them until they are committed and pushed:

```text
edit → save → inspect diff → commit → push → GitHub updated
```

Use a focused branch for changes, inspect the files included in each commit, and push deliberately. Do not configure automatic add/commit/push behavior: intermediate code, generated files, local data, or secrets must not be published accidentally.

GitHub Actions runs the setup and verification wrappers on Ubuntu and Windows after pushes and pull requests. A green workflow confirms automated checks only; it does not prove manual unpacked-extension behavior.
