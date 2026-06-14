"""Schema de salida para eliminacion de platos."""

from pydantic import BaseModel


class PlatoEliminadoResponse(BaseModel):
    """Mensaje publico al eliminar un plato."""

    mensaje: str
    id: str
