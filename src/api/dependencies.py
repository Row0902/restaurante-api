"""Dependencias compartidas por routers FastAPI."""

from repositories.in_memory_menu_repository import InMemoryMenuRepository
from repositories.in_memory_orden_repository import InMemoryOrdenRepository
from repositories.menu_repository import Registro as MenuRegistro
from repositories.orden_repository import Registro as OrdenRegistro
from services.menu_service import MenuService
from services.orden_service import OrdenService

menu: dict[str, MenuRegistro] = {}
ordenes: dict[str, OrdenRegistro] = {}

menu_repository = InMemoryMenuRepository(menu)
orden_repository = InMemoryOrdenRepository(ordenes)
menu_service = MenuService(menu_repository)
orden_service = OrdenService(orden_repository, menu_repository)


def obtener_menu_service() -> MenuService:
    """Devuelve el servicio de menu configurado."""
    return menu_service


def obtener_orden_service() -> OrdenService:
    """Devuelve el servicio de ordenes configurado."""
    return orden_service


def limpiar_estado_en_memoria() -> None:
    """Limpia el almacenamiento en memoria para tests."""
    menu.clear()
    ordenes.clear()
