"""Modelo SQLModel para platos."""

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from core.registro import Registro


class PlatoModel(SQLModel, table=True):
    """Tabla de platos persistidos."""

    __tablename__ = "platos"

    id: str = Field(primary_key=True)
    nombre: str
    precio: float
    extras: Registro = Field(default_factory=dict, sa_column=Column(JSON))
