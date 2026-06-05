from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, conint, confloat, ConfigDict


class DishBase(BaseModel):
    name: str = Field(..., alias="nombre", min_length=1)
    description: Optional[str] = Field(None, alias="descripcion")
    price: confloat(ge=0.0) = Field(..., alias="precio")

    model_config = ConfigDict(
        validate_by_name=True,
        str_strip_whitespace=True,
        json_schema_extra={"example": {"nombre": "Milanesa", "descripcion": "Con papas", "precio": 12.5}},
    )


class DishCreate(DishBase):
    pass


class DishResponse(DishBase):
    id: UUID = Field(..., alias="id")

    model_config = ConfigDict(
        validate_by_name=True,
        str_strip_whitespace=True,
        json_schema_extra={"example": {"nombre": "Milanesa", "descripcion": "Con papas", "precio": 12.5}},
        from_attributes=True,
    )


class OrderItemBase(BaseModel):
    dish_id: UUID = Field(..., alias="plato_id")
    quantity: conint(ge=1) = Field(..., alias="cantidad")

    model_config = ConfigDict(validate_by_name=True)


class OrderCreate(BaseModel):
    items: List[OrderItemBase] = Field(..., alias="items")

    model_config = ConfigDict(validate_by_name=True)


class OrderResponse(BaseModel):
    id: UUID = Field(..., alias="id")
    items: List[OrderItemBase] = Field(..., alias="items")
    total: confloat(ge=0.0) = Field(..., alias="total")
    status: str = Field(..., alias="estado")
    created_at: Optional[datetime] = Field(None, alias="creado_en")

    model_config = ConfigDict(validate_by_name=True, from_attributes=True)
