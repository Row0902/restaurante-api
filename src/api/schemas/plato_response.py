"""Schema de salida para platos."""

from pydantic import BaseModel, ConfigDict


class PlatoResponse(BaseModel):
    """Datos publicos de un plato."""

    id: str
    nombre: str | None = None
    precio: float | None = None

    model_config = ConfigDict(extra="allow")
