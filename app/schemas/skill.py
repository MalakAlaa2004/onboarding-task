from __future__ import annotations

from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., min_length=1, max_length=50)
    proficiency: int = Field(default=80, ge=1, le=100)
    years_experience: float = Field(default=1.0, ge=0.0)
    tags: list[str] = Field(default_factory=list)


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    proficiency: int | None = Field(default=None, ge=1, le=100)
    years_experience: float | None = Field(default=None, ge=0.0)
    tags: list[str] | None = None


class SkillResponse(SkillBase):
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId
    created_at: datetime
    updated_at: datetime
