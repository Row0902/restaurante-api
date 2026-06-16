"""Unit tests for MenuRepository with mocked AsyncSession."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.models import Plato
from repositories.menu import MenuRepository


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mocked AsyncSession."""
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def menu_repo(mock_session: AsyncMock) -> MenuRepository:
    """Create MenuRepository with mocked session."""
    return MenuRepository(session=mock_session)


async def test_get_all_returns_list(
    menu_repo: MenuRepository, mock_session: AsyncMock
) -> None:
    """Verify get_all returns list of Plato."""
    mock_result = MagicMock()
    mock_result.all.return_value = [Plato(id=1, nombre="Test", precio=100.0)]
    mock_session.exec.return_value = mock_result

    result = await menu_repo.get_all()

    assert len(result) == 1
    assert isinstance(result[0], Plato)
    mock_session.exec.assert_called_once()


async def test_get_by_id_found(
    menu_repo: MenuRepository, mock_session: AsyncMock
) -> None:
    """Verify get_by_id returns Plato when found."""
    plato = Plato(id=1, nombre="Test", precio=100.0)
    mock_session.get.return_value = plato

    result = await menu_repo.get_by_id(1)

    assert result is not None
    assert result.id == 1
    mock_session.get.assert_called_once_with(Plato, 1)


async def test_get_by_id_not_found(
    menu_repo: MenuRepository, mock_session: AsyncMock
) -> None:
    """Verify get_by_id returns None when not found."""
    mock_session.get.return_value = None

    result = await menu_repo.get_by_id(999)

    assert result is None


async def test_add_commits_and_returns(
    menu_repo: MenuRepository, mock_session: AsyncMock
) -> None:
    """Verify add calls session.add, commit, refresh."""
    plato = Plato(nombre="Test", precio=100.0)

    result = await menu_repo.add(plato)

    mock_session.add.assert_called_once_with(plato)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(plato)
    assert result is plato


async def test_update_existing(
    menu_repo: MenuRepository, mock_session: AsyncMock
) -> None:
    """Verify update modifies only non-None values."""
    plato = Plato(id=1, nombre="Old", precio=100.0, disponible=True)
    mock_session.get.return_value = plato

    result = await menu_repo.update(1, {"nombre": "New", "precio": None})

    assert result is not None
    assert result.nombre == "New"
    assert result.precio == 100.0
    mock_session.add.assert_called_once_with(plato)
    mock_session.commit.assert_called_once()


async def test_update_not_found(
    menu_repo: MenuRepository, mock_session: AsyncMock
) -> None:
    """Verify update returns None when not found."""
    mock_session.get.return_value = None

    result = await menu_repo.update(999, {"nombre": "New"})

    assert result is None
    mock_session.add.assert_not_called()


async def test_delete_existing(
    menu_repo: MenuRepository, mock_session: AsyncMock
) -> None:
    """Verify delete calls session.delete and returns True."""
    plato = Plato(id=1, nombre="Test", precio=100.0)
    mock_session.get.return_value = plato

    result = await menu_repo.delete(1)

    assert result is True
    mock_session.delete.assert_called_once_with(plato)
    mock_session.commit.assert_called_once()


async def test_delete_not_found(
    menu_repo: MenuRepository, mock_session: AsyncMock
) -> None:
    """Verify delete returns False when not found."""
    mock_session.get.return_value = None

    result = await menu_repo.delete(999)

    assert result is False
    mock_session.delete.assert_not_called()
