"""Modelo SQLModel para la entidad Plato."""

from sqlmodel import Field, SQLModel


class Plato(SQLModel, table=True):
    """Modelo de base de datos para la entidad Plato."""

    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str | None = None
    precio: float
    categoria: str
