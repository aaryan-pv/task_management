from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "task_management_worker",

    broker=(
        f"redis://"
        f"{settings.REDIS_HOST}:"
        f"{settings.REDIS_PORT}/0"
    ),

    backend=(
        f"redis://"
        f"{settings.REDIS_HOST}:"
        f"{settings.REDIS_PORT}/0"
    ),

    include=[
        "app.workers.task_worker"
    ]
)


celery_app.conf.update(

    task_serializer="json",

    accept_content=["json"],

    result_serializer="json",

    timezone="UTC",

    enable_utc=True,

    task_track_started=True,

    task_time_limit=30 * 60
)