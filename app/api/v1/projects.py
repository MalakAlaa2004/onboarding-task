from __future__ import annotations

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query, status

from app.schemas.common import APIResponse
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


def get_project_service() -> ProjectService:
    return ProjectService()


@router.get(
    "",
    response_model=APIResponse[list[ProjectResponse]],
    summary="List projects (Cached / Searchable)",
)
async def list_projects(
    featured: bool = Query(default=False, description="Filter featured projects only"),
    q: str | None = Query(
        default=None, description="Full-text search query across title and summary"
    ),
    service: ProjectService = Depends(get_project_service),
):
    projects = await service.list_projects(featured_only=featured, query=q)
    return APIResponse(
        data=[ProjectResponse.model_validate(p) for p in projects],
        message="Fetched projects successfully.",
    )


@router.get(
    "/{project_id}",
    response_model=APIResponse[ProjectResponse],
    summary="Get project by ID or Slug",
)
async def get_project(
    project_id: str, service: ProjectService = Depends(get_project_service)
):
    project = await service.get_project(project_id)
    return APIResponse(
        data=ProjectResponse.model_validate(project),
        message="Project retrieved successfully.",
    )


@router.get(
    "/{project_id}/detail",
    response_model=APIResponse[ProjectDetailResponse],
    summary="Get project with resolved skill details",
)
async def get_project_detail(
    project_id: str, service: ProjectService = Depends(get_project_service)
):
    detail = await service.get_project_detail(project_id)
    return APIResponse(
        data=detail,
        message="Project detail with populated skills retrieved.",
    )


@router.post(
    "",
    response_model=APIResponse[ProjectResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
)
async def create_project(
    data: ProjectCreate, service: ProjectService = Depends(get_project_service)
):
    created = await service.create_project(data)
    return APIResponse(
        data=ProjectResponse.model_validate(created),
        message="Project created successfully.",
    )


@router.put(
    "/{project_id}",
    response_model=APIResponse[ProjectResponse],
    summary="Update project",
)
async def update_project(
    project_id: PydanticObjectId,
    data: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
):
    updated = await service.update_project(project_id, data)
    return APIResponse(
        data=ProjectResponse.model_validate(updated),
        message="Project updated successfully.",
    )


@router.delete(
    "/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete project"
)
async def delete_project(
    project_id: PydanticObjectId, service: ProjectService = Depends(get_project_service)
):
    await service.delete_project(project_id)
