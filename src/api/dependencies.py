"""Dependencias compartidas por routers FastAPI."""

from services.container import (
    obtener_menu_service,
    obtener_orden_service,
)

__all__ = [
    "obtener_menu_service",
    "obtener_orden_service",
]
