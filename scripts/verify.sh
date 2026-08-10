#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
.venv/bin/ruff check apps/server
.venv/bin/python -c "from importlib.metadata import version; assert version('httpx2')"
.venv/bin/python -m pip check
.venv/bin/python -m pytest apps/server/tests
npm run verify:extension
npm audit --audit-level=high
.venv/bin/python -c "from deutschflow.main import app; assert app.title == 'DeutschFlow local API'"
