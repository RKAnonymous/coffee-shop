from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, views, db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=schemas.UserRead)
async def signup(user: schemas.UserCreate, conn: AsyncSession = Depends(db.get_db)):
    if await views.get_user_by_email(conn, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return await views.create_user(conn, user)

@router.post("/login", response_model=schemas.Token)
async def login(form_data: schemas.UserCreate, conn: AsyncSession = Depends(db.get_db)):
    user = await views.get_user_by_email(conn, form_data.email)
    if not user or not views.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return {
        "access_token": views.create_access_token({"sub": user.email}),
        "refresh_token": views.create_refresh_token({"sub": user.email})
    }

@router.post("/verify", response_model=schemas.UserRead)
async def verify_user_endpoint(data: schemas.VerifyUserSchema, conn: AsyncSession = Depends(db.get_db)):
    user = await views.verify_user(conn, data.email, data.code)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    return user


@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(data: schemas.RefreshTokenSchema):
    try:
        tokens = views.refresh_user_token(data.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e.args))