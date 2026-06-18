"""Excepciones para recursos duplicados en el dominio.

Cada excepción incluye el nombre del recurso duplicado — R15.
"""

from __future__ import annotations

from .base import AppBaseError


class MenuItemDuplicateError(AppBaseError):
    """Intento de crear un plato con un nombre ya existente."""

    def __init__(self, nombre: str) -> None:
        """Inicializa la excepción con el nombre del plato duplicado.

        Args:
            nombre: Nombre del plato que ya existe.
        """
        super().__init__(
            mensaje=f"Ya existe un plato con el nombre '{nombre}'",
            codigo="MENU_ITEM_DUPLICATE",
        )
