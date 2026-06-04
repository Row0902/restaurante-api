from __future__ import annotations
from typing import List
from uuid import UUID
from core.schemas import DishCreate, DishResponse, OrderCreate, OrderResponse


class AbstractRepository:
    async def list_dishes(self) -> List[DishResponse]:
        raise NotImplementedError

    async def create_dish(self, dish_create: DishCreate) -> DishResponse:
        raise NotImplementedError

    async def get_dish(self, dish_id: UUID) -> DishResponse:
        raise NotImplementedError

    async def update_dish(self, dish_id: UUID, dish_update: DishCreate) -> DishResponse:
        raise NotImplementedError

    async def delete_dish(self, dish_id: UUID) -> None:
        raise NotImplementedError

    async def list_orders(self) -> List[OrderResponse]:
        raise NotImplementedError

    async def create_order(self, order_create: OrderCreate) -> OrderResponse:
        raise NotImplementedError

    async def get_order(self, order_id: UUID) -> OrderResponse:
        raise NotImplementedError

    async def update_order_status(self, order_id: UUID, status: str) -> OrderResponse:
        raise NotImplementedError
