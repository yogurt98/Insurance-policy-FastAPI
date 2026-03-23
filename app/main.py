import sys
import redis.asyncio as aioredis_modern

# 核心魔法：将 aioredis 模块重定向到新版 redis 的异步接口
# 这样当 fastapi-cache2 执行 "import aioredis" 时，实际拿到的是兼容 3.11 的新代码
sys.modules["aioredis"] = aioredis_modern

from fastapi import FastAPI, Depends
from app.core.exceptions import add_exception_handlers
from app.core.limiter import add_rate_limit
from app.core.cache import init_cache
from app.middleware.correlation_id import CorrelationIdMiddleware, request_id_var
from app.api.endpoints import policies, auth, bulk
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

import time

import uuid
from contextvars import ContextVar
from typing import Callable

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

app = FastAPI(
    title="Policy Management API",
    description="A RESTful API for managing insurance policies in a Canadian context",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 注册限流器
add_rate_limit(app)

# 注册统一错误处理器
add_exception_handlers(app)

def patch_record(record):
    # 核心：如果 extra 里没这个键，强行补一个，防止格式化崩溃
    if "request_id" not in record["extra"]:
        record["extra"]["request_id"] = "no-id"


# 1. 清除默认设置
logger.remove()

# 使用 patch 配置（这就是防弹衣）
logger.configure(patcher=patch_record)

# 2. 自定义格式：使用 .get() 确保没有 ID 时也不会崩
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{extra[request_id]}</cyan> - "  # 注意这里显示 request_id
    "<level>{message}</level>"
)

# 3. 添加输出目标
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level="INFO",
    # filter=lambda record: record["extra"].setdefault("request_id", "no-id") or True
)


# 注册 correlation-id 中间件（越早注册越好）
app.add_middleware(CorrelationIdMiddleware)


# include router
app.include_router(policies.router, prefix="/api/v1/policies", tags=["policies"])
app.include_router(bulk.router, prefix="/api/v1/policies", tags=["bulk"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

# exemple root router
@app.get("/")
async def root():
    return {"message": "Welcome to Policy Management API",
            "docs": "/docs",
            "version": settings.VERSION
    }

# 启动时创建表（生产中用Alembic迁移）
# 注意：生产级用Alembic，这里只是骨架
# 在应用启动时初始化（可选，生产中移除）

@app.on_event("startup")
async def startup_event():
    # 就像开机自检
    await init_cache(app)
    print("正在检查数据库状态...")
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    print("系统已就绪！")

