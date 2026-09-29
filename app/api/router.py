from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.agent import router as agent_router
from app.api.v1.ai import router as ai_router
from app.api.v1.experiences import router as exp_router
from app.api.v1.health import router as health_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.projects import router as projects_router
from app.api.v1.skills import router as skills_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(skills_router)
api_router.include_router(projects_router)
api_router.include_router(exp_router)
api_router.include_router(jobs_router)
api_router.include_router(ai_router)
api_router.include_router(agent_router)
