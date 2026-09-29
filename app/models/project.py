from __future__ import annotations

from beanie import PydanticObjectId
from pydantic import Field
from pymongo import TEXT, IndexModel

from app.models.base import BaseDocument


class Project(BaseDocument):
    title: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100)
    summary: str = Field(..., min_length=5, max_length=300)
    description: str = Field(default="", max_length=5000)
    featured: bool = Field(default=False)
    status: str = Field(default="completed")
    stars: int = Field(default=0, ge=0)
    skill_ids: list[PydanticObjectId] = Field(default_factory=list)
    embedding: list[float] = Field(default_factory=list)

    class Settings:
        name = "projects"
        indexes = [
            IndexModel([("slug", 1)], unique=True, name="uniq_project_slug"),
            IndexModel(
                [("status", 1), ("stars", -1)], name="idx_projects_status_stars"
            ),
            IndexModel(
                [("title", TEXT), ("summary", TEXT), ("description", TEXT)],
                weights={"title": 10, "summary": 5, "description": 1},
                name="idx_projects_fulltext",
            ),
        ]
