# NovaGates Backend & AI Developer Onboarding

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/database-MongoDB%207.0-47A248.svg)](https://www.mongodb.com/)
[![Redis](https://img.shields.io/badge/cache-Redis%207-DC382D.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/container-Docker-2496ED.svg)](https://www.docker.com/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-black.svg)](https://github.com/astral-sh/ruff)

This repository contains the structured deliverables, local infrastructure orchestration, query notebooks, and seed project scaffolds for the **NovaGates 2-Week Backend & AI Developer Programme**.

---

## 🏛️ System Architecture

```mermaid
graph TD
    Client([HTTP / Swagger / User]) -->|REST API| FastAPI[FastAPI Application Layer]
    FastAPI -->|Cache-Aside / Sessions| Redis[(Redis 7 Cache & Broker)]
    FastAPI -->|Async Beanie ODM| Mongo[(MongoDB 7.0 Document Store)]
    
    subgraph Async & Background
        CeleryWorker[Celery Task Worker] -->|Broker| Redis
        CeleryBeat[Celery Beat Scheduler] -->|Every 2h Trigger| CeleryWorker
        CeleryWorker -->|Job Matching| TavilyAPI[Tavily Search API]
    end

    subgraph AI Orchestration
        LangGraphAgent[LangGraph Portfolio Bot] -->|Stateful Tool Calling| FastAPI
        LangGraphAgent -->|Vector Search| Mongo
    end
```

---

## ⚡ Quickstart (One-Command Operations)

We provide a PowerShell task runner [`run.ps1`](file:///d:/Work-orientation/run.ps1) and standard [`Makefile`](file:///d:/Work-orientation/Makefile) for consistent developer experience.

### 1. Start Infrastructure
```powershell
# Windows PowerShell
.\run.ps1 up

# Linux / macOS
make up
```

### 2. Seed Database & Provision Indexes
```powershell
.\run.ps1 seed
```
*Seeds collections (`skills`, `projects`, `experiences`) and automatically provisions unique, compound, and weighted text indexes.*

### 3. Run End-to-End Smoke Verification
```powershell
.\run.ps1 verify
```
*Executes live checks across Docker, MongoDB aggregation pipelines, text search scoring, and Redis TTL / FIFO queues.*

### 4. Code Quality & Linting
```powershell
.\run.ps1 lint
.\run.ps1 format
```

---

## 📁 Repository Layout

```text
d:/Work-orientation/
├── .vscode/                     # Team-standard IDE configurations
│   ├── extensions.json          # Recommended VS Code plugins
│   └── settings.json            # Auto-formatting (Ruff / Black)
├── app/                         # Production FastAPI + Beanie Layered Architecture
│   ├── api/v1/                  # Routers: /skills, /projects, /experiences, /jobs, /ai, /health
│   ├── core/                    # Config (pydantic-settings), db_init, cache, exceptions
│   ├── models/                  # Beanie Document models (Project, Skill, Experience)
│   ├── repositories/            # Generic BaseRepository & Domain Repositories
│   ├── schemas/                 # Pydantic v2 Request & Response models
│   ├── services/                # Business logic, Redis caching, Ollama Cloud & Tavily
│   └── main.py                  # Lifespan application factory
├── tests/                       # Automated pytest suite (HTTPX async test client)
├── deliverables/                # Curriculum deliverables & milestones
│   ├── day1_environment_check.py# Environment diagnostic script
│   ├── sample_seed_data.json    # Reference domain dataset
│   ├── seed_database.py         # Production database seeder & indexer
│   ├── verify_all.py            # End-to-end infrastructure smoke test
│   ├── mongodb_queries.ipynb    # Milestone: Interactive MongoDB Jupyter Notebook
│   ├── mongodb_queries.md       # Milestone: Documented MongoDB query catalogue
│   └── redis_caching_guide.md   # Day 4/5 Redis & Caching reference architecture
├── docker-compose.yml           # Container orchestration (MongoDB 7 & Redis 7)
├── pyproject.toml               # Project metadata & Ruff/pytest configurations
├── .env.example                 # Production configuration blueprint
├── run.ps1                      # PowerShell developer automation script
├── Makefile                     # Cross-platform developer automation
└── README.md                    # System documentation
```

---

## 🎯 Curriculum Milestones & Progress

- [x] **Day 1: Setup & Onboarding** — Tooling validated (Python, `uv`, Git, Docker Desktop).
- [x] **Day 2–3: MongoDB Foundations** — CRUD, filtering, compound indexing, query plans (`explain`), multi-stage aggregations (`$lookup`, `$unwind`), text search, and Atlas vector search.
- [x] **Day 4–5: Redis & Caching** — CLI patterns, TTL invalidation, Cache-Aside pattern, and distributed locking.
- [x] **Day 5–6: Seed Project Scaffold & Core Logic** — FastAPI layered architecture with Beanie ODM, Redis cache, Tavily job search, and Ollama Cloud integration.
- [ ] **Day 6–7: Celery & Tavily Job Retrieval Worker** — Background Celery worker process.
- [ ] **Day 7: Full Stack Containerisation** — Multi-stage Dockerfile and full stack compose.
- [ ] **Day 8–10: LangGraph Portfolio Agent** — Conversational agent with state, memory, and backend tool calling.

---

## 🧪 Testing & Validation Standards

Every pull request must satisfy:
1. `python deliverables/verify_all.py` passes with **0 failures**.
2. Python code adheres to PEP 8 / PEP 604 and passes `ruff check .`.
3. Unit and integration tests cover both happy paths and edge cases (e.g. `NotFound` exceptions).
