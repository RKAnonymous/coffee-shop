import asyncio
from datetime import datetime, timedelta
from sqlalchemy.future import select
from email.message import EmailMessage
from app.config import settings
from app.tasks.celery_app import celery
from app import models
from app.db import AsyncSessionLocal
from app.utils.send_email import async_send_mail


@celery.task
def delete_unverified_users():
    asyncio.run(async_delete_unverified_users())



async def async_delete_unverified_users():
    async with AsyncSessionLocal() as db:
        UNVERIFIED_USER_THRESHOLD = datetime.now(settings.tzinfo) - timedelta(minutes=settings.UNVERIFIED_USER_LIFETIME_MINUTES)

        result = await db.execute(
            select(models.User).filter(
                models.User.is_verified == False,
                models.User.is_deleted == False,
                models.User.created_at < UNVERIFIED_USER_THRESHOLD,
            )
        )
        users = result.scalars().all()
        for user in users:
            user.is_deleted = True
            user.deleted_at = datetime.now(settings.tzinfo)
        await db.commit()
        print(f"Deleted {len(users)} unverified users")


@celery.task
def send_verification_email(email: str, verification_code: str):
    verification_link = f"http://localhost:8000/verify?email={email}&code={verification_code}"

    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = email
    msg["Subject"] = "Verify your Coffee Shop account"

    msg.add_alternative(f"""
<html>
  <body>
    <p>Hi there,</p>
    <p>Please verify your Coffee Shop account by clicking 
       <a href="{verification_link}">this link</a>.</p>
    <p>If you didn't request this, please ignore this email.</p>
    <p>— Coffee Shop Team</p>
  </body>
</html>
    """, subtype="html")

    asyncio.run(async_send_mail(msg))