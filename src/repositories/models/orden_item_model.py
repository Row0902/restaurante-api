"""Modelo SQLModel para items de orden."""

from sqlmodel import Field, SQLModel


class OrdenItemModel(SQLModel, table=True):
    """Tabla de items persistidos por orden."""

    __tablename__ = "orden_items"

    id: int | None = Field(default=None, primary_key=True)
    orden_id: str = Field(foreign_key="ordenes.id")
    posicion: int
    plato_id: str
    cantidad: int
