# src/core/schemas.py
from pydantic import BaseModel, Field

# --- Plato ---


class PlatoCreate(BaseModel):
    nombre: str
    descripcion: str = ""
    precio: float = Field(gt=0)
    disponible: bool = True


class PlatoUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    precio: float | None = Field(default=None, gt=0)
    disponible: bool | None = None


class PlatoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    precio: float
    disponible: bool

    model_config = {"from_attributes": True}


# --- Orden ---


class OrdenItemCreate(BaseModel):
    plato_id: int
    cantidad: int = Field(default=1, gt=0)


class OrdenCreate(BaseModel):
    items: list[OrdenItemCreate]


class OrdenItemResponse(BaseModel):
    id: int
    plato_id: int
    cantidad: int

    model_config = {"from_attributes": True}


class OrdenResponse(BaseModel):
    id: int
    total: float
    estado: str
    items: list[OrdenItemResponse]

    model_config = {"from_attributes": True}


class OrdenEstadoUpdate(BaseModel):
    estado: str
