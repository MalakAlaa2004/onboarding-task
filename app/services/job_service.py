from __future__ import annotations

import logging

import httpx

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.models.skill import Skill
from app.schemas.job import JobItem, JobMatchResponse

logger = logging.getLogger(__name__)


class JobMatchingService:
    def __init__(self, api_key: str | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.endpoint = "https://api.tavily.com/search"

    async def retrieve_matching_jobs(
        self, custom_query: str | None = None, max_results: int = 5
    ) -> JobMatchResponse:
        """Queries Tavily API for job posts matching top developer portfolio skills."""
        if not self.api_key:
            raise ExternalServiceError(
                "Tavily",
                "TAVILY_API_KEY is not configured in .env. Set your key to enable live job search.",
            )

        if not custom_query:
            # Dynamically derive query from highest proficiency skills
            top_skills = await Skill.find().sort("-proficiency").limit(4).to_list()
            skill_keywords = (
                " ".join([s.name for s in top_skills]) or "Python FastAPI Backend"
            )
            search_query = (
                f"{skill_keywords} remote junior backend developer jobs hiring"
            )
        else:
            search_query = custom_query

        logger.info("Executing Tavily job retrieval with query: '%s'", search_query)

        payload = {
            "api_key": self.api_key,
            "query": search_query,
            "search_depth": "advanced",
            "include_domains": [
                "linkedin.com",
                "indeed.com",
                "remoteok.com",
                "weworkremotely.com",
            ],
            "max_results": max_results,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(self.endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                logger.error(
                    "Tavily HTTP error (%s): %s",
                    e.response.status_code,
                    e.response.text,
                )
                raise ExternalServiceError(
                    "Tavily", f"API returned status {e.response.status_code}"
                ) from e
            except Exception as e:
                logger.error("Tavily network request failed: %s", e)
                raise ExternalServiceError("Tavily", str(e)) from e

        results = data.get("results", [])
        matches = [
            JobItem(
                title=item.get("title", "Untitled Position"),
                url=item.get("url", ""),
                content=item.get("content", ""),
                score=item.get("score"),
            )
            for item in results
        ]

        return JobMatchResponse(
            query_used=search_query,
            total_found=len(matches),
            matches=matches,
        )
