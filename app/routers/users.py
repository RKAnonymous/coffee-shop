from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import schemas, db, models, deps

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserRead)
async def get_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user

@router.get("/", response_model=List[schemas.UserRead])
async def get_users(conn: AsyncSession = Depends(db.get_db), admin: models.User = Depends(deps.admin_required)):
    result = await conn.execute(select(models.User))
    return result.scalars().all()

@router.get("/{user_id}", response_model=schemas.UserRead)
async def get_user(user_id: int, conn: AsyncSession = Depends(db.get_db), admin: models.User = Depends(deps.admin_required)):
    user = await conn.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=schemas.UserRead)
async def update_user(user_id: int, data: schemas.UserUpdate, conn: AsyncSession = Depends(db.get_db), admin: models.User = Depends(deps.admin_required)):
    user = await conn.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    await conn.commit()
    await conn.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: int, conn: AsyncSession = Depends(db.get_db), admin: models.User = Depends(deps.admin_required)):
    user = await conn.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await conn.delete(user)
    await conn.commit()
    return {"detail": "User deleted"}
