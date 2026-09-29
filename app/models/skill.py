from __future__ import annotations

from pydantic import Field
from pymongo import IndexModel

from app.models.base import BaseDocument


class Skill(BaseDocument):
    name: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., min_length=1, max_length=50)
    proficiency: int = Field(default=80, ge=1, le=100)
    years_experience: float = Field(default=1.0, ge=0.0)
    tags: list[str] = Field(default_factory=list)

    class Settings:
        name = "skills"
        indexes = [
            IndexModel([("name", 1)], unique=True, name="uniq_skill_name"),
            IndexModel(
                [("category", 1), ("proficiency", -1)], name="idx_skill_cat_prof"
            ),
        ]
