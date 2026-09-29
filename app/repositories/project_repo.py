from __future__ import annotations

from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self) -> None:
        super().__init__(Project)

    async def get_by_slug(self, slug: str) -> Project | None:
        return await Project.find_one(Project.slug == slug)

    async def get_featured(self) -> list[Project]:
        return await Project.find(Project.featured == True).sort("-stars").to_list()  # noqa: E712

    async def search_text(self, query: str, limit: int = 10) -> list[Project]:
        # MongoDB $text search stage
        return await Project.find({"$text": {"$search": query}}).limit(limit).to_list()
