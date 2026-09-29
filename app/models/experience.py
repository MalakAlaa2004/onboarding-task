from __future__ import annotations

from pydantic import Field
from pymongo import IndexModel

from app.models.base import BaseDocument


class Experience(BaseDocument):
    company: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., min_length=2, max_length=100)
    start_date: str = Field(..., description="YYYY-MM-DD or YYYY-MM")
    end_date: str | None = Field(default=None, description="None if current role")
    is_current: bool = Field(default=False)
    technologies: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)

    class Settings:
        name = "experiences"
        indexes = [
            IndexModel(
                [("is_current", -1), ("company", 1)], name="idx_exp_current_company"
            ),
        ]
