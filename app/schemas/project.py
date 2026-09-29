from __future__ import annotations

from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.skill import SkillResponse


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100)
    summary: str = Field(..., min_length=5, max_length=300)
    description: str = Field(default="", max_length=5000)
    featured: bool = Field(default=False)
    status: str = Field(default="completed")
    stars: int = Field(default=0, ge=0)
    skill_ids: list[PydanticObjectId] = Field(default_factory=list)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    summary: str | None = None
    description: str | None = None
    featured: bool | None = None
    status: str | None = None
    stars: int | None = None
    skill_ids: list[PydanticObjectId] | None = None


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId
    created_at: datetime
    updated_at: datetime


class ProjectDetailResponse(ProjectResponse):
    skills: list[SkillResponse] = Field(default_factory=list)
