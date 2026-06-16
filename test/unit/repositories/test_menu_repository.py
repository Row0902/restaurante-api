"""Tests for MenuRepository — all methods mocked at the AsyncSession boundary.

Following Strict TDD: RED phase — test written before production code.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from core.exceptions import MenuNotFoundError
from core.models.menu import MenuItem
from core.schemas.menu import PlatoCreate, PlatoUpdate
from repositories.menu import MenuRepository


@pytest.fixture
def mock_session() -> AsyncMock:
    """Return an AsyncMock specced on AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def repo(mock_session: AsyncMock) -> MenuRepository:
    """Return a MenuRepository with a mocked session injected."""
    return MenuRepository(session=mock_session)


class TestGetAll:
    """get_all returns all MenuItem rows from the database."""

    async def test_returns_items_when_exist(
        self,
        repo: MenuRepository,
        mock_session: AsyncMock,
    ) -> None:
        """get_all returns a list of MenuItem when rows exist."""
        items = [
            MenuItem(id=1, nombre="Pasta", precio=12.5),
            MenuItem(id=2, nombre="Pizza", precio=15.0),
        ]
        mock_result = MagicMock()
        mock_result.all.return_value = items
        mock_session.exec.return_value = mock_result

        result = await repo.get_all()

        assert result == items
        mock_session.exec.assert_awaited_once()

    async def test_returns_empty_list_when_no_items(
        self,
        repo: MenuRepository,
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
    """get_by_id returns a single MenuItem by primary key."""

    async def test_returns_item_when_found(
        self,
        repo: MenuRepository,
        mock_session: AsyncMock,
    ) -> None:
        """get_by_id returns the MenuItem when the id exists."""
        expected = MenuItem(id=1, nombre="Pasta", precio=12.5)
        mock_session.get.return_value = expected

        result = await repo.get_by_id(1)

        assert result is expected
        assert result.nombre == "Pasta"
        assert result.precio == 12.5
        mock_session.get.assert_awaited_once_with(MenuItem, 1)

    async def test_raises_not_found_when_missing(
        self,
        repo: MenuRepository,
        mock_session: AsyncMock,
    ) -> None:
        """get_by_id raises MenuNotFoundError when the id does not exist."""
        mock_session.get.return_value = None

        with pytest.raises(MenuNotFoundError) as excinfo:
            await repo.get_by_id(99)

        assert str(excinfo.value) == "Menu item 99 not found."
        mock_session.get.assert_awaited_once_with(MenuItem, 99)


class TestCreate:
    """create persists a new MenuItem from PlatoCreate data."""

    async def test_returns_item_with_generated_id(
        self,
        repo: MenuRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Create returns a MenuItem with id and correct field values."""
        data = PlatoCreate(nombre="Pasta", precio=12.5)

        # Capture the item passed to session.add so we can mutate it during flush
        captured: list[MenuItem] = []

        def capture_add(item: MenuItem) -> None:
            captured.append(item)

        async def set_id_on_flush() -> None:
            if captured:
                captured[0].id = 1

        mock_session.add.side_effect = capture_add
        mock_session.flush = AsyncMock(side_effect=set_id_on_flush)
        mock_session.refresh = AsyncMock()

        result = await repo.create(data)

        assert isinstance(result, MenuItem)
        assert result.id == 1
        assert result.nombre == "Pasta"
        assert result.precio == 12.5
        assert result.categoria is None
        assert result.descripcion is None
        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()


class TestUpdate:
    """update applies partial changes to an existing MenuItem."""

    async def test_partial_update_preserves_unset_fields(
        self,
        repo: MenuRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Update only modifies fields present in PlatoUpdate."""
        original = MenuItem(
            id=1,
            nombre="Pasta",
            precio=12.5,
            categoria="Principal",
            descripcion="Clasica italiana",
        )
        mock_session.get.return_value = original
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        data = PlatoUpdate(nombre="Pizza")
        result = await repo.update(1, data)

        assert result.nombre == "Pizza"
        assert result.precio == 12.5  # unchanged
        assert result.categoria == "Principal"  # unchanged
        assert result.descripcion == "Clasica italiana"  # unchanged
        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()

    async def test_raises_not_found_when_missing(
        self,
        repo: MenuRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Update raises MenuNotFoundError when the id does not exist."""
        mock_session.get.return_value = None

        with pytest.raises(MenuNotFoundError) as excinfo:
            await repo.update(99, PlatoUpdate(nombre="Pizza"))

        assert "99" in str(excinfo.value)


class TestDelete:
    """delete removes an existing MenuItem from the database."""

    async def test_completes_without_error(
        self,
        repo: MenuRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Delete succeeds when the item exists."""
        item = MenuItem(id=1, nombre="Pasta", precio=12.5)
        mock_session.get.return_value = item
        mock_session.flush = AsyncMock()

        await repo.delete(1)

        mock_session.get.assert_awaited_once_with(MenuItem, 1)
        mock_session.delete.assert_called_once_with(item)
        mock_session.flush.assert_awaited_once()

    async def test_raises_not_found_when_missing(
        self,
        repo: MenuRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Delete raises MenuNotFoundError when the id does not exist."""
        mock_session.get.return_value = None

        with pytest.raises(MenuNotFoundError) as excinfo:
            await repo.delete(99)

        assert "99" in str(excinfo.value)
