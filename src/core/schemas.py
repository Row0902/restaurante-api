"""Esquemas Pydantic para validación de requests/responses."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PlatoBase(BaseModel):
    """Atributos base de un plato."""
    nombre: str
    precio: float
    descripcion: Optional[str] = None


class PlatoCreate(PlatoBase):
    """Esquema para crear un plato."""
    pass


class PlatoUpdate(PlatoBase):
    """Esquema para actualizar un plato."""
    nombre: Optional[str] = None
    precio: Optional[float] = None


class PlatoResponse(PlatoBase):
    """Esquema de respuesta para un plato."""
    id: str
    model_config = ConfigDict(from_attributes=True)


class OrdenItemSchema(BaseModel):
    """Esquema para un ítem de orden en request/response."""
    plato_id: str
    cantidad: int = Field(default=1, ge=1)


class OrdenCreate(BaseModel):
    """Esquema para crear una orden."""
    items: List[OrdenItemSchema]


class OrdenUpdateEstado(BaseModel):
    """Esquema para cambiar el estado de la orden."""
    estado: str


class OrdenResponse(BaseModel):
    """Esquema de respuesta para una orden."""
    id: str
    total: float
    estado: str
    items: List[OrdenItemSchema]
    
    model_config = ConfigDict(from_attributes=True)
