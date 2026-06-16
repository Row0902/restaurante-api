"""Tests for MenuService — all methods mocked at the MenuRepository boundary.

Following Strict TDD: RED phase — test written before production code.
"""

from unittest.mock import AsyncMock

import pytest

from core.exceptions import InvalidMenuDataError, MenuNotFoundError
from core.models.menu import MenuItem
from core.schemas.menu import PlatoCreate, PlatoUpdate
from repositories.menu import MenuRepository
from services.menu import MenuService


@pytest.fixture
def mock_repo() -> AsyncMock:
    """Return an AsyncMock specced on MenuRepository."""
    return AsyncMock(spec=MenuRepository)


@pytest.fixture
def service(mock_repo: AsyncMock) -> MenuService:
    """Return a MenuService with a mocked repository injected."""
    return MenuService(repository=mock_repo)


class TestGetAll:
    """get_all delegates to repo.get_all and returns result unchanged."""

    async def test_returns_items_unchanged(
        self,
        mock_repo: AsyncMock,
        service: MenuService,
    ) -> None:
        """get_all returns the same list that repo.get_all returns."""
        items = [
            MenuItem(id=1, nombre="Pasta", precio=12.5),
            MenuItem(id=2, nombre="Pizza", precio=15.0),
        ]
        mock_repo.get_all.return_value = items

        result = await service.get_all()

        assert result == items
        mock_repo.get_all.assert_awaited_once()

    async def test_returns_empty_list_when_no_items(
        self,
        mock_repo: AsyncMock,
        service: MenuService,
    ) -> None:
        """get_all returns an empty list when the repo returns empty."""
        mock_repo.get_all.return_value = []

        result = await service.get_all()

        assert result == []
        mock_repo.get_all.assert_awaited_once()


class TestGetById:
    """get_by_id delegates to repo.get_by_id and returns result unchanged."""

    async def test_returns_item_when_found(
        self,
        mock_repo: AsyncMock,
        service: MenuService,
    ) -> None:
        """get_by_id returns the MenuItem from the repo."""
        expected = MenuItem(id=1, nombre="Pasta", precio=12.5)
        mock_repo.get_by_id.return_value = expected

        result = await service.get_by_id(1)

        assert result is expected
        assert result.nombre == "Pasta"
        assert result.precio == 12.5
        mock_repo.get_by_id.assert_awaited_once_with(1)

    async def test_propagates_not_found_error(
        self,
        mock_repo: AsyncMock,
        service: MenuService,
    ) -> None:
        """get_by_id propagates MenuNotFoundError from the repo."""
        mock_repo.get_by_id.side_effect = MenuNotFoundError(99)

        with pytest.raises(MenuNotFoundError) as excinfo:
            await service.get_by_id(99)

        assert str(excinfo.value) == "Menu item 99 not found."
        mock_repo.get_by_id.assert_awaited_once_with(99)


class TestCreate:
    """create validates data then delegates to repo.create."""

    async def test_valid_data_calls_repo(
        self,
        mock_repo: AsyncMock,
        service: MenuService,
    ) -> None:
        """Create calls validate() then repo.create() for valid data."""
        data = PlatoCreate(nombre="Pasta", precio=12.5)
        expected = MenuItem(id=1, nombre="Pasta", precio=12.5)
        mock_repo.create.return_value = expected

        result = await service.create(data)

        assert result is expected
        assert result.nombre == "Pasta"
        mock_repo.create.assert_awaited_once_with(data)

    async def test_empty_nombre_raises_error(
        self,
        mock_repo: AsyncMock,
        service: MenuService,
    ) -> None:
        """Create raises InvalidMenuDataError for empty nombre, repo not called."""
        data = PlatoCreate(nombre="", precio=12.5)

        with pytest.raises(InvalidMenuDataError) as excinfo:
            await service.create(data)

        assert str(excinfo.value) == "nombre is required."
        mock_repo.create.assert_not_awaited()

    async def test_zero_precio_raises_error(
        self,
        mock_repo: AsyncMock,
        service: MenuService,
    ) -> None:
        """Create raises InvalidMenuDataError for non-positive precio, repo not called."""
        data = PlatoCreate(nombre="Pasta", precio=0)

        with pytest.raises(InvalidMenuDataError) as excinfo:
            await service.create(data)

        assert str(excinfo.value) == "precio must be positive."
        mock_repo.create.assert_not_awaited()


class TestUpdate:
    """update validates data then delegates to repo.update."""

    async def test_valid_partial_calls_repo(
        self,
        mock_repo: AsyncMock,
        service: MenuService,
    ) -> None:
        """Update calls validate() then repo.update() for valid partial data."""
        data = PlatoUpdate(nombre="Pizza")
        expected = MenuItem(id=1, nombre="Pizza", precio=12.5)
        mock_repo.update.return_value = expected

        result = await service.update(1, data)

        assert result is expected
        assert result.nombre == "Pizza"
        mock_repo.update.assert_awaited_once_with(1, data)

    async def test_empty_nombre_raises_error(
        self,
        mock_repo: AsyncMock,
        service: MenuService,
    ) -> None:
        """Update raises InvalidMenuDataError for empty nombre, repo not called."""
        data = PlatoUpdate(nombre="")

        with pytest.raises(InvalidMenuDataError) as excinfo:
            await service.update(1, data)

        assert str(excinfo.value) == "nombre is required."
        mock_repo.update.assert_not_awaited()

    async def test_propagates_not_found_error(
        self,
        mock_repo: AsyncMock,
        service: MenuService,
    ) -> None:
        """Update propagates MenuNotFoundError from the repo."""
        data = PlatoUpdate(nombre="Pizza")
        mock_repo.update.side_effect = MenuNotFoundError(99)

        with pytest.raises(MenuNotFoundError) as excinfo:
            await service.update(99, data)

        assert str(excinfo.value) == "Menu item 99 not found."
        mock_repo.update.assert_awaited_once_with(99, data)


class TestDelete:
    """delete delegates to repo.delete."""

    async def test_existing_item_calls_repo(
        self,
        mock_repo: AsyncMock,
        service: MenuService,
    ) -> None:
        """Delete delegates to repo.delete for an existing item."""
        mock_repo.delete.return_value = None

        await service.delete(1)

        mock_repo.delete.assert_awaited_once_with(1)

    async def test_propagates_not_found_error(
        self,
        mock_repo: AsyncMock,
        service: MenuService,
    ) -> None:
        """Delete propagates MenuNotFoundError from the repo."""
        mock_repo.delete.side_effect = MenuNotFoundError(99)

        with pytest.raises(MenuNotFoundError) as excinfo:
            await service.delete(99)

        assert str(excinfo.value) == "Menu item 99 not found."
        mock_repo.delete.assert_awaited_once_with(99)
