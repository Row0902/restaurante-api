"""Schema de entrada para actualizar el estado de una orden."""

from pydantic import BaseModel


class EstadoUpdate(BaseModel):
    """Schema de entrada para actualizar el estado de una orden."""

    estado: str
