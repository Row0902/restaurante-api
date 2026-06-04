from __future__ import annotations
import asyncio
from typing import Dict, List
from uuid import UUID, uuid4
from datetime import datetime

from core.schemas import (
    DishCreate,
    DishResponse,
    OrderCreate,
    OrderResponse,
    OrderItemBase,
)
from core.exceptions import NotFoundError
from repositories.abstract_repository import AbstractRepository


class InMemoryRepository(AbstractRepository):
    def __init__(self) -> None:
        # store as dict[str, dict] with Spanish keys for public consistency
        self._menu: Dict[str, Dict] = {}
        self._orders: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()

    async def list_dishes(self) -> List[DishResponse]:
        async with self._lock:
            return [DishResponse(id=UUID(k), **{
                "name": v.get("nombre"),
                "description": v.get("descripcion"),
                "price": v.get("precio"),
            }) for k, v in self._menu.items()]

    async def create_dish(self, dish_create: DishCreate) -> DishResponse:
        new_id = uuid4()
        async with self._lock:
            self._menu[str(new_id)] = {
                "id": str(new_id),
                "nombre": dish_create.name,
                "descripcion": dish_create.description,
                "precio": dish_create.price,
            }
            v = self._menu[str(new_id)]
        return DishResponse(id=new_id, name=v["nombre"], description=v["descripcion"], price=v["precio"])

    async def get_dish(self, dish_id: UUID) -> DishResponse:
        key = str(dish_id)
        async with self._lock:
            try:
                v = self._menu[key]
            except KeyError:
                raise NotFoundError(f"Dish {dish_id} not found")
        return DishResponse(id=dish_id, name=v["nombre"], description=v.get("descripcion"), price=v["precio"])

    async def update_dish(self, dish_id: UUID, dish_update: DishCreate) -> DishResponse:
        key = str(dish_id)
        async with self._lock:
            if key not in self._menu:
                raise NotFoundError(f"Dish {dish_id} not found")
            self._menu[key] = {
                "id": key,
                "nombre": dish_update.name,
                "descripcion": dish_update.description,
                "precio": dish_update.price,
            }
            v = self._menu[key]
        return DishResponse(id=dish_id, name=v["nombre"], description=v.get("descripcion"), price=v["precio"])

    async def delete_dish(self, dish_id: UUID) -> None:
        key = str(dish_id)
        async with self._lock:
            try:
                self._menu.pop(key)
            except KeyError:
                raise NotFoundError(f"Dish {dish_id} not found")

    async def list_orders(self) -> List[OrderResponse]:
        async with self._lock:
            return [OrderResponse(
                id=UUID(k),
                items=[OrderItemBase(dish_id=UUID(i["plato_id"]), quantity=i["cantidad"]) for i in v["items"]],
                total=v["total"],
                status=v["estado"],
                created_at=v.get("creado_en"),
            ) for k, v in self._orders.items()]

    async def create_order(self, order_create: OrderCreate) -> OrderResponse:
        new_id = uuid4()
        total = 0.0
        items_out = []
        async with self._lock:
            for item in order_create.items:
                key = str(item.dish_id)
                try:
                    dish = self._menu[key]
                except KeyError:
                    raise NotFoundError(f"Dish {item.dish_id} not found")
                cantidad = item.quantity
                total += dish["precio"] * cantidad
                items_out.append({"plato_id": key, "cantidad": cantidad})
            self._orders[str(new_id)] = {
                "id": str(new_id),
                "items": items_out,
                "total": total,
                "estado": "pendiente",
                "creado_en": datetime.utcnow(),
            }
            stored = self._orders[str(new_id)]

        return OrderResponse(
            id=new_id,
            items=[OrderItemBase(dish_id=UUID(i["plato_id"]), quantity=i["cantidad"]) for i in stored["items"]],
            total=stored["total"],
            status=stored["estado"],
            created_at=stored.get("creado_en"),
        )

    async def get_order(self, order_id: UUID) -> OrderResponse:
        key = str(order_id)
        async with self._lock:
            try:
                v = self._orders[key]
            except KeyError:
                raise NotFoundError(f"Order {order_id} not found")
        return OrderResponse(
            id=order_id,
            items=[OrderItemBase(dish_id=UUID(i["plato_id"]), quantity=i["cantidad"]) for i in v["items"]],
            total=v["total"],
            status=v["estado"],
            created_at=v.get("creado_en"),
        )

    async def update_order_status(self, order_id: UUID, status: str) -> OrderResponse:
        key = str(order_id)
        async with self._lock:
            if key not in self._orders:
                raise NotFoundError(f"Order {order_id} not found")
            self._orders[key]["estado"] = status
            v = self._orders[key]
        return OrderResponse(
            id=UUID(key),
            items=[OrderItemBase(dish_id=UUID(i["plato_id"]), quantity=i["cantidad"]) for i in v["items"]],
            total=v["total"],
            status=v["estado"],
            created_at=v.get("creado_en"),
        )
