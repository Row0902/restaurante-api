"""Ensamblado de servicios de aplicacion."""

from collections.abc import AsyncIterator

from sqlmodel.ext.asyncio.session import AsyncSession

from repositories.database import obtener_sesion
from repositories.sqlmodel_menu_repository import SqlModelMenuRepository
from repositories.sqlmodel_orden_repository import SqlModelOrdenRepository
from services.menu_service import MenuService
from services.orden_service import OrdenService


def construir_menu_service(session: AsyncSession) -> MenuService:
    """Construye servicio de menu con repositorio SQLModel."""
    return MenuService(SqlModelMenuRepository(session))


def construir_orden_service(session: AsyncSession) -> OrdenService:
    """Construye servicio de ordenes con repositorios SQLModel."""
    menu_repository = SqlModelMenuRepository(session)
    orden_repository = SqlModelOrdenRepository(session)
    return OrdenService(orden_repository, menu_repository)


async def obtener_menu_service() -> AsyncIterator[MenuService]:
    """Devuelve el servicio de menu configurado."""
    async for session in obtener_sesion():
        yield construir_menu_service(session)


async def obtener_orden_service() -> AsyncIterator[OrdenService]:
    """Devuelve el servicio de ordenes configurado."""
    async for session in obtener_sesion():
        yield construir_orden_service(session)
