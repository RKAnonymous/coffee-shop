import uuid
import bcrypt
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from jose import jwt, JWTError
from .config import settings
from . import models, schemas
from app.tasks.user_tasks import send_verification_email


def get_password_hash(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def verify_password(plain_password: str, hashed_password: str | bytes) -> bool:
    # ensure hashed_password is bytes
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)


def create_access_token(data: dict, expires_minutes: int = 30):
    to_encode = data.copy()
    expire = datetime.now(settings.tzinfo) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict, expires_days: int = 7):
    to_encode = data.copy()
    expire = datetime.now(settings.tzinfo) + timedelta(days=expires_days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def refresh_user_token(refresh_token: str) -> dict:
    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise ValueError("Invalid refresh token: no subject")
    except JWTError:
        raise ValueError("Invalid refresh token")

    access_token = create_access_token({"sub": email})
    new_refresh_token = create_refresh_token({"sub": email})
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token
    }


async def get_user_by_email(session: AsyncSession, email: str):
    result = await session.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

async def create_user(session: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    hashed_str = hashed_password.decode("utf-8")
    verification_code = str(uuid.uuid4())[:6]
    session_user = models.User(
        email=user.email,
        hashed_password=hashed_str,
        first_name=user.first_name,
        last_name=user.last_name,
        verification_code=verification_code
    )
    session.add(session_user)
    await session.commit()
    await session.refresh(session_user)
    send_verification_email.delay(session_user.email, verification_code)
    print(f"Verification code for {user.email}: {verification_code}")
    return session_user


async def verify_user(session: AsyncSession, email: str, code: str):
    user = await get_user_by_email(session, email)
    if user and user.verification_code == code:
        user.is_verified = True
        user.verification_code = None
        await session.commit()
        await session.refresh(user)
        return user
    return None


async def set_user_role(session: AsyncSession, data: schemas.UserUpdateRole) -> models.User:
    user_id = data.user_id
    role = data.role

    user = await session.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if role not in ("admin", "user"):
        raise HTTPException(status_code=403, detail="Invalid role")

    user.role = role
    await session.commit()
    await session.refresh(user)
    return user