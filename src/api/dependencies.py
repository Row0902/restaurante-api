"""Dependencias compartidas por routers FastAPI."""

from collections.abc import AsyncIterator

from fastapi import Request

from services.container import (
    obtener_menu_service_desde,
    obtener_orden_service_desde,
)
from services.menu_service import MenuService
from services.orden_service import OrdenService


async def obtener_menu_service(request: Request) -> AsyncIterator[MenuService]:
    """Devuelve servicio de menu para el request."""
    async for service in obtener_menu_service_desde(request.app.state.session_maker):
        yield service


async def obtener_orden_service(request: Request) -> AsyncIterator[OrdenService]:
    """Devuelve servicio de ordenes para el request."""
    async for service in obtener_orden_service_desde(request.app.state.session_maker):
        yield service

__all__ = [
    "obtener_menu_service",
    "obtener_orden_service",
]
