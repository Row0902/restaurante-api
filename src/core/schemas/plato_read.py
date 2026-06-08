"""Schema de salida para un plato."""

from pydantic import BaseModel, ConfigDict


class PlatoRead(BaseModel):
    """Schema de salida para un plato."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None = None
    precio: float
    categoria: str
