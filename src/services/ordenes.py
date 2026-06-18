"""Servicio de aplicación para la gestión de órdenes.

Orquesta la creación de órdenes con cálculo de total
y validación de transiciones de estado — R1.
"""

from __future__ import annotations

from core.exceptions.invalid_state import InvalidOrderStateError
from core.models.order import Order
from core.models.order_item import OrderItem
from core.repositories.menu import AbstractMenuRepository
from core.repositories.ordenes import AbstractOrderRepository
from core.schemas.order import (
    CreateOrdenRequest,
    EstadoUpdateRequest,
    OrdenResponse,
)


class OrderService:
    """Lógica de negocio para órdenes del restaurante."""

    def __init__(
        self,
        order_repo: AbstractOrderRepository,
        menu_repo: AbstractMenuRepository,
    ) -> None:
        """Inicializa el servicio con repositorios inyectados.

        Args:
            order_repo: Repositorio de órdenes.
            menu_repo: Repositorio de menú para validar platos.
        """
        self._order_repo = order_repo
        self._menu_repo = menu_repo

    async def listar(self) -> list[OrdenResponse]:
        """Lista todas las órdenes."""
        orders = await self._order_repo.get_all()
        return [OrdenResponse.model_validate(order) for order in orders]

    async def obtener_por_id(self, orden_id: int) -> OrdenResponse:
        """Obtiene una orden por ID. Lanza OrderNotFoundError si no existe."""
        order = await self._order_repo.get_by_id(orden_id)
        return OrdenResponse.model_validate(order)

    async def crear(self, request: CreateOrdenRequest) -> OrdenResponse:
        """Crea una orden calculando el total desde los precios del menú.

        Valida que cada plato_id exista en el menú.
        Lanza MenuItemNotFoundError si algún plato no existe.
        """
        order = Order()
        total = 0.0

        for item_req in request.items:
            menu_item = await self._menu_repo.get_by_id(item_req.plato_id)
            assert menu_item.id is not None
            order.items.append(
                OrderItem(
                    menu_item_id=menu_item.id,
                    cantidad=item_req.cantidad,
                    precio_unitario=menu_item.precio,
                )
            )
            total += menu_item.precio * item_req.cantidad

        order.total = total
        created = await self._order_repo.add(order)
        return OrdenResponse.model_validate(created)

    async def cambiar_estado(
        self, orden_id: int, request: EstadoUpdateRequest
    ) -> OrdenResponse:
        """Cambia el estado de una orden con validación polimórfica (R1).

        Lanza InvalidOrderStateError si la transición no es permitida.
        """
        order = await self._order_repo.get_by_id(orden_id)

        if not order.estado.puede_transicionar_a(request.estado):
            raise InvalidOrderStateError(
                actual=order.estado.value,
                destino=request.estado.value,
            )

        updated = await self._order_repo.update_estado(orden_id, request.estado)
        return OrdenResponse.model_validate(updated)
