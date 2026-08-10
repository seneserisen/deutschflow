PYTHON ?= python

.PHONY: setup dev-server dev-extension test lint verify
setup:
	$(PYTHON) -m pip install -e "apps/server[dev]"
	npm install
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
	$(PYTHON) -m pytest apps/server/tests
	npm run verify:extension

