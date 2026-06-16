"""Domain models for the restaurant API."""

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Plato(SQLModel, table=True):
    """Menu item table model."""

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)
    precio: float = Field(ge=0)
    descripcion: str | None = Field(default=None)
    disponible: bool = Field(default=True)


class OrdenItem(SQLModel):
    """Order line item value object (embedded as JSON)."""

    plato_id: int = Field(ge=0)
    cantidad: int = Field(default=1, ge=1)


class Orden(SQLModel, table=True):
    """Order table model."""

    id: int | None = Field(default=None, primary_key=True)
    items: list[OrdenItem] = Field(default_factory=list, sa_column=Column(JSON))
    total: float = Field(default=0.0, ge=0)
    estado: str = Field(default="pendiente")
