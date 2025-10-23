from .celery_app import celery
from . import user_tasks

__all__ = ["celery"]
