# app/celery_worker.py
import os
from celery import Celery
from app.core.config import settings

# 动态读取 REDIS_HOST，如果没有环境变量则默认使用 docker-compose 的 "redis"
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

celery = Celery(
    "policy_tasks",
    broker=f"redis://{REDIS_HOST}:6379/0",  # ✅ 动态组装 URL
    backend=f"redis://{REDIS_HOST}:6379/1",  # ✅ 动态组装 URL
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