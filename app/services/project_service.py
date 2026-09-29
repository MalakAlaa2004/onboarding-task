from __future__ import annotations

import logging
from typing import Any

from beanie import PydanticObjectId

from app.core.cache import get_cache
from app.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from app.models.project import Project
from app.models.skill import Skill
from app.repositories.project_repo import ProjectRepository
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.schemas.skill import SkillResponse

logger = logging.getLogger(__name__)

CACHE_KEY_PROJECTS_ALL = "cache:projects:all"


class ProjectService:
    def __init__(self, repo: ProjectRepository | None = None) -> None:
        self.repo = repo or ProjectRepository()

    async def list_projects(
        self, featured_only: bool = False, query: str | None = None
    ) -> list[Project]:
        if query:
            return await self.repo.search_text(query)

        cache = get_cache()
        cache_key = f"{CACHE_KEY_PROJECTS_ALL}:featured={featured_only}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return [Project.model_validate(p) for p in cached]

        if featured_only:
            projects = await self.repo.get_featured()
        else:
            projects = await self.repo.get_all()

        serializable = [p.model_dump(mode="json") for p in projects]
        await cache.set(cache_key, serializable, ttl=300)
        return projects

    async def get_project(self, project_id: PydanticObjectId | str) -> Project:
        cache_key = f"cache:project:{project_id}"
        cached = await get_cache().get(cache_key)
        if cached is not None:
            return Project.model_validate(cached)

        project = await self.repo.get_by_id(project_id)
        if not project:
            # Fallback checking slug
            project = await self.repo.get_by_slug(str(project_id))
        if not project:
            raise EntityNotFoundError("Project", project_id)

        await get_cache().set(cache_key, project.model_dump(mode="json"), ttl=300)
        return project

    async def get_project_detail(
        self, project_id: PydanticObjectId | str
    ) -> ProjectDetailResponse:
        project = await self.get_project(project_id)
        skills: list[SkillResponse] = []

        if project.skill_ids:
            found_skills = await Skill.find(
                {"_id": {"$in": project.skill_ids}}
            ).to_list()
            skills = [SkillResponse.model_validate(s) for s in found_skills]

        base_dict = ProjectResponse.model_validate(project).model_dump()
        return ProjectDetailResponse(**base_dict, skills=skills)

    async def create_project(self, data: ProjectCreate) -> Project:
        existing = await self.repo.get_by_slug(data.slug)
        if existing:
            raise EntityAlreadyExistsError("Project", "slug", data.slug)

        project = Project(**data.model_dump())
        created = await self.repo.create(project)
        await self._invalidate_caches()
        return created

    async def update_project(
        self, project_id: PydanticObjectId | str, data: ProjectUpdate
    ) -> Project:
        project = await self.get_project(project_id)
        update_data = data.model_dump(exclude_unset=True)

        if "slug" in update_data and update_data["slug"] != project.slug:
            dup = await self.repo.get_by_slug(update_data["slug"])
            if dup:
                raise EntityAlreadyExistsError("Project", "slug", update_data["slug"])

        for key, val in update_data.items():
            setattr(project, key, val)

        project.touch()
        updated = await self.repo.save(project)
        await self._invalidate_caches(project_id, project.slug)
        return updated

    async def delete_project(self, project_id: PydanticObjectId | str) -> None:
        project = await self.get_project(project_id)
        await self.repo.delete(project)
        await self._invalidate_caches(project_id, project.slug)

    async def _invalidate_caches(self, *extra_keys: Any) -> None:
        keys = [
            f"{CACHE_KEY_PROJECTS_ALL}:featured=True",
            f"{CACHE_KEY_PROJECTS_ALL}:featured=False",
        ]
        for extra in extra_keys:
            if extra:
                keys.append(f"cache:project:{extra}")
        await get_cache().invalidate(*keys)
