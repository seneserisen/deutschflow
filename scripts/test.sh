#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
[ -x "$ROOT/.venv/bin/python" ] || { printf 'ERROR: DeutschFlow is not set up. Run ./setup.sh first.\n' >&2; exit 1; }
exec "$ROOT/scripts/verify.sh"
