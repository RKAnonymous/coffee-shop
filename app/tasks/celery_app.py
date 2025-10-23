from celery import Celery
from celery.schedules import crontab
from app.config import settings


celery = Celery(
    settings.PROJECT_NAME,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.user_tasks",
    ],
)

celery.conf.update(
    timezone=settings.TIMEZONE,
    enable_utc=False,
)

# Celery Beat Schedule
celery.conf.beat_schedule = {
    # Runs every midnight
    "delete-unverified-users-every-5-minutes": {
        "task": "app.tasks.user_tasks.delete_unverified_users",
        "schedule": crontab(
            hour=settings.CELERY_UNVERIFIED_USER_CLEANUP_HOUR,
            minute=settings.CELERY_UNVERIFIED_USER_CLEANUP_MINUTE
        ),
    }
}
