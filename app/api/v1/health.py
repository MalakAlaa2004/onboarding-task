from __future__ import annotations

from fastapi import APIRouter

from app.core.cache import get_cache
from app.core.config import get_settings
from app.core.db_init import DatabaseManager

router = APIRouter(prefix="/health", tags=["Health & Diagnostics"])


@router.get("", summary="Liveness Probe")
async def liveness():
    settings = get_settings()
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/ready", summary="Readiness Probe (Verifies DB & Cache)")
async def readiness():
    db_ok = False
    cache_ok = False

    # Check MongoDB
    try:
        if DatabaseManager.client:
            res = await DatabaseManager.client.admin.command("ping")
            db_ok = res.get("ok") == 1.0 or res.get("ok") == 1
    except Exception:
        db_ok = False

    # Check Redis
    try:
        cache = get_cache()
        if cache.client:
            cache_ok = await cache.client.ping()
    except Exception:
        cache_ok = False

    return {
        "ready": db_ok and cache_ok,
        "database": "connected" if db_ok else "disconnected",
        "cache": "connected" if cache_ok else "disconnected",
    }
