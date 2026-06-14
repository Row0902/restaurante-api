"""Modelo SQLModel para ordenes."""

from sqlmodel import Field, SQLModel


class OrdenModel(SQLModel, table=True):
    """Tabla de ordenes persistidas."""

    __tablename__ = "ordenes"

    id: str = Field(primary_key=True)
    total: float
    estado: str
