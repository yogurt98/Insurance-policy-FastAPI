# app/api/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, oauth2_scheme
from app.core.limiter import limiter
from app.middleware.correlation_id import request_id_var
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token
from app.services.auth import authenticate_user, create_user, create_access_token_from_user
from loguru import logger

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
async def login_for_access_token(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    # 1. 绑定日志 ID
    rid = request_id_var.get("no-id")
    log = logger.bind(request_id=rid, user=form_data.username)

    log.info(f"AUTH_IN | Attempting login for user: {form_data.username}")

    # 2. 身份验证
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        log.warning(f"AUTH_FAILED | Invalid credentials for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token_from_user(user)
    log.success(f"AUTH_SUCCESS | User logged in: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(
        request: Request,
        token: str = Depends(oauth2_scheme)
):
    """
    登出逻辑：将当前 Token 加入 Redis 黑名单
    """
    rid = request_id_var.get("no-id")
    log = logger.bind(request_id=rid)

    # 从 app 对象中直接获取 redis 实例
    redis = request.app.state.redis

    # 将 token 存入黑名单，过期时间应与 JWT 的有效期一致（此处默认 1 小时）
    blacklist_key = f"blacklist:{token}"
    await redis.setex(blacklist_key, 3600, "revoked")

    log.info(f"AUTH_OUT | Token added to blacklist | RID: {rid}")

    return {"message": "已成功登出，Token 已失效"}











