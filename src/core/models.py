# src/core/models.py
from sqlmodel import Field, Relationship, SQLModel


class Plato(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str = ""
    precio: float
    disponible: bool = True

    items: list[OrdenItem] = Relationship(back_populates="plato")


class OrdenItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    orden_id: int = Field(foreign_key="orden.id")
    plato_id: int = Field(foreign_key="plato.id")
    cantidad: int = 1

    orden: Orden = Relationship(back_populates="items")
    plato: Plato = Relationship(back_populates="items")


class Orden(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    total: float = 0.0
    estado: str = "pendiente"

    items: list[OrdenItem] = Relationship(back_populates="orden")
