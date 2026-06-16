"""Orden and OrdenItem SQLModel tables for the orders domain.

Spec-granted grouping: both classes in one file per design decision
(pragmatic for course scope, each is ~18 lines).
"""

from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class OrdenItem(SQLModel, table=True):
    """A line item within an order.

    Snapshots precio_unitario and nombre at creation time so menu price
    changes do not retroactively alter existing orders.
    """

    __tablename__ = "orden_items"

    id: int | None = Field(default=None, primary_key=True)
    orden_id: int = Field(foreign_key="ordenes.id")
    plato_id: int
    cantidad: int
    precio_unitario: float
    nombre: str

    orden: Orden = Relationship(back_populates="items")


class Orden(SQLModel, table=True):
    """An order placed by a customer at a table.

    Tracks estado through a lifecycle managed by EstadoOrden state machine.
    """

    __tablename__ = "ordenes"

    id: int | None = Field(default=None, primary_key=True)
    items: list[OrdenItem] = Relationship(back_populates="orden")
    total: float
    estado: str = Field(default="pendiente")
    created_at: datetime | None = Field(default_factory=datetime.now)
    mesa: int | None = Field(default=None)
