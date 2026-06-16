"""Unit tests for MenuService with mocked MenuRepository."""

from unittest.mock import AsyncMock

import pytest

from core.exceptions import NotFoundError
from core.models import Plato
from core.schemas import PlatoCreate, PlatoUpdate
from services.menu import MenuService


@pytest.fixture
def mock_menu_repo() -> AsyncMock:
    """Create a mocked MenuRepository."""
    return AsyncMock()


@pytest.fixture
def menu_service(mock_menu_repo: AsyncMock) -> MenuService:
    """Create MenuService with mocked repository."""
    return MenuService(menu_repo=mock_menu_repo)


async def test_list_all_delegates_to_repo(
    menu_service: MenuService, mock_menu_repo: AsyncMock
) -> None:
    """Verify list_all calls repo.get_all and returns results."""
    expected = [Plato(id=1, nombre="Test", precio=100.0)]
    mock_menu_repo.get_all.return_value = expected

    result = await menu_service.list_all()

    assert result == expected
    mock_menu_repo.get_all.assert_called_once()


async def test_get_by_id_delegates_to_repo(
    menu_service: MenuService, mock_menu_repo: AsyncMock
) -> None:
    """Verify get_by_id calls repo.get_by_id and returns Plato."""
    expected = Plato(id=1, nombre="Test", precio=100.0)
    mock_menu_repo.get_by_id.return_value = expected

    result = await menu_service.get_by_id(1)

    assert result == expected
    mock_menu_repo.get_by_id.assert_called_once_with(1)


async def test_get_by_id_not_found_raises(
    menu_service: MenuService, mock_menu_repo: AsyncMock
) -> None:
    """Verify get_by_id raises NotFoundError when not found."""
    mock_menu_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await menu_service.get_by_id(999)


async def test_create_converts_schema_and_delegates(
    menu_service: MenuService, mock_menu_repo: AsyncMock
) -> None:
    """Verify create converts PlatoCreate to Plato and delegates to repo."""
    data = PlatoCreate(nombre="Nuevo", precio=500.0)
    mock_menu_repo.add.side_effect = lambda plato: Plato(
        id=1,
        nombre=plato.nombre,
        precio=plato.precio,
    )

    result = await menu_service.create(data)

    assert isinstance(result, Plato)
    assert result.nombre == "Nuevo"
    assert result.precio == 500.0
    mock_menu_repo.add.assert_called_once()
    added = mock_menu_repo.add.call_args[0][0]
    assert isinstance(added, Plato)


async def test_update_converts_schema_and_delegates(
    menu_service: MenuService, mock_menu_repo: AsyncMock
) -> None:
    """Verify update converts PlatoUpdate and delegates to repo."""
    existing = Plato(id=1, nombre="Viejo", precio=100.0, disponible=True)
    mock_menu_repo.get_by_id.return_value = existing
    mock_menu_repo.update.return_value = Plato(
        id=1, nombre="Nuevo", precio=100.0, disponible=True
    )

    data = PlatoUpdate(nombre="Nuevo")
    result = await menu_service.update(1, data)

    assert result is not None
    assert result.nombre == "Nuevo"
    mock_menu_repo.update.assert_called_once_with(1, {"nombre": "Nuevo"})


async def test_update_not_found_raises(
    menu_service: MenuService, mock_menu_repo: AsyncMock
) -> None:
    """Verify update raises NotFoundError when item not found."""
    mock_menu_repo.get_by_id.return_value = None

    data = PlatoUpdate(nombre="Nuevo")
    with pytest.raises(NotFoundError):
        await menu_service.update(999, data)


async def test_delete_delegates_to_repo(
    menu_service: MenuService, mock_menu_repo: AsyncMock
) -> None:
    """Verify delete calls repo.delete and returns result."""
    mock_menu_repo.delete.return_value = True

    result = await menu_service.delete(1)

    assert result is True
    mock_menu_repo.delete.assert_called_once_with(1)
