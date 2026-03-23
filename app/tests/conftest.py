# app/tests/conftest.py
import pytest
import asyncio

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.main import app
from httpx import ASGITransport, AsyncClient


# 测试数据库使用单独的数据库，避免污染开发数据
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/policy_test_db"


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环，
    pytest-asyncio 需要的事件循环"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """测试用数据库引擎"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine):
    """每个测试用一个独立的 session"""
    async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_db):
    """Async HTTP 客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


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



