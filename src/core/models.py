"""Modelos de base de datos (SQLModel)."""

import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Plato(SQLModel, table=True):
    """Modelo de plato del menú."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    nombre: str
    precio: float
    descripcion: Optional[str] = None


class OrdenItem(SQLModel, table=True):
    """Ítem individual dentro de una orden."""
    
    __tablename__ = "orden_item"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    orden_id: str = Field(foreign_key="orden.id")
    plato_id: str = Field(foreign_key="plato.id")
    cantidad: int = 1
    
    orden: "Orden" = Relationship(back_populates="items")


class Orden(SQLModel, table=True):
    """Modelo de orden."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    total: float = 0.0
    estado: str = "pendiente"  # pendiente, preparando, entregado
    
    items: List[OrdenItem] = Relationship(back_populates="orden", cascade_delete=True)
