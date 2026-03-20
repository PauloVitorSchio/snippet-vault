DC = docker compose

# ── Docker lifecycle ──────────────────────────────────────────────────────────

.PHONY: build
build:
	$(DC) build

.PHONY: up
up:
	$(DC) up

.PHONY: up-build
up-build:
	$(DC) up --build

.PHONY: down
down:
	$(DC) down

.PHONY: logs
logs:
	$(DC) logs -f api

# ── Django management ─────────────────────────────────────────────────────────

.PHONY: migrate
migrate:
	$(DC) exec api python manage.py migrate

.PHONY: makemigrations
makemigrations:
	$(DC) exec api python manage.py makemigrations

.PHONY: superuser
superuser:
	$(DC) exec api python manage.py createsuperuser

.PHONY: shell
shell:
	$(DC) exec api python manage.py shell

# ── Testing ───────────────────────────────────────────────────────────────────

.PHONY: test
test:
	$(DC) exec api pytest

.PHONY: test-cov
test-cov:
	$(DC) exec api pytest --cov --cov-report=term-missing

# ── Shells ────────────────────────────────────────────────────────────────────

.PHONY: bash
bash:
	$(DC) exec api bash

.PHONY: psql
psql:
	$(DC) exec postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB

# ── Linting & formatting ──────────────────────────────────────────────────────

.PHONY: lint
lint:
	uv run ruff check .

.PHONY: lint-fix
lint-fix:
	uv run ruff check --fix .

.PHONY: format
format:
	uv run ruff format .

.PHONY: format-check
format-check:
	uv run ruff format --check .

# ── Local dev (host) ──────────────────────────────────────────────────────────

.PHONY: install
install:
	uv sync && uv run pre-commit install
