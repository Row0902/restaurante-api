"""Implementación SQLModel del repositorio de órdenes.

Operaciones asíncronas con SQLAlchemy — R14.
Implementa AbstractOrderRepository — R7.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.enums.order_status import OrderStatus
from core.exceptions.not_found import OrderNotFoundError
from core.models.order import Order
from core.repositories.ordenes import AbstractOrderRepository


class OrderRepository(AbstractOrderRepository):
    """Acceso a datos de órdenes via SQLModel."""

    def __init__(self, session: AsyncSession) -> None:
        """Inicializa el repositorio con una sesión activa.

        Args:
            session: Sesión asíncrona SQLAlchemy.
        """
        self._session = session

    async def get_all(self) -> list[Order]:
        """Obtiene todas las órdenes con sus items."""
        stmt = select(Order).options(selectinload(Order.items))
        result = await self._session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_id(self, order_id: int) -> Order:
        """Busca una orden por ID con sus items. Lanza OrderNotFoundError si no existe."""
        order = await self._session.get(
            Order, order_id, options=[selectinload(Order.items)]
        )
        if order is None:
            raise OrderNotFoundError(orden_id=order_id)
        return order

    async def add(self, order: Order) -> Order:
        """Crea una orden y retorna con ID asignado."""
        self._session.add(order)
        await self._session.commit()
        await self._session.refresh(order)
        return order

    async def update_estado(self, order_id: int, estado: OrderStatus) -> Order:
        """Actualiza el estado de una orden. Lanza OrderNotFoundError si no existe."""
        order = await self.get_by_id(order_id)
        order.estado = estado
        await self._session.commit()
        await self._session.refresh(order)
        return order
