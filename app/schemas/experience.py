from __future__ import annotations

from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field


class ExperienceBase(BaseModel):
    company: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., min_length=2, max_length=100)
    start_date: str
    end_date: str | None = None
    is_current: bool = False
    technologies: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(BaseModel):
    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool | None = None
    technologies: list[str] | None = None
    responsibilities: list[str] | None = None


class ExperienceResponse(ExperienceBase):
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId
    created_at: datetime
    updated_at: datetime
