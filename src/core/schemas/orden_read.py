"""Schema de salida para una orden."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from core.schemas.orden_item_read import OrdenItemRead


class OrdenRead(BaseModel):
    """Schema de salida para una orden."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    total: float
    estado: str
    created_at: datetime
    items: list[OrdenItemRead]
