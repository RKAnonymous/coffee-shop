import uuid
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from jose import jwt
from .config import settings
from . import models, schemas


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def verify_password(plain_password: str, hashed_password: str | bytes) -> bool:
    # ensure hashed_password is bytes
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)


def create_access_token(data: dict, expires_minutes: int = 30):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict, expires_days: int = 7):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=expires_days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    hashed_str = hashed_password.decode("utf-8")
    verification_code = str(uuid.uuid4())[:6]
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_str,
        first_name=user.first_name,
        last_name=user.last_name,
        verification_code=verification_code
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    print(f"Verification code for {user.email}: {verification_code}")
    return db_user

async def verify_user(db: AsyncSession, email: str, code: str):
    user = await get_user_by_email(db, email)
    if user and user.verification_code == code:
        user.is_verified = True
        user.verification_code = None
        await db.commit()
        await db.refresh(user)
        return user
    return None
