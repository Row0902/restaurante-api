"""Schema de salida para un ítem de orden."""

from pydantic import BaseModel, ConfigDict


class OrdenItemRead(BaseModel):
    """Schema de salida para un ítem de orden."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    plato_id: int
    cantidad: int
