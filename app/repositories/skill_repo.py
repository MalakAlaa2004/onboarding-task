from __future__ import annotations

from app.models.skill import Skill
from app.repositories.base import BaseRepository


class SkillRepository(BaseRepository[Skill]):
    def __init__(self) -> None:
        super().__init__(Skill)

    async def get_by_name(self, name: str) -> Skill | None:
        return await Skill.find_one(Skill.name == name)

    async def get_by_category(self, category: str) -> list[Skill]:
        return await Skill.find(Skill.category == category).to_list()
