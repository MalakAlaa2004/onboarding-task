from __future__ import annotations

from beanie import PydanticObjectId

from app.core.exceptions import EntityNotFoundError
from app.models.experience import Experience
from app.repositories.experience_repo import ExperienceRepository
from app.schemas.experience import ExperienceCreate, ExperienceUpdate


class ExperienceService:
    def __init__(self, repo: ExperienceRepository | None = None) -> None:
        self.repo = repo or ExperienceRepository()

    async def list_experiences(self, current_only: bool = False) -> list[Experience]:
        if current_only:
            return await self.repo.get_current()
        return await self.repo.get_all()

    async def get_experience(self, exp_id: PydanticObjectId | str) -> Experience:
        exp = await self.repo.get_by_id(exp_id)
        if not exp:
            raise EntityNotFoundError("Experience", exp_id)
        return exp

    async def create_experience(self, data: ExperienceCreate) -> Experience:
        exp = Experience(**data.model_dump())
        return await self.repo.create(exp)

    async def update_experience(
        self, exp_id: PydanticObjectId | str, data: ExperienceUpdate
    ) -> Experience:
        exp = await self.get_experience(exp_id)
        for key, val in data.model_dump(exclude_unset=True).items():
            setattr(exp, key, val)
        exp.touch()
        return await self.repo.save(exp)

    async def delete_experience(self, exp_id: PydanticObjectId | str) -> None:
        exp = await self.get_experience(exp_id)
        await self.repo.delete(exp)
