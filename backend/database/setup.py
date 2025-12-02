from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from config import settings
from models.database import HCPInteraction


# 1. Create Async Engine
async_engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)


# 2. Async session factory
async_session_factory = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# 3. Create tables on startup
async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# 4. Dependency for FastAPI routes
async def get_db_session() -> AsyncGenerator:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
