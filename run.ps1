<#
.SYNOPSIS
    NovaGates Developer Automation CLI
.DESCRIPTION
    One-stop task runner for local infrastructure, database seeding, verification, and code quality.
.EXAMPLE
    .\run.ps1 up
    .\run.ps1 seed
    .\run.ps1 verify
    .\run.ps1 lint
#>

param (
    [Parameter(Position = 0, Mandatory = $true)]
    [ValidateSet("up", "down", "restart", "status", "logs", "seed", "verify", "lint", "format", "check-env", "test", "dev")]
    [string]$Command
)

$ErrorActionPreference = "Stop"

function Refresh-Path {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

Refresh-Path

switch ($Command) {
    "up" {
        Write-Host "--> Starting MongoDB & Redis containers in detached mode..." -ForegroundColor Cyan
        docker compose up -d
        docker compose ps
    }
    "down" {
        Write-Host "--> Stopping and removing containers..." -ForegroundColor Yellow
        docker compose down
    }
    "restart" {
        Write-Host "--> Restarting containers..." -ForegroundColor Cyan
        docker compose restart
        docker compose ps
    }
    "status" {
        Write-Host "--> Checking container status..." -ForegroundColor Cyan
        docker compose ps
    }
    "logs" {
        docker compose logs -f
    }
    "seed" {
        Write-Host "--> Seeding local MongoDB with portfolio dataset..." -ForegroundColor Cyan
        .\.venv\Scripts\python deliverables/seed_database.py
    }
    "verify" {
        Write-Host "--> Running end-to-end infrastructure smoke test..." -ForegroundColor Cyan
        .\.venv\Scripts\python deliverables/verify_all.py
    }
    "check-env" {
        .\.venv\Scripts\python deliverables/day1_environment_check.py
    }
    "lint" {
        Write-Host "--> Running Ruff linter..." -ForegroundColor Cyan
        .\.venv\Scripts\ruff check .
    }
    "format" {
        Write-Host "--> Running Ruff code formatter..." -ForegroundColor Cyan
        .\.venv\Scripts\ruff format .
    }
    "test" {
        Write-Host "--> Running automated pytest test suite..." -ForegroundColor Cyan
        .\.venv\Scripts\pytest -v
    }
    "dev" {
        Write-Host "--> Starting FastAPI development server on http://localhost:8000 (Docs: /docs)..." -ForegroundColor Green
        .\.venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    }
}
