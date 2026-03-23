# app/celery_worker.py
from celery import Celery
from app.core.config import settings

celery = Celery(
    "policy_tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
    include=["app.tasks"]
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Toronto",
    enable_utc=True,
    task_track_started=True,
)