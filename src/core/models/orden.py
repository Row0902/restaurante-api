"""Modelo SQLModel para la entidad Orden."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from core.models.orden_item import OrdenItem


class Orden(SQLModel, table=True):
    """Modelo de base de datos para la entidad Orden."""

    id: int | None = Field(default=None, primary_key=True)
    total: float = 0.0
    estado: str = "pendiente"
    created_at: datetime = Field(default_factory=datetime.now)

    items: list[OrdenItem] = Relationship(
        back_populates="orden",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
