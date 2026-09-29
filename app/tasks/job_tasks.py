from __future__ import annotations

import asyncio
import logging

from app.core.celery_app import celery_app
from app.services.job_service import JobMatchingService

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.job_tasks.fetch_matching_jobs_task", bind=True, max_retries=3
)
def fetch_matching_jobs_task(
    self, query: str | None = None, max_results: int = 5
) -> dict:
    """Background task executed every 2 hours (or on-demand) via Celery."""
    logger.info(
        "Celery task started: fetch_matching_jobs_task (id: %s)", self.request.id
    )

    async def _run():
        service = JobMatchingService()
        result = await service.retrieve_matching_jobs(
            custom_query=query, max_results=max_results
        )
        return result.model_dump(mode="json")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        output = loop.run_until_complete(_run())
        loop.close()
        logger.info("Celery task %s completed successfully.", self.request.id)
        return output
    except Exception as exc:
        logger.error("Celery task failed with error: %s. Scheduling retry...", exc)
        raise self.retry(exc=exc, countdown=60) from exc
