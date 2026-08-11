import os
from celery import Celery

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")
redis_url = f"redis://{redis_host}:{redis_port}/0"

celery_app = Celery(
    "chesscoach_tasks",
    broker=redis_url,
    backend=redis_url,
    include=["app.tasks.engine"]  # We'll build worker tasks here later
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)