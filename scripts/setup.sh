#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

command -v python3 >/dev/null 2>&1 || fail "Python was not found. Install Python 3.12 or later, then run ./setup.sh again."
python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)' || fail "Python 3.12 or later is required."
command -v node >/dev/null 2>&1 || fail "Node.js was not found. Install Node.js 24 LTS (24.15 or later)."
node -e 'const [major, minor] = process.versions.node.split(".").map(Number); process.exit((major === 24 && minor >= 15) || major >= 26 ? 0 : 1)' || fail "Node.js 24.15+ in the Node 24 line, or Node.js 26+, is required."
command -v npm >/dev/null 2>&1 || fail "npm was not found. It is normally installed with Node.js."

if [ ! -x "$ROOT/.venv/bin/python" ]; then
  printf 'Creating the local Python environment...\n'
  python3 -m venv "$ROOT/.venv"
else
  printf 'Existing .venv detected.\n'
fi

"$ROOT/.venv/bin/python" -m pip install -e "$ROOT/apps/server[dev]"
npm ci
npm run build
printf '\nDeutschFlow setup completed successfully.\nNext: run ./run.sh and follow START_HERE.md.\n'
