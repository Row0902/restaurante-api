"""Schema de entrada para crear ordenes."""

from pydantic import BaseModel, Field

from api.schemas.item_orden_request import ItemOrdenRequest


class OrdenRequest(BaseModel):
    """Datos requeridos para crear una orden."""

    items: list[ItemOrdenRequest] = Field(default_factory=list)
