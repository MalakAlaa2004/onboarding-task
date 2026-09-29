from __future__ import annotations

import pytest

from app.core.celery_app import celery_app


def test_celery_task_registration():
    from app.tasks.job_tasks import fetch_matching_jobs_task

    assert fetch_matching_jobs_task.name in celery_app.tasks
    assert "periodic-tavily-job-sync" in celery_app.conf.beat_schedule


@pytest.mark.asyncio
async def test_celery_trigger_endpoint(async_client):
    res = await async_client.post("/api/v1/jobs/sync-task", json={"max_results": 2})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "task_id" in data
    assert data["status"] == "QUEUED"
