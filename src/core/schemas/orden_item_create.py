"""Schema de entrada para crear un ítem dentro de una orden."""

from pydantic import BaseModel


class OrdenItemCreate(BaseModel):
    """Schema de entrada para crear un ítem dentro de una orden."""

    plato_id: int
    cantidad: int = 1
