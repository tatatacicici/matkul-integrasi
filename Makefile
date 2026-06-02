.PHONY: setup compile install dev format lint clean up down logs migrate migration db-status test-e2e

# Setuptools and pip-tools are equivalent to Composer
setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install pip-tools

# Equivalent to `composer update` — generates locked requirements.txt
compile:
	.venv/bin/pip-compile pyproject.toml -o requirements.txt
	.venv/bin/pip-compile --extra dev pyproject.toml -o requirements-dev.txt

# Equivalent to `composer install`
install:
	.venv/bin/pip-sync requirements-dev.txt
	.venv/bin/pip install -e .

install-prod:
	.venv/bin/pip-sync requirements.txt
	.venv/bin/pip install -e .

# Development server (equivalent to php artisan serve / composer dev)
dev:
	.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Code Formatting & Linting
format:
	ruff format app/

lint:
	ruff check app/

# Docker equivalent scripts
up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache

# ── Database Migration (Alembic) ─────────────────────────────────────────────
# URL untuk koneksi lokal (lewat port forwarding Docker)
DB_URL = postgresql://blog_user:blog_pass@localhost:5433/blog

# Terapkan semua migrasi ke database
migrate:
	DATABASE_URL=$(DB_URL) .venv/bin/alembic upgrade head

# Generate file migrasi baru dari perubahan model
# Usage: make migration m="add_category_to_posts"
migration:
	DATABASE_URL=$(DB_URL) .venv/bin/alembic revision --autogenerate -m "$(m)"

# Cek status migrasi saat ini
db-status:
	@echo "── Current Revision ──"
	@DATABASE_URL=$(DB_URL) .venv/bin/alembic current
	@echo ""
	@echo "── Migration History ──"
	@DATABASE_URL=$(DB_URL) .venv/bin/alembic history --verbose

# Rollback migrasi 1 langkah
db-rollback:
	DATABASE_URL=$(DB_URL) .venv/bin/alembic downgrade -1

# ── E2E Testing (Selenium) ──────────────────────────────────────────────────
# Pastikan Docker services (make up) dan frontend (cd frontend && npm run dev) sudah berjalan
test-e2e:
	.venv/bin/pytest tests/qa/ -v --no-header -x
