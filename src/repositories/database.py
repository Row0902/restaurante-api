"""Engine async de SQLAlchemy, sesión y lifecycle de la base de datos."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from core.config import Settings

settings = Settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Crea todas las tablas definidas con SQLModel."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession]:
    """Dependencia FastAPI para inyectar sesión async."""
    async with SessionLocal() as session:
        yield session


async def close_db() -> None:
    """Cierra el engine al detener la aplicación."""
    await engine.dispose()


@asynccontextmanager
async def lifespan(_app: Any) -> AsyncGenerator[None]:
    """Crea tablas al iniciar y cierra el engine al detener."""
    await init_db()
    yield
    await close_db()
