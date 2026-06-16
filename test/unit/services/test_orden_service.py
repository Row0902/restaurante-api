"""Tests for OrdenesService — methods mocked at the repository boundary.

Following Strict TDD: RED phase — test written before production code.
"""

from unittest.mock import AsyncMock

import pytest

from core.exceptions import (
    InvalidEstadoTransitionError,
    InvalidOrdenDataError,
    MenuNotFoundError,
    OrdenNotFoundError,
)
from core.models.menu import MenuItem
from core.models.orden import Orden
from core.schemas.orden import OrdenCreate, OrdenItemData
from repositories.menu import MenuRepository
from repositories.orden import OrdenRepository
from services.orden import OrdenesService


@pytest.fixture
def mock_orden_repo() -> AsyncMock:
    """Return an AsyncMock specced on OrdenRepository."""
    return AsyncMock(spec=OrdenRepository)


@pytest.fixture
def mock_menu_repo() -> AsyncMock:
    """Return an AsyncMock specced on MenuRepository."""
    return AsyncMock(spec=MenuRepository)


@pytest.fixture
def service(
    mock_orden_repo: AsyncMock,
    mock_menu_repo: AsyncMock,
) -> OrdenesService:
    """Return an OrdenesService with mocked repositories injected."""
    return OrdenesService(orden_repo=mock_orden_repo, menu_repo=mock_menu_repo)


class TestGetAll:
    """get_all delegates to orden_repo.get_all."""

    async def test_returns_orders_unchanged(
        self,
        mock_orden_repo: AsyncMock,
        service: OrdenesService,
    ) -> None:
        """get_all returns the same list that orden_repo.get_all returns."""
        orders = [
            Orden(id=1, total=20.0, estado="pendiente"),
            Orden(id=2, total=15.0, estado="preparando"),
        ]
        mock_orden_repo.get_all.return_value = orders

        result = await service.get_all()

        assert result == orders
        assert len(result) == 2
        mock_orden_repo.get_all.assert_awaited_once()

    async def test_returns_empty_list_when_no_orders(
        self,
        mock_orden_repo: AsyncMock,
        service: OrdenesService,
    ) -> None:
        """get_all returns an empty list when the repo returns empty."""
        mock_orden_repo.get_all.return_value = []

        result = await service.get_all()

        assert result == []
        mock_orden_repo.get_all.assert_awaited_once()


class TestGetById:
    """get_by_id delegates to orden_repo.get_by_id."""

    async def test_returns_order_when_found(
        self,
        mock_orden_repo: AsyncMock,
        service: OrdenesService,
    ) -> None:
        """get_by_id returns the Orden from the repo."""
        expected = Orden(id=1, total=20.0, estado="pendiente")
        mock_orden_repo.get_by_id.return_value = expected

        result = await service.get_by_id(1)

        assert result is expected
        assert result.id == 1
        mock_orden_repo.get_by_id.assert_awaited_once_with(1)

    async def test_propagates_not_found_error(
        self,
        mock_orden_repo: AsyncMock,
        service: OrdenesService,
    ) -> None:
        """get_by_id propagates OrdenNotFoundError from the repo."""
        mock_orden_repo.get_by_id.side_effect = OrdenNotFoundError(99)

        with pytest.raises(OrdenNotFoundError) as excinfo:
            await service.get_by_id(99)

        assert str(excinfo.value) == "Order 99 not found."
        assert excinfo.value.orden_id == 99
        mock_orden_repo.get_by_id.assert_awaited_once_with(99)


class TestCreate:
    """create validates data, looks up prices, then delegates to repo."""

    async def test_valid_order_creates_with_price_lookup(
        self,
        mock_orden_repo: AsyncMock,
        mock_menu_repo: AsyncMock,
        service: OrdenesService,
    ) -> None:
        """Create validates, looks up menu prices, and delegates to repo."""
        data = OrdenCreate(items=[OrdenItemData(plato_id=1, cantidad=2)], mesa=5)
        menu_item = MenuItem(id=1, nombre="Pasta", precio=10.0)
        mock_menu_repo.get_by_id.return_value = menu_item
        expected_orden = Orden(id=1, total=20.0, estado="pendiente", mesa=5)
        mock_orden_repo.create.return_value = expected_orden

        result = await service.create(data)

        assert result is expected_orden
        assert result.total == 20.0
        assert result.estado == "pendiente"
        mock_menu_repo.get_by_id.assert_awaited_once_with(1)
        mock_orden_repo.create.assert_awaited_once()

        # Verify create was called with correct items_data and total
        _args, _kwargs = mock_orden_repo.create.await_args  # type: ignore[union-attr]
        _create_data, items_data, total = _args
        assert total == 20.0
        assert items_data == [
            {"plato_id": 1, "cantidad": 2, "precio_unitario": 10.0, "nombre": "Pasta"},
        ]

    async def test_computes_total_for_multiple_items(
        self,
        mock_orden_repo: AsyncMock,
        mock_menu_repo: AsyncMock,
        service: OrdenesService,
    ) -> None:
        """Create computes total = sum of cantidad * precio_unitario for all items."""
        data = OrdenCreate(
            items=[
                OrdenItemData(plato_id=1, cantidad=2),
                OrdenItemData(plato_id=2, cantidad=3),
            ],
        )

        async def get_by_id_side_effect(plato_id: int) -> MenuItem:
            prices = {1: 10.0, 2: 15.0}
            return MenuItem(
                id=plato_id, nombre=f"Item{plato_id}", precio=prices[plato_id]
            )

        mock_menu_repo.get_by_id.side_effect = get_by_id_side_effect
        expected_orden = Orden(id=1, total=65.0, estado="pendiente")
        mock_orden_repo.create.return_value = expected_orden

        result = await service.create(data)

        assert result.total == 65.0  # (2 * 10.0) + (3 * 15.0)
        assert mock_menu_repo.get_by_id.await_count == 2

    async def test_invalid_order_empty_items_raises_error(
        self,
        mock_orden_repo: AsyncMock,
        mock_menu_repo: AsyncMock,
        service: OrdenesService,
    ) -> None:
        """Create raises InvalidOrdenDataError for empty items, repo not called."""
        data = OrdenCreate(items=[])

        with pytest.raises(InvalidOrdenDataError) as excinfo:
            await service.create(data)

        assert "items" in str(excinfo.value)
        mock_orden_repo.create.assert_not_awaited()
        mock_menu_repo.get_by_id.assert_not_awaited()

    async def test_menu_not_found_during_creation(
        self,
        mock_orden_repo: AsyncMock,
        mock_menu_repo: AsyncMock,
        service: OrdenesService,
    ) -> None:
        """Create propagates MenuNotFoundError, repo not called."""
        data = OrdenCreate(items=[OrdenItemData(plato_id=99, cantidad=1)])
        mock_menu_repo.get_by_id.side_effect = MenuNotFoundError(99)

        with pytest.raises(MenuNotFoundError) as excinfo:
            await service.create(data)

        assert str(excinfo.value) == "Menu item 99 not found."
        mock_orden_repo.create.assert_not_awaited()


class TestCambiarEstado:
    """cambiar_estado validates transition and delegates to repo."""

    async def test_valid_transition_updates_estado(
        self,
        mock_orden_repo: AsyncMock,
        service: OrdenesService,
    ) -> None:
        """Cambiar_estado validates transition and calls repo.update."""
        orden = Orden(id=1, total=20.0, estado="pendiente")
        mock_orden_repo.get_by_id.return_value = orden
        updated = Orden(id=1, total=20.0, estado="preparando")
        mock_orden_repo.update.return_value = updated

        result = await service.cambiar_estado(1, "preparando")

        assert result.estado == "preparando"
        mock_orden_repo.get_by_id.assert_awaited_once_with(1)
        mock_orden_repo.update.assert_awaited_once()

    async def test_invalid_transition_raises_error(
        self,
        mock_orden_repo: AsyncMock,
        service: OrdenesService,
    ) -> None:
        """Cambiar_estado raises InvalidEstadoTransitionError, repo.update not called."""
        orden = Orden(id=1, total=20.0, estado="entregado")
        mock_orden_repo.get_by_id.return_value = orden

        with pytest.raises(InvalidEstadoTransitionError) as excinfo:
            await service.cambiar_estado(1, "preparando")

        assert "entregado" in str(excinfo.value.actual)
        assert "preparando" in str(excinfo.value.intentado)
        mock_orden_repo.update.assert_not_awaited()

    async def test_order_not_found_raises_error(
        self,
        mock_orden_repo: AsyncMock,
        service: OrdenesService,
    ) -> None:
        """Cambiar_estado propagates OrdenNotFoundError from repo."""
        mock_orden_repo.get_by_id.side_effect = OrdenNotFoundError(99)

        with pytest.raises(OrdenNotFoundError) as excinfo:
            await service.cambiar_estado(99, "preparando")

        assert "99" in str(excinfo.value)
        mock_orden_repo.update.assert_not_awaited()


class TestDelete:
    """delete delegates to orden_repo.delete."""

    async def test_existing_order_calls_repo(
        self,
        mock_orden_repo: AsyncMock,
        service: OrdenesService,
    ) -> None:
        """Delete delegates to orden_repo.delete for an existing order."""
        mock_orden_repo.delete.return_value = None

        await service.delete(1)

        mock_orden_repo.delete.assert_awaited_once_with(1)

    async def test_propagates_not_found_error(
        self,
        mock_orden_repo: AsyncMock,
        service: OrdenesService,
    ) -> None:
        """Delete propagates OrdenNotFoundError from the repo."""
        mock_orden_repo.delete.side_effect = OrdenNotFoundError(99)

        with pytest.raises(OrdenNotFoundError) as excinfo:
            await service.delete(99)

        assert str(excinfo.value) == "Order 99 not found."
        mock_orden_repo.delete.assert_awaited_once_with(99)
