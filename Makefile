PYTHON ?= python

.PHONY: setup dev-server dev-extension test lint verify
setup:
	$(PYTHON) -m pip uninstall --yes httpx
	$(PYTHON) -m pip install --require-hashes -r requirements-dev.lock
	$(PYTHON) -m pip install --no-deps -e apps/server
	npm ci
dev-server:
	$(PYTHON) -m deutschflow.main
dev-extension:
	npm run dev:extension
test:
	$(PYTHON) -m pytest apps/server/tests
	npm run test:extension
lint:
	$(PYTHON) -m ruff check apps/server
	npm run typecheck
verify:
	$(PYTHON) -m ruff check apps/server
	$(PYTHON) -m pip check
	$(PYTHON) -m pytest apps/server/tests
	npm run verify:extension
	npm audit --audit-level=high
