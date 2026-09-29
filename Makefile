.PHONY: help up down restart status logs seed verify check-env lint format test dev

help:
	@echo "NovaGates Developer Commands:"
	@echo "  make up         - Start MongoDB & Redis containers"
	@echo "  make down       - Stop containers"
	@echo "  make restart    - Restart containers"
	@echo "  make status     - View running containers"
	@echo "  make logs       - Tail container logs"
	@echo "  make seed       - Seed MongoDB with sample data and build indexes"
	@echo "  make verify     - Run E2E smoke tests on Mongo & Redis"
	@echo "  make check-env  - Validate local environment tools"
	@echo "  make lint       - Run Ruff linter"
	@echo "  make format     - Run Ruff code formatter"
	@echo "  make test       - Run automated pytest test suite"
	@echo "  make dev        - Start local FastAPI server on :8000"

up:
	docker compose up -d
	docker compose ps

down:
	docker compose down

restart:
	docker compose restart
	docker compose ps

status:
	docker compose ps

logs:
	docker compose logs -f

seed:
	python deliverables/seed_database.py

verify:
	python deliverables/verify_all.py

check-env:
	python deliverables/day1_environment_check.py

lint:
	.\.venv\Scripts\ruff check .

format:
	.\.venv\Scripts\ruff format .

test:
	.\.venv\Scripts\pytest -v

dev:
	.\.venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
