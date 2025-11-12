"""Celery configuration for async task processing."""
from celery import Celery
from config.settings import settings

celery_app = Celery(
    "csirt",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "pipeline.tasks",
        "alerts.tasks",
        "integrations.tasks",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    beat_schedule={
        "collect-events": {
            "task": "pipeline.tasks.collect_events_from_sources",
            "schedule": 300.0,  # Every 5 minutes
        },
        "correlate-events": {
            "task": "pipeline.tasks.correlate_events",
            "schedule": 600.0,  # Every 10 minutes
        },
    },
)

