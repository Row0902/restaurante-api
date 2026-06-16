"""Dependency injection for the API layer.

Provides async session lifecycle and service/repository factory
functions for FastAPI dependency injection.
"""

import os
from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from repositories.menu import MenuRepository
from repositories.orden import OrdenRepository
from services.menu import MenuService
from services.orden import OrdenesService

_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./restaurante.db")
_engine = create_async_engine(_DATABASE_URL, echo=False)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Yield an async DB session for the duration of a request.

    Commits the transaction after the request handler completes
    (code after yield runs after the response). Repository flushes
    but never commits — this function owns the transaction boundary.
    """
    async with AsyncSession(_engine) as session:
        yield session
        await session.commit()


async def get_menu_repository(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008  # type: ignore[arg-type]
) -> AsyncGenerator[MenuRepository]:
    """Build a MenuRepository with the current session."""
    yield MenuRepository(session)


async def get_menu_service(
    menu_repo: MenuRepository = Depends(get_menu_repository),  # noqa: B008
) -> AsyncGenerator[MenuService]:
    """Build a MenuService wired to a MenuRepository with the current session."""
    yield MenuService(menu_repo)


async def get_orden_repository(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008  # type: ignore[arg-type]
) -> AsyncGenerator[OrdenRepository]:
    """Build an OrdenRepository with the current session."""
    yield OrdenRepository(session)


async def get_orden_service(
    orden_repo: OrdenRepository = Depends(get_orden_repository),  # noqa: B008
    menu_repo: MenuRepository = Depends(get_menu_repository),  # noqa: B008
) -> AsyncGenerator[OrdenesService]:
    """Build an OrdenesService with both repositories backed by the current session."""
    yield OrdenesService(orden_repo, menu_repo)
