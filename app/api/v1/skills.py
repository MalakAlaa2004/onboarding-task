from __future__ import annotations

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from app.schemas.common import APIResponse
from app.schemas.skill import SkillCreate, SkillResponse, SkillUpdate
from app.services.skill_service import SkillService

router = APIRouter(prefix="/skills", tags=["Skills"])


def get_skill_service() -> SkillService:
    return SkillService()


@router.get(
    "",
    response_model=APIResponse[list[SkillResponse]],
    summary="List all skills (Cached)",
)
async def list_skills(service: SkillService = Depends(get_skill_service)):
    skills = await service.list_skills()
    return APIResponse(
        data=[SkillResponse.model_validate(s) for s in skills],
        message="Fetched skills successfully.",
    )


@router.get(
    "/{skill_id}", response_model=APIResponse[SkillResponse], summary="Get skill by ID"
)
async def get_skill(
    skill_id: PydanticObjectId, service: SkillService = Depends(get_skill_service)
):
    skill = await service.get_skill(skill_id)
    return APIResponse(
        data=SkillResponse.model_validate(skill),
        message="Skill retrieved.",
    )


@router.post(
    "",
    response_model=APIResponse[SkillResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create skill",
)
async def create_skill(
    data: SkillCreate, service: SkillService = Depends(get_skill_service)
):
    created = await service.create_skill(data)
    return APIResponse(
        data=SkillResponse.model_validate(created),
        message="Skill created successfully.",
    )


@router.put(
    "/{skill_id}", response_model=APIResponse[SkillResponse], summary="Update skill"
)
async def update_skill(
    skill_id: PydanticObjectId,
    data: SkillUpdate,
    service: SkillService = Depends(get_skill_service),
):
    updated = await service.update_skill(skill_id, data)
    return APIResponse(
        data=SkillResponse.model_validate(updated),
        message="Skill updated successfully.",
    )


@router.delete(
    "/{skill_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete skill"
)
async def delete_skill(
    skill_id: PydanticObjectId, service: SkillService = Depends(get_skill_service)
):
    await service.delete_skill(skill_id)
