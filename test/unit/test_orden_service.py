"""Unit tests for OrdenService with mocked repositories."""

from unittest.mock import AsyncMock

import pytest

from core.exceptions import NotFoundError
from core.models import Orden, Plato
from core.schemas import OrdenCreate, OrdenItemSchema
from services.ordenes import OrdenService


@pytest.fixture
def mock_orden_repo() -> AsyncMock:
    """Create a mocked OrdenRepository."""
    return AsyncMock()


@pytest.fixture
def mock_menu_repo() -> AsyncMock:
    """Create a mocked MenuRepository."""
    return AsyncMock()


@pytest.fixture
def orden_service(
    mock_orden_repo: AsyncMock, mock_menu_repo: AsyncMock
) -> OrdenService:
    """Create OrdenService with mocked repositories."""
    return OrdenService(
        orden_repo=mock_orden_repo,
        menu_repo=mock_menu_repo,
    )


async def test_list_all_delegates_to_repo(
    orden_service: OrdenService, mock_orden_repo: AsyncMock
) -> None:
    """Verify list_all calls repo.get_all and returns results."""
    expected = [Orden(id=1)]
    mock_orden_repo.get_all.return_value = expected

    result = await orden_service.list_all()

    assert result == expected
    mock_orden_repo.get_all.assert_called_once()


async def test_get_by_id_delegates_to_repo(
    orden_service: OrdenService, mock_orden_repo: AsyncMock
) -> None:
    """Verify get_by_id calls repo.get_by_id and returns Orden."""
    expected = Orden(id=1, estado="pendiente")
    mock_orden_repo.get_by_id.return_value = expected

    result = await orden_service.get_by_id(1)

    assert result == expected
    mock_orden_repo.get_by_id.assert_called_once_with(1)


async def test_get_by_id_not_found_raises(
    orden_service: OrdenService, mock_orden_repo: AsyncMock
) -> None:
    """Verify get_by_id raises NotFoundError when not found."""
    mock_orden_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await orden_service.get_by_id(999)


async def test_create_calculates_total(
    orden_service: OrdenService,
    mock_orden_repo: AsyncMock,
    mock_menu_repo: AsyncMock,
) -> None:
    """Verify create calculates total from menu prices."""
    plato_a = Plato(id=1, nombre="A", precio=100.0)
    plato_b = Plato(id=2, nombre="B", precio=200.0)

    async def get_by_id_side_effect(plato_id: int) -> Plato | None:
        return {1: plato_a, 2: plato_b}.get(plato_id)

    mock_menu_repo.get_by_id.side_effect = get_by_id_side_effect
    mock_orden_repo.add.side_effect = lambda o: Orden(
        id=1,
        items=o.items,
        total=o.total,
        estado=o.estado,
    )

    data = OrdenCreate(
        items=[
            OrdenItemSchema(plato_id=1, cantidad=2),
            OrdenItemSchema(plato_id=2, cantidad=1),
        ]
    )
    result = await orden_service.create(data)

    assert result.total == 400.0  # (100*2) + (200*1)
    assert result.estado == "pendiente"
    assert mock_menu_repo.get_by_id.call_count == 2
    mock_orden_repo.add.assert_called_once()


async def test_create_raises_on_missing_menu_item(
    orden_service: OrdenService, mock_menu_repo: AsyncMock
) -> None:
    """Verify create raises NotFoundError when menu item missing."""
    mock_menu_repo.get_by_id.return_value = None

    data = OrdenCreate(items=[OrdenItemSchema(plato_id=999, cantidad=1)])

    with pytest.raises(NotFoundError):
        await orden_service.create(data)


async def test_update_estado_delegates_to_repo(
    orden_service: OrdenService, mock_orden_repo: AsyncMock
) -> None:
    """Verify update_estado calls repo.update_estado and returns Orden."""
    expected = Orden(id=1, estado="entregado")
    mock_orden_repo.update_estado.return_value = expected

    result = await orden_service.update_estado(1, "entregado")

    assert result is not None
    assert result.estado == "entregado"
    mock_orden_repo.update_estado.assert_called_once_with(1, "entregado")


async def test_update_estado_not_found_raises(
    orden_service: OrdenService, mock_orden_repo: AsyncMock
) -> None:
    """Verify update_estado raises NotFoundError when order not found."""
    mock_orden_repo.update_estado.return_value = None

    with pytest.raises(NotFoundError):
        await orden_service.update_estado(999, "entregado")
