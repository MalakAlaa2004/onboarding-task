from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.schemas.common import APIResponse
from app.services.ai_service import OllamaCloudClient
from app.services.project_service import ProjectService
from app.services.skill_service import SkillService

router = APIRouter(prefix="/ai", tags=["AI & Ollama Cloud"])


class BioResponse(BaseModel):
    summary: str
    model: str
    provider: str = "Ollama Cloud"


def get_ai_client() -> OllamaCloudClient:
    return OllamaCloudClient()


def get_skill_service() -> SkillService:
    return SkillService()


def get_project_service() -> ProjectService:
    return ProjectService()


@router.post(
    "/bio",
    response_model=APIResponse[BioResponse],
    summary="Generate executive developer pitch using Ollama Cloud",
)
async def generate_bio(
    ai_client: OllamaCloudClient = Depends(get_ai_client),
    skill_service: SkillService = Depends(get_skill_service),
    project_service: ProjectService = Depends(get_project_service),
):
    # Fetch live skills and projects from database
    skills = await skill_service.list_skills()
    projects = await project_service.list_projects(featured_only=True)

    skill_names = [s.name for s in skills[:6]]
    project_titles = [f"{p.title} ({p.summary})" for p in projects[:3]]

    summary = await ai_client.generate_portfolio_bio(
        skills=skill_names, projects=project_titles
    )
    return APIResponse(
        data=BioResponse(
            summary=summary,
            model=ai_client.default_model,
        ),
        message="AI executive bio generated via Ollama Cloud.",
    )
