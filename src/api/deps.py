"""Dependencias inyectables de FastAPI para servicios."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.database import get_session
from repositories.menu import MenuRepository
from repositories.ordenes import OrdenRepository
from services.menu import MenuService
from services.ordenes import OrdenService


async def get_menu_service(
    session: AsyncSession = Depends(get_session),
) -> MenuService:
    return MenuService(MenuRepository(session))


async def get_orden_service(
    session: AsyncSession = Depends(get_session),
) -> OrdenService:
    return OrdenService(
        OrdenRepository(session),
        MenuRepository(session),
    )
