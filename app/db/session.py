# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,               # 开发时可以改成 True 看 SQL
    future=True,              # 强制使用 SQLAlchemy 2.0 风格的语法
    pool_pre_ping=True,
)

# 异步 session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# 依赖注入用
# 代码运行到 yield 会暂停，并将 session 对象交给后面的业务逻辑
# 无论业务逻辑是否成功，最后都能释放资源
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session