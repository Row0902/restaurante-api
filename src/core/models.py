from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Plato(SQLModel, table=True):
    __tablename__ = "platos"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str
    precio: float


class Orden(SQLModel, table=True):
    __tablename__ = "ordenes"

    id: int | None = Field(default=None, primary_key=True)

    items: list = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )

    total: float = 0
    estado: str = "pendiente"