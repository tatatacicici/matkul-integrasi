.PHONY: setup compile install dev format lint clean up down logs

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
