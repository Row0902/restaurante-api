"""Dependencias para inyección en FastAPI."""

from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from db.session import get_session
from repositories.menu_repository import MenuRepository
from repositories.orden_repository import OrdenRepository
from services.menu_service import MenuService
from services.orden_service import OrdenService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_menu_service(session: SessionDep) -> MenuService:
    """Inyecta el servicio de menú."""
    repo = MenuRepository(session)
    return MenuService(repo)


def get_orden_service(session: SessionDep) -> OrdenService:
    """Inyecta el servicio de órdenes."""
    orden_repo = OrdenRepository(session)
    menu_repo = MenuRepository(session)
    return OrdenService(orden_repo, menu_repo)


MenuServiceDep = Annotated[MenuService, Depends(get_menu_service)]
OrdenServiceDep = Annotated[OrdenService, Depends(get_orden_service)]
