"""Schema de entrada para crear platos."""

from pydantic import BaseModel, ConfigDict


class PlatoRequest(BaseModel):
    """Datos requeridos para crear un plato."""

    nombre: str
    precio: float

    model_config = ConfigDict(extra="allow")
