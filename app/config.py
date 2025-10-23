from pathlib import Path
from dotenv import load_dotenv
from pydantic import EmailStr, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from zoneinfo import ZoneInfo


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra='ignore'
    )
    PROJECT_NAME: str = "Coffee Shop"
    DATABASE_URL: str
    JWT_SECRET_KEY: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: EmailStr
    SMTP_PASSWORD: str
    SMTP_FROM: EmailStr

    UNVERIFIED_USER_LIFETIME_MINUTES: int = 2880
    TIMEZONE: str = "Asia/Tashkent"

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_UNVERIFIED_USER_CLEANUP_HOUR: int = 0
    CELERY_UNVERIFIED_USER_CLEANUP_MINUTE: int = 0

    @field_validator("TIMEZONE", mode="before")
    def validate_timezone(cls, v):
        try:
            # Accept string, convert to ZoneInfo for internal use
            tz = ZoneInfo(v)
            return v  # keep string in Settings, use property for ZoneInfo
        except Exception:
            raise ValueError(f"Invalid timezone: {v}")

    @property
    def tzinfo(self) -> ZoneInfo:
        return ZoneInfo(self.TIMEZONE)

settings = Settings()
