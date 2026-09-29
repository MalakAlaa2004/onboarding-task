.PHONY: help up down restart status logs seed verify check-env lint format

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
	python -m uv run ruff check .

format:
	python -m uv run ruff format .
