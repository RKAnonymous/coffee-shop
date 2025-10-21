import asyncio
from celery import Celery
from datetime import datetime, timedelta
from .db import AsyncSessionLocal
from . import models
from sqlalchemy.future import select

celery_app = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

async def async_delete_unverified_users():
    async with AsyncSessionLocal() as db:
        threshold = datetime.utcnow() - timedelta(days=2)
        result = await db.execute(select(models.User).filter(models.User.is_verified==False, models.User.created_at<threshold))
        users = result.scalars().all()
        for user in users:
            await db.delete(user)
        await db.commit()

@celery_app.task
def delete_unverified_users():
    asyncio.run(async_delete_unverified_users())
