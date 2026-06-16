"""Tests for OrdenRepository — all methods mocked at the AsyncSession boundary.

Following Strict TDD: RED phase — test written before production code.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from core.exceptions import OrdenNotFoundError
from core.models.orden import Orden, OrdenItem
from core.schemas.orden import OrdenCreate, OrdenItemData, OrdenUpdateEstado
from repositories.orden import OrdenRepository


@pytest.fixture
def mock_session() -> AsyncMock:
    """Return an AsyncMock specced on AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def repo(mock_session: AsyncMock) -> OrdenRepository:
    """Return an OrdenRepository with a mocked session injected."""
    return OrdenRepository(session=mock_session)


class TestGetAll:
    """get_all returns all Orden rows from the database."""

    async def test_returns_orders_when_exist(
        self,
        repo: OrdenRepository,
        mock_session: AsyncMock,
    ) -> None:
        """get_all returns a list of Orden when rows exist."""
        items1 = [
            OrdenItem(
                id=1,
                orden_id=1,
                plato_id=1,
                cantidad=2,
                precio_unitario=10.0,
                nombre="Pasta",
            )
        ]
        items2 = [
            OrdenItem(
                id=2,
                orden_id=2,
                plato_id=2,
                cantidad=1,
                precio_unitario=15.0,
                nombre="Pizza",
            )
        ]
        orders = [
            Orden(id=1, items=items1, total=20.0, estado="pendiente", mesa=5),
            Orden(id=2, items=items2, total=15.0, estado="preparando", mesa=3),
        ]
        mock_result = MagicMock()
        mock_result.all.return_value = orders
        mock_session.exec.return_value = mock_result

        result = await repo.get_all()

        assert result == orders
        assert len(result) == 2
        mock_session.exec.assert_awaited_once()

    async def test_returns_empty_list_when_no_orders(
        self,
        repo: OrdenRepository,
        mock_session: AsyncMock,
    ) -> None:
        """get_all returns an empty list when the table is empty."""
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.exec.return_value = mock_result

        result = await repo.get_all()

        assert result == []
        mock_session.exec.assert_awaited_once()


class TestGetById:
    """get_by_id returns a single Orden by primary key."""

    async def test_returns_order_when_found(
        self,
        repo: OrdenRepository,
        mock_session: AsyncMock,
    ) -> None:
        """get_by_id returns the Orden when the id exists."""
        items = [
            OrdenItem(
                id=1,
                orden_id=1,
                plato_id=1,
                cantidad=2,
                precio_unitario=10.0,
                nombre="Pasta",
            )
        ]
        expected = Orden(id=1, items=items, total=20.0, estado="pendiente")
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = expected
        mock_session.exec.return_value = mock_result

        result = await repo.get_by_id(1)

        assert result is expected
        assert result.id == 1
        assert result.total == 20.0
        assert result.estado == "pendiente"
        mock_session.exec.assert_awaited_once()

    async def test_raises_not_found_when_missing(
        self,
        repo: OrdenRepository,
        mock_session: AsyncMock,
    ) -> None:
        """get_by_id raises OrdenNotFoundError when the id does not exist."""
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = None
        mock_session.exec.return_value = mock_result

        with pytest.raises(OrdenNotFoundError) as excinfo:
            await repo.get_by_id(99)

        assert str(excinfo.value) == "Order 99 not found."
        assert excinfo.value.orden_id == 99
        mock_session.exec.assert_awaited_once()


class TestCreate:
    """create persists a new Orden with line items."""

    async def test_creates_order_with_items_and_returns_it(
        self,
        repo: OrdenRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Create returns an Orden with id, items, and correct field values."""
        data = OrdenCreate(items=[OrdenItemData(plato_id=1, cantidad=2)], mesa=5)
        items_data = [
            {"plato_id": 1, "cantidad": 2, "precio_unitario": 10.0, "nombre": "Pasta"},
        ]
        total = 20.0

        captured_orden: list[Orden] = []
        captured_items: list[OrdenItem] = []

        def capture_add(obj: object) -> None:
            if isinstance(obj, Orden):
                captured_orden.append(obj)
            elif isinstance(obj, OrdenItem):
                captured_items.append(obj)

        async def set_ids_on_flush() -> None:
            if captured_orden:
                captured_orden[0].id = 1
            for i, item in enumerate(captured_items):
                item.id = i + 1

        def setup_get_by_id_mock() -> None:
            """Set up exec mock so get_by_id returns the created orden with items."""
            if captured_orden and captured_items:
                orden = captured_orden[0]
                orden.items = captured_items
                mock_result = MagicMock()
                mock_result.one_or_none.return_value = orden
                mock_session.exec.return_value = mock_result

        async def on_flush() -> None:
            await set_ids_on_flush()
            setup_get_by_id_mock()

        mock_session.add.side_effect = capture_add
        mock_session.flush = AsyncMock(side_effect=on_flush)

        result = await repo.create(data, items_data, total)

        assert result.id == 1
        assert result.total == 20.0
        assert result.mesa == 5
        assert result.estado == "pendiente"
        assert len(captured_items) == 1
        assert captured_items[0].plato_id == 1
        assert captured_items[0].precio_unitario == 10.0
        assert captured_items[0].nombre == "Pasta"
        mock_session.add.assert_called()
        mock_session.flush.assert_awaited()
        mock_session.exec.assert_awaited_once()


class TestUpdate:
    """update modifies the estado of an existing Orden."""

    async def test_updates_estado_of_existing_order(
        self,
        repo: OrdenRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Update changes estado and returns the updated Orden."""
        original = Orden(id=1, total=20.0, estado="pendiente")
        updated = Orden(id=1, total=20.0, estado="preparando")

        # First get_by_id call returns original, second returns updated (post-flush)
        mock_result1 = MagicMock()
        mock_result1.one_or_none.return_value = original
        mock_result2 = MagicMock()
        mock_result2.one_or_none.return_value = updated
        mock_session.exec = AsyncMock(side_effect=[mock_result1, mock_result2])
        mock_session.flush = AsyncMock()

        data = OrdenUpdateEstado(estado="preparando")
        result = await repo.update(1, data)

        assert result.estado == "preparando"
        assert result.total == 20.0  # unchanged
        assert mock_session.exec.await_count == 2
        mock_session.flush.assert_awaited_once()

    async def test_raises_not_found_when_missing(
        self,
        repo: OrdenRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Update raises OrdenNotFoundError when the id does not exist."""
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = None
        mock_session.exec.return_value = mock_result

        with pytest.raises(OrdenNotFoundError) as excinfo:
            await repo.update(99, OrdenUpdateEstado(estado="preparando"))

        assert "99" in str(excinfo.value)


class TestDelete:
    """delete removes an existing Orden from the database."""

    async def test_completes_without_error(
        self,
        repo: OrdenRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Delete succeeds when the order exists."""
        orden = Orden(id=1, total=20.0, estado="pendiente")
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = orden
        mock_session.exec.return_value = mock_result
        mock_session.flush = AsyncMock()

        await repo.delete(1)

        mock_session.exec.assert_awaited_once()
        mock_session.delete.assert_called_once_with(orden)
        mock_session.flush.assert_awaited_once()

    async def test_raises_not_found_when_missing(
        self,
        repo: OrdenRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Delete raises OrdenNotFoundError when the id does not exist."""
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = None
        mock_session.exec.return_value = mock_result

        with pytest.raises(OrdenNotFoundError) as excinfo:
            await repo.delete(99)

        assert "99" in str(excinfo.value)
