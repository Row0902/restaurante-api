"""Pydantic v2 schemas for API request/response validation."""

from pydantic import BaseModel, ConfigDict, Field


class PlatoCreate(BaseModel):
    """Schema for creating a new menu item."""

    nombre: str = Field(min_length=1, max_length=200)
    precio: float = Field(gt=0)
    descripcion: str | None = None
    disponible: bool = True


class PlatoUpdate(BaseModel):
    """Schema for partial menu item updates."""

    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    precio: float | None = Field(default=None, gt=0)
    descripcion: str | None = None
    disponible: bool | None = None


class PlatoResponse(BaseModel):
    """Schema for menu item API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    precio: float
    descripcion: str | None
    disponible: bool


class OrdenItemSchema(BaseModel):
    """Schema for order line items."""

    plato_id: int
    cantidad: int = Field(default=1, ge=1)


class OrdenCreate(BaseModel):
    """Schema for creating a new order."""

    items: list[OrdenItemSchema] = Field(min_length=1)


class OrdenResponse(BaseModel):
    """Schema for order API responses."""

    id: int
    items: list[OrdenItemSchema]
    total: float
    estado: str


class EstadoUpdate(BaseModel):
    """Schema for updating order status."""

    estado: str = Field(min_length=1)
