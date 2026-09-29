from __future__ import annotations

import logging

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

celery_app = Celery(
    "novagates_tasks",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2",
    include=["app.tasks.job_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Day 6/7 Requirement: Celery Beat scheduled task running every 2 hours
    beat_schedule={
        "periodic-tavily-job-sync": {
            "task": "app.tasks.job_tasks.fetch_matching_jobs_task",
            "schedule": crontab(minute=0, hour="*/2"),
            "args": (),
        },
    },
)
