import ssl
from email.message import EmailMessage
import aiosmtplib
from app.config import settings


ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def async_send_mail(message: EmailMessage):
    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        tls_context=ssl_context,  # Only in local dev server NOT PROD!!!
    )

