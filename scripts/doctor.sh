#!/usr/bin/env sh
set -u
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
FAILURES=0

ok() { printf '%-25s %-7s %s\n' "$1" "OK" "$2"; }
warn() { printf '%-25s %-7s %s\n' "$1" "WARN" "$2"; }
info() { printf '%-25s %-7s %s\n' "$1" "INFO" "$2"; }
fail() { printf '%-25s %-7s %s\n' "$1" "ERROR" "$2"; FAILURES=$((FAILURES + 1)); }

printf 'DeutschFlow environment check\nRepository: %s\n\n' "$ROOT"
if command -v python3 >/dev/null 2>&1; then
  if python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)'; then ok "Python" "$(python3 --version 2>&1)"; else fail "Python" "Python 3.12 or later is required."; fi
else fail "Python" "Not found. Install Python 3.12 or later."; fi
if command -v node >/dev/null 2>&1; then
  if node -e 'const [major, minor] = process.versions.node.split(".").map(Number); process.exit((major === 24 && minor >= 15) || major >= 26 ? 0 : 1)'; then ok "Node.js" "$(node --version)"; else fail "Node.js" "Node.js 24.15+ in the Node 24 line, or Node.js 26+, is required."; fi
else fail "Node.js" "Not found. Install Node.js 24 LTS (24.15 or later)."; fi
if command -v npm >/dev/null 2>&1; then ok "npm" "$(npm --version)"; else fail "npm" "Not found."; fi
[ -f "$ROOT/requirements-dev.lock" ] && ok "Python dependency lock" "requirements-dev.lock" || fail "Python dependency lock" "Missing; restore it from Git."
if [ -x "$ROOT/.venv/bin/python" ]; then
  ok "Virtual environment" ".venv"
  if "$ROOT/.venv/bin/python" -c 'from importlib.metadata import version; import deutschflow, fastapi, sqlalchemy, uvicorn; assert version("httpx2")' 2>/dev/null; then ok "Python package" "Runtime imports and test client succeeded."; else fail "Python package" "Incomplete; run ./setup.sh again."; fi
else fail "Virtual environment" "Missing; run ./setup.sh."; fi
[ -d "$ROOT/node_modules" ] && ok "Extension dependencies" "node_modules exists." || fail "Extension dependencies" "Missing; run ./setup.sh."
[ -f "$ROOT/apps/extension/dist/manifest.json" ] && ok "Extension build" "dist/manifest.json exists." || fail "Extension build" "Missing; run ./setup.sh or ./run.sh."
if [ -d "$ROOT/artifacts" ] && [ -w "$ROOT/artifacts" ]; then ok "Artifacts directory" "Writable."; else fail "Artifacts directory" "Missing or not writable."; fi
if command -v git >/dev/null 2>&1 && git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  ok "Git repository" "Local repository detected."
  BRANCH=$(git -C "$ROOT" branch --show-current 2>/dev/null || true)
  ok "Git branch" "${BRANCH:-No branch name yet.}"
  REMOTE=$(git -C "$ROOT" remote get-url origin 2>/dev/null || true)
  if [ -n "$REMOTE" ]; then ok "Git remote" "$REMOTE"; else warn "Git remote" "No origin configured; add one deliberately when ready."; fi
else warn "Git" "Git repository information is unavailable; runtime use still works."; fi
if command -v curl >/dev/null 2>&1; then
  if curl --fail --silent --show-error --max-time 2 http://127.0.0.1:43131/api/v1/health >/dev/null 2>&1; then ok "Local service" "Running."; else info "Local service" "Not running; ./run.sh starts it."; fi
else info "Local service" "Not checked because curl is unavailable."; fi
if [ "$FAILURES" -gt 0 ]; then printf '\n%s required check(s) failed.\n' "$FAILURES"; exit 1; fi
printf '\nAll required environment checks passed.\n'
