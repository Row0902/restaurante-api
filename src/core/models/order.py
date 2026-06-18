"""Entidad Orden (SQLModel).

Representa la tabla ``order``. Una orden contiene ítems del menú,
un total calculado y un estado que avanza según la máquina de estados.
"""

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel

from core.enums.order_status import OrderStatus
from core.models.order_item import OrderItem

# -- evita que ``from __future__ import annotations`` rompa SQLAlchemy


class Order(SQLModel, table=True):
    """Orden de compra de un cliente.

    Attributes:
        id: Identificador único.
        total: Suma de precios × cantidades de los ítems.
        estado: Estado actual según la máquina de estados.
        items: Ítems de la orden (relación uno-a-muchos).
    """

    __tablename__ = "order"

    id: int | None = Field(default=None, primary_key=True)
    total: float = Field(default=0.0)
    estado: OrderStatus = Field(default=OrderStatus.pendiente)

    items: Mapped[list[OrderItem]] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
