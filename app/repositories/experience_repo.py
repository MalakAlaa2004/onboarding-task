from __future__ import annotations

from app.models.experience import Experience
from app.repositories.base import BaseRepository


class ExperienceRepository(BaseRepository[Experience]):
    def __init__(self) -> None:
        super().__init__(Experience)

    async def get_current(self) -> list[Experience]:
        return await Experience.find(Experience.is_current == True).to_list()  # noqa: E712
