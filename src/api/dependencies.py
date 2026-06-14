"""Dependencias compartidas por routers FastAPI."""

from services.container import (
    limpiar_estado_en_memoria,
    obtener_menu_service,
    obtener_orden_service,
)

__all__ = [
    "limpiar_estado_en_memoria",
    "obtener_menu_service",
    "obtener_orden_service",
]
