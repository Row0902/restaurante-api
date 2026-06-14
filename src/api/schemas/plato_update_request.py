"""Schema de entrada para actualizar platos."""

from pydantic import BaseModel, ConfigDict


class PlatoUpdateRequest(BaseModel):
    """Datos aceptados para reemplazar un plato."""

    nombre: str | None = None
    precio: float | None = None

    model_config = ConfigDict(extra="allow")
