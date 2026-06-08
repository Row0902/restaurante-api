"""Schema de entrada para actualizar un plato."""

from pydantic import BaseModel


class PlatoUpdate(BaseModel):
    """Schema de entrada para actualizar un plato (todos los campos opcionales)."""

    nombre: str | None = None
    descripcion: str | None = None
    precio: float | None = None
    categoria: str | None = None
