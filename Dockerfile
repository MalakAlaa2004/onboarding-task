# syntax=docker/dockerfile:1
# Multi-stage production build for NovaGates Portfolio API & Worker

# Stage 1: Dependency Builder
FROM ghcr.io/astral-sh/uv:0.5.21 AS uv-source
FROM python:3.10-slim AS builder

WORKDIR /app
COPY --from=uv-source /uv /uvx /bin/

# Copy dependency specifications
COPY pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python --no-cache \
        fastapi "uvicorn[standard]" beanie motor pydantic pydantic-settings redis httpx celery langgraph langchain-core langchain-openai

# Stage 2: Lean Production Runtime
FROM python:3.10-slim AS runtime

# Security: Create non-root execution user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application source code
COPY --chown=appuser:appuser app /app/app
COPY --chown=appuser:appuser pyproject.toml /app/

USER appuser

EXPOSE 8000

# Default runtime command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
