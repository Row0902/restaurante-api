"""Excepciones para recursos no encontrados.

Cada excepción incluye el identificador del recurso en su mensaje — R15.
"""

from __future__ import annotations

from .base import AppBaseError


class MenuItemNotFoundError(AppBaseError):
    """El plato solicitado no existe en el menú."""

    def __init__(self, plato_id: int | str) -> None:
        """Inicializa la excepción con el ID del plato no encontrado.

        Args:
            plato_id: Identificador del plato que no existe.
        """
        super().__init__(
            mensaje=f"Plato con id '{plato_id}' no encontrado",
            codigo="MENU_ITEM_NOT_FOUND",
        )


class OrderNotFoundError(AppBaseError):
    """La orden solicitada no existe."""

    def __init__(self, orden_id: int | str) -> None:
        """Inicializa la excepción con el ID de la orden no encontrada.

        Args:
            orden_id: Identificador de la orden que no existe.
        """
        super().__init__(
            mensaje=f"Orden con id '{orden_id}' no encontrada",
            codigo="ORDER_NOT_FOUND",
        )
