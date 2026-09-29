from __future__ import annotations

import logging

from beanie import PydanticObjectId

from app.core.cache import get_cache
from app.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from app.models.skill import Skill
from app.repositories.skill_repo import SkillRepository
from app.schemas.skill import SkillCreate, SkillUpdate

logger = logging.getLogger(__name__)

CACHE_KEY_SKILLS_ALL = "cache:skills:all"


class SkillService:
    def __init__(self, repo: SkillRepository | None = None) -> None:
        self.repo = repo or SkillRepository()

    async def list_skills(self) -> list[Skill]:
        cache = get_cache()
        cached = await cache.get(CACHE_KEY_SKILLS_ALL)
        if cached is not None:
            return [Skill.model_validate(item) for item in cached]

        skills = await self.repo.get_all()
        # Cache list as dicts
        serializable = [skill.model_dump(mode="json") for skill in skills]
        await cache.set(CACHE_KEY_SKILLS_ALL, serializable, ttl=300)
        return skills

    async def get_skill(self, skill_id: PydanticObjectId | str) -> Skill:
        skill = await self.repo.get_by_id(skill_id)
        if not skill:
            raise EntityNotFoundError("Skill", skill_id)
        return skill

    async def create_skill(self, data: SkillCreate) -> Skill:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise EntityAlreadyExistsError("Skill", "name", data.name)

        skill = Skill(**data.model_dump())
        created = await self.repo.create(skill)
        await get_cache().invalidate(CACHE_KEY_SKILLS_ALL)
        return created

    async def update_skill(
        self, skill_id: PydanticObjectId | str, data: SkillUpdate
    ) -> Skill:
        skill = await self.get_skill(skill_id)
        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] != skill.name:
            dup = await self.repo.get_by_name(update_data["name"])
            if dup:
                raise EntityAlreadyExistsError("Skill", "name", update_data["name"])

        for key, val in update_data.items():
            setattr(skill, key, val)

        skill.touch()
        updated = await self.repo.save(skill)
        await get_cache().invalidate(CACHE_KEY_SKILLS_ALL, f"cache:skill:{skill_id}")
        return updated

    async def delete_skill(self, skill_id: PydanticObjectId | str) -> None:
        skill = await self.get_skill(skill_id)
        await self.repo.delete(skill)
        await get_cache().invalidate(CACHE_KEY_SKILLS_ALL, f"cache:skill:{skill_id}")
