"""Schema de entrada para items de orden."""

from pydantic import BaseModel, Field


class ItemOrdenRequest(BaseModel):
    """Datos de un item solicitado."""

    plato_id: str
    cantidad: int = Field(default=1, gt=0)
