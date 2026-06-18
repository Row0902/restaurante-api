"""Tests unitarios para OrderRepository con SQLite en memoria."""

import pytest
from sqlmodel import SQLModel

from core.database import create_engine, session_factory
from core.enums.order_status import OrderStatus
from core.exceptions.not_found import OrderNotFoundError
from core.models.menu_item import MenuItem
from core.models.order import Order
from core.models.order_item import OrderItem
from repositories.menu import MenuRepository
from repositories.ordenes import OrderRepository


@pytest.fixture
async def repos():
    """Provee MenuRepository y OrderRepository con SQLite en memoria."""
    engine = create_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    factory = session_factory(engine)
    async with factory() as session:
        menu_repo = MenuRepository(session)
        order_repo = OrderRepository(session)
        yield menu_repo, order_repo


class TestOrderRepositoryAdd:
    @pytest.mark.anyio
    async def test_add_crea_orden_con_items(self, repos):
        menu_repo, order_repo = repos
        pizza = await menu_repo.add(MenuItem(nombre="Pizza", precio=12.5))

        order = Order()
        order.items.append(
            OrderItem(menu_item_id=pizza.id, cantidad=2, precio_unitario=pizza.precio)
        )
        order.total = pizza.precio * 2

        created = await order_repo.add(order)
        assert created.id == 1
        assert created.total == 25.0
        assert len(created.items) == 1

    @pytest.mark.anyio
    async def test_add_multiples_ordenes(self, repos):
        menu_repo, order_repo = repos
        await menu_repo.add(MenuItem(nombre="X", precio=1.0))

        o1 = Order(total=1.0)
        o2 = Order(total=2.0)
        a = await order_repo.add(o1)
        b = await order_repo.add(o2)
        assert a.id == 1
        assert b.id == 2


class TestOrderRepositoryGetAll:
    @pytest.mark.anyio
    async def test_vacio_devuelve_lista_vacia(self, repos):
        _, order_repo = repos
        result = await order_repo.get_all()
        assert result == []

    @pytest.mark.anyio
    async def test_con_datos_devuelve_todas(self, repos):
        _, order_repo = repos
        await order_repo.add(Order(total=10.0))
        await order_repo.add(Order(total=20.0))
        result = await order_repo.get_all()
        assert len(result) == 2


class TestOrderRepositoryGetById:
    @pytest.mark.anyio
    async def test_encontrada_retorna_orden_con_items(self, repos):
        menu_repo, order_repo = repos
        pizza = await menu_repo.add(MenuItem(nombre="Pizza", precio=12.5))

        order = Order()
        order.items.append(
            OrderItem(menu_item_id=pizza.id, cantidad=3, precio_unitario=12.5)
        )
        order.total = 37.5
        await order_repo.add(order)

        fetched = await order_repo.get_by_id(1)
        assert fetched.total == 37.5
        assert len(fetched.items) == 1
        assert fetched.items[0].cantidad == 3

    @pytest.mark.anyio
    async def test_no_encontrada_lanza_excepcion(self, repos):
        _, order_repo = repos
        with pytest.raises(OrderNotFoundError):
            await order_repo.get_by_id(999)


class TestOrderRepositoryUpdateEstado:
    @pytest.mark.anyio
    async def test_actualiza_estado(self, repos):
        _, order_repo = repos
        await order_repo.add(Order())
        updated = await order_repo.update_estado(1, OrderStatus.preparando)
        assert updated.estado == OrderStatus.preparando

    @pytest.mark.anyio
    async def test_orden_inexistente_lanza_excepcion(self, repos):
        _, order_repo = repos
        with pytest.raises(OrderNotFoundError):
            await order_repo.update_estado(999, OrderStatus.preparando)
