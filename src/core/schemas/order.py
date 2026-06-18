"""Schemas Pydantic para órdenes — contratos de API.

DTOs de entrada y salida para los endpoints de órdenes.
Separados de los modelos SQLModel — R5, R13.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from core.enums.order_status import OrderStatus


class CreateOrdenItemRequest(BaseModel):
    """DTO para un ítem dentro de una orden nueva.

    Attributes:
        plato_id: ID del plato en el menú.
        cantidad: Cantidad de unidades (default 1, mínimo 1).
    """

    plato_id: int = Field(gt=0)
    cantidad: int = Field(default=1, gt=0)


class CreateOrdenRequest(BaseModel):
    """DTO para crear una nueva orden.

    Attributes:
        items: Lista de ítems del menú (mínimo 1).
    """

    items: list[CreateOrdenItemRequest] = Field(min_length=1)


class EstadoUpdateRequest(BaseModel):
    """DTO para cambiar el estado de una orden.

    Attributes:
        estado: Nuevo estado válido según la máquina de estados.
    """

    estado: OrderStatus


class OrdenItemResponse(BaseModel):
    """DTO de respuesta para un ítem dentro de una orden."""

    model_config = {"from_attributes": True}

    id: int
    menu_item_id: int
    cantidad: int
    precio_unitario: float


class OrdenResponse(BaseModel):
    """DTO de respuesta para una orden."""

    model_config = {"from_attributes": True}

    id: int
    total: float
    estado: str
    items: list[OrdenItemResponse] = []
    created_at: datetime | None = None
