# app/services/auth.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token
from app.schemas.user import UserCreate, TokenData

async def authenticate_user(
        db:AsyncSession, username: str, password: str
) -> User | None:
    result = await db.execute(select(User).where(username == User.username))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role,
        is_active=True,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


def create_access_token_from_user(user: User) -> str:
    """从用户对象生成 JWT Token"""
    # token_data = TokenData(username=user.username, role=user.role)
    return create_access_token(
        subject=user.username,
        # sub 放 username
        # 可以加更多 claims 如 role，但这里简单起见放 TokenData 里
    )





