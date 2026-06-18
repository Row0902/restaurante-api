"""Enum de estados de orden con validación polimórfica de transiciones.

Cada estado conoce a qué otros estados puede transicionar.
Sin condicionales (if/match) preguntando el tipo — R1.
"""

from __future__ import annotations

from enum import StrEnum


class OrderStatus(StrEnum):
    """Estados posibles de una orden de restaurante.

    Cada variante implementa su propia lógica de transición
    a través del método ``puede_transicionar_a()``.
    """

    pendiente = "pendiente"
    preparando = "preparando"
    entregado = "entregado"
    cancelado = "cancelado"

    def puede_transicionar_a(self, destino: OrderStatus) -> bool:
        """Valida si la transición desde el estado actual a ``destino`` es permitida.

        Args:
            destino: El estado al que se quiere transicionar.

        Returns:
            True si la transición es válida, False en caso contrario.
        """
        transiciones: dict[OrderStatus, set[OrderStatus]] = {
            OrderStatus.pendiente: {OrderStatus.preparando, OrderStatus.cancelado},
            OrderStatus.preparando: {OrderStatus.entregado, OrderStatus.cancelado},
            OrderStatus.entregado: set(),
            OrderStatus.cancelado: set(),
        }

        return destino in transiciones.get(self, set())
