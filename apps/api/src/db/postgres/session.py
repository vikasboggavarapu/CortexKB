## for sessions 
import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/myapp"
)

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    DATABASE_URL,
    echo = True,
    pool_size = 10,
    max_overflow = 20,
    pool_pre_ping = True,
    pool_recycle = 1800
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

