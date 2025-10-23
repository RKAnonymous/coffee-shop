from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from . import models, db, config

bearer_scheme = HTTPBearer(auto_error=True)

async def is_authenticated(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    conn: AsyncSession = Depends(db.get_db)
):
    token = credentials.credentials  # just the JWT token
    try:
        payload = jwt.decode(token, config.settings.JWT_SECRET_KEY, algorithms=[config.settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await conn.execute(select(models.User).filter(models.User.email == email))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def is_admin(auth_user: models.User = Depends(is_authenticated)):
    """
    Ensure that the user is an admin
    """
    if auth_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to perform this action",
        )
    return auth_user


async def is_verified(auth_user: models.User = Depends(is_authenticated)):
    """
    Ensure that the current user is verified.
    """
    if not auth_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User email not verified",
        )
    return auth_user