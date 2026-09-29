from __future__ import annotations

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query, status

from app.schemas.common import APIResponse
from app.schemas.experience import (
    ExperienceCreate,
    ExperienceResponse,
    ExperienceUpdate,
)
from app.services.experience_service import ExperienceService

router = APIRouter(prefix="/experiences", tags=["Experiences"])


def get_exp_service() -> ExperienceService:
    return ExperienceService()


@router.get(
    "",
    response_model=APIResponse[list[ExperienceResponse]],
    summary="List career experiences",
)
async def list_experiences(
    current_only: bool = Query(
        default=False, description="Filter currently active roles only"
    ),
    service: ExperienceService = Depends(get_exp_service),
):
    items = await service.list_experiences(current_only=current_only)
    return APIResponse(
        data=[ExperienceResponse.model_validate(x) for x in items],
        message="Fetched experiences successfully.",
    )


@router.get(
    "/{exp_id}",
    response_model=APIResponse[ExperienceResponse],
    summary="Get experience by ID",
)
async def get_experience(
    exp_id: PydanticObjectId, service: ExperienceService = Depends(get_exp_service)
):
    item = await service.get_experience(exp_id)
    return APIResponse(
        data=ExperienceResponse.model_validate(item),
        message="Experience retrieved.",
    )


@router.post(
    "",
    response_model=APIResponse[ExperienceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create experience",
)
async def create_experience(
    data: ExperienceCreate, service: ExperienceService = Depends(get_exp_service)
):
    created = await service.create_experience(data)
    return APIResponse(
        data=ExperienceResponse.model_validate(created),
        message="Experience created successfully.",
    )


@router.put(
    "/{exp_id}",
    response_model=APIResponse[ExperienceResponse],
    summary="Update experience",
)
async def update_experience(
    exp_id: PydanticObjectId,
    data: ExperienceUpdate,
    service: ExperienceService = Depends(get_exp_service),
):
    updated = await service.update_experience(exp_id, data)
    return APIResponse(
        data=ExperienceResponse.model_validate(updated),
        message="Experience updated successfully.",
    )


@router.delete(
    "/{exp_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete experience"
)
async def delete_experience(
    exp_id: PydanticObjectId, service: ExperienceService = Depends(get_exp_service)
):
    await service.delete_experience(exp_id)
