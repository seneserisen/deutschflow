#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

[ -x "$ROOT/.venv/bin/python" ] || { printf 'ERROR: DeutschFlow is not set up. Run ./setup.sh first.\n' >&2; exit 1; }
[ -d "$ROOT/node_modules" ] || { printf 'ERROR: Extension dependencies are missing. Run ./setup.sh again.\n' >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { printf 'ERROR: npm was not found. Install Node.js 24 LTS (24.15 or later).\n' >&2; exit 1; }

npm run build
printf '\nDeutschFlow is ready for the browser.\n'
printf 'Extension folder: %s/apps/extension/dist\n\n' "$ROOT"
printf 'Load that folder from chrome://extensions or opera://extensions using Developer mode.\n'
printf 'The service is starting at http://127.0.0.1:43131. Keep this terminal open; press Ctrl+C to stop.\n\n'
exec "$ROOT/.venv/bin/python" -m deutschflow.main
