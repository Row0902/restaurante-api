"""Schema de entrada para cambiar estado de orden."""

from pydantic import BaseModel


class EstadoOrdenRequest(BaseModel):
    """Datos para cambiar el estado de una orden."""

    estado: str
