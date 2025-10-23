from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import views, schemas, models, permissions as deps, db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserRead, dependencies=[Depends(deps.is_authenticated)])
async def get_me(current_user: models.User = Depends(deps.is_authenticated)):
    return current_user


@router.get("/", response_model=List[schemas.UserRead], dependencies=[Depends(deps.is_admin)])
async def get_users(conn: AsyncSession = Depends(db.get_db)):
    result = await conn.execute(select(models.User))
    return result.scalars().all()


@router.get("/{user_id}", response_model=schemas.UserRead, dependencies=[Depends(deps.is_admin)])
async def get_user(user_id: int, conn: AsyncSession = Depends(db.get_db)):
    user = await conn.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=schemas.UserRead, dependencies=[Depends(deps.is_authenticated)])
async def partial_update_user(user_id: int, data: schemas.UserUpdate, conn: AsyncSession = Depends(db.get_db)):
    user = await conn.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(user, key, value)

    await conn.commit()
    await conn.refresh(user)
    return user


@router.delete("/{user_id}", dependencies=[Depends(deps.is_admin)])
async def delete_user(user_id: int, conn: AsyncSession = Depends(db.get_db)):
    user = await conn.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await conn.delete(user)
    await conn.commit()
    return {"detail": "User deleted"}


@router.patch("/{user_id}/role", response_model=schemas.UserRead, dependencies=[Depends(deps.is_admin)])
async def set_user_role_api(data: schemas.UserUpdateRole, conn: AsyncSession = Depends(db.get_db)):
    return await views.set_user_role(conn, data)