"""Schema de entrada para crear una orden."""

from pydantic import BaseModel

from core.schemas.orden_item_create import OrdenItemCreate


class OrdenCreate(BaseModel):
    """Schema de entrada para crear una orden."""

    items: list[OrdenItemCreate]
