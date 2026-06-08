"""Schema de entrada para crear un plato."""

from pydantic import BaseModel


class PlatoCreate(BaseModel):
    """Schema de entrada para crear un plato."""

    nombre: str
    descripcion: str | None = None
    precio: float
    categoria: str
