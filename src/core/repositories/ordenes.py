"""Interfaz abstracta para el repositorio de órdenes.

Define el contrato que toda implementación debe cumplir.
Los servicios dependen de esta abstracción — R7.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.enums.order_status import OrderStatus
from core.models.order import Order


class AbstractOrderRepository(ABC):
    """Puerto de acceso a datos para órdenes."""

    @abstractmethod
    async def get_all(self) -> list[Order]:
        """Obtiene todas las órdenes.

        Returns:
            Lista de órdenes.
        """
        ...

    @abstractmethod
    async def get_by_id(self, order_id: int) -> Order:
        """Busca una orden por ID.

        Args:
            order_id: ID de la orden.

        Returns:
            La orden encontrada.

        Raises:
            OrderNotFoundError: Si no existe.
        """
        ...

    @abstractmethod
    async def add(self, order: Order) -> Order:
        """Crea una nueva orden.

        Args:
            order: Orden a crear (con items y total calculado).

        Returns:
            La orden con su ID asignado.
        """
        ...

    @abstractmethod
    async def update_estado(self, order_id: int, estado: OrderStatus) -> Order:
        """Actualiza el estado de una orden.

        Args:
            order_id: ID de la orden.
            estado: Nuevo estado.

        Returns:
            La orden actualizada.

        Raises:
            OrderNotFoundError: Si la orden no existe.
        """
        ...
