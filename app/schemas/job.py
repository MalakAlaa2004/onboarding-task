from __future__ import annotations

from pydantic import BaseModel, Field


class JobMatchRequest(BaseModel):
    query: str | None = Field(
        default=None, description="Custom search query; defaults to portfolio skills"
    )
    max_results: int = Field(default=5, ge=1, le=20)


class JobItem(BaseModel):
    title: str
    url: str
    content: str
    score: float | None = None


class JobMatchResponse(BaseModel):
    query_used: str
    total_found: int
    matches: list[JobItem]
    source: str = "Tavily Live Search"
