# app/tests/conftest.py
import pytest, os
import asyncio

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool  # ✅ 引入 NullPool 禁用测试连接池
from app.api.deps import get_db

from app.core.config import settings
from app.db.base import Base
from app.main import app, init_cache
from httpx import ASGITransport, AsyncClient


# 测试数据库使用单独的数据库，避免污染开发数据
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/policy_db"
)
# @pytest.fixture(scope="session")
# def event_loop():
#     """管理整个 session 的事件循环，防止 Loop 冲突"""
#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Session 级别：初始化数据库表"""
    # ✅ 使用 NullPool，防止测试间连接池污染
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

# @pytest_asyncio.fixture(scope="session")
# async def test_engine():
#     """测试用数据库引擎"""
#     engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     yield engine
#     await engine.dispose()


@pytest_asyncio.fixture
async def test_db():
    """为每个测试提供独立的 Session，并自动回滚"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback() # ✅ 关键：每个测试后回滚，保证互不干扰
    await engine.dispose()

@pytest_asyncio.fixture
async def client(test_db):
    """Async HTTP 客户端"""
    # ✅ 最关键一步：依赖注入覆盖！让 FastAPI 内部使用测试生成的 session
    async def override_get_db():
        yield test_db
    app.dependency_overrides[get_db] = override_get_db
    # 手动触发缓存初始化，并捕获可能的连接错误
    try:
        await init_cache(app)
    except Exception:
        pass

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_token(client):
    """自动注册并登录，返回 token 字符串"""
    user_data = {
        "username": "testadmin",
        "email": "admin@test.com",
        "role": "admin",
        "password": "Password123!"
    }
    # 注册
    await client.post("/api/v1/auth/register", json=user_data)
    # 登录
    resp = await client.post("/api/v1/auth/login", data={"username": "testadmin", "password": "Password123!"})
    return resp.json()["access_token"]



