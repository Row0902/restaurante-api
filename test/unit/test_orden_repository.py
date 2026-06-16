"""Unit tests for OrdenRepository with mocked AsyncSession."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.models import Orden
from repositories.ordenes import OrdenRepository


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mocked AsyncSession."""
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def orden_repo(mock_session: AsyncMock) -> OrdenRepository:
    """Create OrdenRepository with mocked session."""
    return OrdenRepository(session=mock_session)


async def test_get_all_returns_list(
    orden_repo: OrdenRepository, mock_session: AsyncMock
) -> None:
    """Verify get_all returns list of Orden."""
    mock_result = MagicMock()
    mock_result.all.return_value = [Orden(id=1)]
    mock_session.exec.return_value = mock_result

    result = await orden_repo.get_all()

    assert len(result) == 1
    assert isinstance(result[0], Orden)
    mock_session.exec.assert_called_once()


async def test_get_by_id_found(
    orden_repo: OrdenRepository, mock_session: AsyncMock
) -> None:
    """Verify get_by_id returns Orden when found."""
    orden = Orden(id=1, estado="pendiente")
    mock_session.get.return_value = orden

    result = await orden_repo.get_by_id(1)

    assert result is not None
    assert result.id == 1
    mock_session.get.assert_called_once_with(Orden, 1)


async def test_get_by_id_not_found(
    orden_repo: OrdenRepository, mock_session: AsyncMock
) -> None:
    """Verify get_by_id returns None when not found."""
    mock_session.get.return_value = None

    result = await orden_repo.get_by_id(999)

    assert result is None


async def test_add_commits_and_returns(
    orden_repo: OrdenRepository, mock_session: AsyncMock
) -> None:
    """Verify add calls session.add, commit, refresh."""
    orden = Orden()

    result = await orden_repo.add(orden)

    mock_session.add.assert_called_once_with(orden)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(orden)
    assert result is orden


async def test_update_estado_existing(
    orden_repo: OrdenRepository, mock_session: AsyncMock
) -> None:
    """Verify update_estado modifies estado field."""
    orden = Orden(id=1, estado="pendiente")
    mock_session.get.return_value = orden

    result = await orden_repo.update_estado(1, "entregado")

    assert result is not None
    assert result.estado == "entregado"
    mock_session.add.assert_called_once_with(orden)
    mock_session.commit.assert_called_once()


async def test_update_estado_not_found(
    orden_repo: OrdenRepository, mock_session: AsyncMock
) -> None:
    """Verify update_estado returns None when not found."""
    mock_session.get.return_value = None

    result = await orden_repo.update_estado(999, "entregado")

    assert result is None
    mock_session.add.assert_not_called()
