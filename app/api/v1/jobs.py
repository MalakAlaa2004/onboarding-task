from __future__ import annotations

from fastapi import APIRouter, Depends

from app.schemas.common import APIResponse
from app.schemas.job import JobMatchRequest, JobMatchResponse
from app.services.job_service import JobMatchingService

router = APIRouter(prefix="/jobs", tags=["Jobs & Tavily Search"])


def get_job_service() -> JobMatchingService:
    return JobMatchingService()


@router.post(
    "/match",
    response_model=APIResponse[JobMatchResponse],
    summary="Match jobs to portfolio using Tavily",
)
async def match_jobs(
    request: JobMatchRequest | None = None,
    service: JobMatchingService = Depends(get_job_service),
):
    query = request.query if request else None
    max_results = request.max_results if request else 5
    result = await service.retrieve_matching_jobs(
        custom_query=query, max_results=max_results
    )
    return APIResponse(
        data=result,
        message="Retrieved matching live job postings.",
    )


@router.post(
    "/sync-task",
    summary="Trigger asynchronous background Tavily job search via Celery",
)
async def trigger_job_sync_task(request: JobMatchRequest | None = None):
    from app.tasks.job_tasks import fetch_matching_jobs_task

    query = request.query if request else None
    max_results = request.max_results if request else 5

    task = fetch_matching_jobs_task.delay(query=query, max_results=max_results)
    return {
        "success": True,
        "task_id": task.id,
        "status": "QUEUED",
        "message": "Background job matching task dispatched to Celery worker queue.",
    }
