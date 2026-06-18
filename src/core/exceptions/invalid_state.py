"""Excepción para transiciones de estado no válidas en órdenes.

Se lanza cuando se intenta cambiar una orden a un estado
que no es reachable desde su estado actual — R1, R15.
"""

from __future__ import annotations

from .base import AppBaseError


class InvalidOrderStateError(AppBaseError):
    """Transición de estado no permitida para la orden."""

    def __init__(self, actual: str, destino: str) -> None:
        """Inicializa la excepción con los estados involucrados.

        Args:
            actual: Estado actual de la orden.
            destino: Estado al que se intentó transicionar.
        """
        super().__init__(
            mensaje=f"No se puede cambiar de '{actual}' a '{destino}'",
            codigo="INVALID_ORDER_STATE",
        )
