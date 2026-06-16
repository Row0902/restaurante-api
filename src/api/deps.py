"""FastAPI dependency injection for the restaurant API."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from repositories.menu import MenuRepository
from repositories.ordenes import OrdenRepository
from services.menu import MenuService
from services.ordenes import OrdenService

engine = create_async_engine("sqlite+aiosqlite:///./restaurante.db")


async def get_session() -> AsyncGenerator[AsyncSession]:
    """Yield an async DB session."""
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_menu_repository(session: SessionDep) -> MenuRepository:
    """Provide MenuRepository with DB session."""
    return MenuRepository(session=session)


async def get_orden_repository(session: SessionDep) -> OrdenRepository:
    """Provide OrdenRepository with DB session."""
    return OrdenRepository(session=session)


async def get_menu_service(
    repo: Annotated[MenuRepository, Depends(get_menu_repository)],
) -> MenuService:
    """Provide MenuService with injected repository."""
    return MenuService(menu_repo=repo)


async def get_orden_service(
    orden_repo: Annotated[OrdenRepository, Depends(get_orden_repository)],
    menu_repo: Annotated[MenuRepository, Depends(get_menu_repository)],
) -> OrdenService:
    """Provide OrdenService with injected repositories."""
    return OrdenService(orden_repo=orden_repo, menu_repo=menu_repo)


MenuServiceDep = Annotated[MenuService, Depends(get_menu_service)]
OrdenServiceDep = Annotated[OrdenService, Depends(get_orden_service)]
