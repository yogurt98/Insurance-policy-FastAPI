# app/api/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.limiter import limiter
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token
from app.services.auth import authenticate_user, create_user, create_access_token_from_user

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    # 检查用户是否存在
    existing = await db.execute(select(User).where(User.username == user_in.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")
    user = await create_user(db, user_in)
    return user



@router.post("/login", response_model=Token)
@limiter.limit("10/minute")  # 每分钟最多 10 次
async def login_foe_access_token(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token_from_user(user)
    return {"access_token": access_token, "token_type": "bearer"}














