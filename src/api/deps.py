# src/api/deps.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from core.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session
