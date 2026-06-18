"""Capa de infraestructura de base de datos.

Motor asíncrono SQLAlchemy + SQLModel, fábrica de sesiones y utilidades.
Sin dependencia de FastAPI — R7, R14.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel


def create_engine(database_url: str) -> AsyncEngine:
    """Crea un motor asíncrono SQLAlchemy a partir de una URL.

    Args:
        database_url: URL de conexión (ej. sqlite+aiosqlite:///./restaurante.db).

    Returns:
        Motor asíncrono configurado.
    """
    return create_async_engine(database_url, echo=False)


def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Crea una fábrica de sesiones asíncronas.

    Args:
        engine: Motor asíncrono SQLAlchemy.

    Returns:
        Factory que produce instancias de AsyncSession.
    """
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session(
    factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    """Generador asíncrono de sesiones de base de datos.

    Para usar con FastAPI ``Depends()``.

    Args:
        factory: Fábrica de sesiones asíncronas.

    Yields:
        Una sesión asíncrona SQLAlchemy.
    """
    async with factory() as session:
        yield session


async def init_db(engine: AsyncEngine) -> None:
    """Crea todas las tablas en la base de datos.

    Args:
        engine: Motor asíncrono SQLAlchemy.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
