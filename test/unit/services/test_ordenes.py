"""Tests unitarios para OrderService con repos mockeados (R11)."""

from unittest.mock import AsyncMock

import pytest

from core.enums.order_status import OrderStatus
from core.exceptions.invalid_state import InvalidOrderStateError
from core.exceptions.not_found import MenuItemNotFoundError, OrderNotFoundError
from core.models.menu_item import MenuItem
from core.models.order import Order
from core.models.order_item import OrderItem
from core.schemas.order import (
    CreateOrdenItemRequest,
    CreateOrdenRequest,
    EstadoUpdateRequest,
)
from services.ordenes import OrderService


@pytest.fixture
def order_repo():
    """Mock de AbstractOrderRepository."""
    return AsyncMock()


@pytest.fixture
def menu_repo():
    """Mock de AbstractMenuRepository."""
    return AsyncMock()


@pytest.fixture
def service(order_repo, menu_repo):
    """OrderService con repositorios mockeados."""
    return OrderService(order_repo, menu_repo)


class TestOrderServiceListar:
    @pytest.mark.anyio
    async def test_listar_vacio(self, service, order_repo):
        order_repo.get_all.return_value = []
        result = await service.listar()
        assert result == []

    @pytest.mark.anyio
    async def test_listar_con_ordenes(self, service, order_repo):
        order = Order(id=1, total=25.0, estado=OrderStatus.pendiente)
        order.items = [
            OrderItem(id=1, menu_item_id=1, cantidad=2, precio_unitario=12.5)
        ]
        order_repo.get_all.return_value = [order]
        result = await service.listar()
        assert len(result) == 1
        assert result[0].total == 25.0


class TestOrderServiceObtenerPorId:
    @pytest.mark.anyio
    async def test_encontrado(self, service, order_repo):
        order = Order(id=1, total=10.0, estado=OrderStatus.pendiente)
        order_repo.get_by_id.return_value = order
        result = await service.obtener_por_id(1)
        assert result.id == 1
        order_repo.get_by_id.assert_awaited_once_with(1)

    @pytest.mark.anyio
    async def test_no_encontrado(self, service, order_repo):
        order_repo.get_by_id.side_effect = OrderNotFoundError(orden_id=999)
        with pytest.raises(OrderNotFoundError):
            await service.obtener_por_id(999)


class TestOrderServiceCrear:
    @pytest.mark.anyio
    async def test_crear_calcula_total(self, service, order_repo, menu_repo):
        pizza = MenuItem(id=1, nombre="Pizza", precio=12.5)
        menu_repo.get_by_id.return_value = pizza
        order_repo.add.return_value = Order(
            id=1, total=25.0, estado=OrderStatus.pendiente
        )

        request = CreateOrdenRequest(
            items=[CreateOrdenItemRequest(plato_id=1, cantidad=2)]
        )
        result = await service.crear(request)

        assert result.total == 25.0
        assert result.estado == "pendiente"
        menu_repo.get_by_id.assert_awaited_once_with(1)
        order_repo.add.assert_awaited_once()

    @pytest.mark.anyio
    async def test_crear_con_plato_inexistente(self, service, menu_repo):
        menu_repo.get_by_id.side_effect = MenuItemNotFoundError(plato_id=999)
        request = CreateOrdenRequest(
            items=[CreateOrdenItemRequest(plato_id=999, cantidad=1)]
        )
        with pytest.raises(MenuItemNotFoundError):
            await service.crear(request)

    @pytest.mark.anyio
    async def test_crear_con_multiples_items(self, service, order_repo, menu_repo):
        menu_repo.get_by_id.side_effect = [
            MenuItem(id=1, nombre="Pizza", precio=12.5),
            MenuItem(id=2, nombre="Ensalada", precio=8.0),
        ]
        order_repo.add.return_value = Order(id=1, total=33.0)

        request = CreateOrdenRequest(
            items=[
                CreateOrdenItemRequest(plato_id=1, cantidad=2),
                CreateOrdenItemRequest(plato_id=2, cantidad=1),
            ]
        )
        result = await service.crear(request)

        assert result.total == 33.0
        assert menu_repo.get_by_id.call_count == 2


class TestOrderServiceCambiarEstado:
    @pytest.mark.anyio
    async def test_cambiar_estado_valido(self, service, order_repo):
        existing = Order(id=1, total=10.0, estado=OrderStatus.pendiente)
        order_repo.get_by_id.return_value = existing
        updated = Order(id=1, total=10.0, estado=OrderStatus.preparando)
        order_repo.update_estado.return_value = updated

        request = EstadoUpdateRequest(estado=OrderStatus.preparando)
        result = await service.cambiar_estado(1, request)

        assert result.estado == "preparando"
        order_repo.update_estado.assert_awaited_once_with(1, OrderStatus.preparando)

    @pytest.mark.anyio
    async def test_transicion_invalida_lanza_error(self, service, order_repo):
        existing = Order(id=1, total=10.0, estado=OrderStatus.entregado)
        order_repo.get_by_id.return_value = existing

        request = EstadoUpdateRequest(estado=OrderStatus.cancelado)
        with pytest.raises(InvalidOrderStateError):
            await service.cambiar_estado(1, request)

    @pytest.mark.anyio
    async def test_orden_inexistente_lanza_error(self, service, order_repo):
        order_repo.get_by_id.side_effect = OrderNotFoundError(orden_id=999)
        request = EstadoUpdateRequest(estado=OrderStatus.preparando)
        with pytest.raises(OrderNotFoundError):
            await service.cambiar_estado(999, request)
