"""Modelo SQLModel para los ítems de una orden."""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from core.models.orden import Orden


class OrdenItem(SQLModel, table=True):
    """Modelo de base de datos para los ítems de una orden."""

    id: int | None = Field(default=None, primary_key=True)
    orden_id: int | None = Field(default=None, foreign_key="orden.id")
    plato_id: int = Field(foreign_key="plato.id")
    cantidad: int = 1

    orden: Optional["Orden"] = Relationship(back_populates="items")
