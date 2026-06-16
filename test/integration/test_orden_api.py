"""Integration tests for order API endpoints."""

from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from core.exceptions import NotFoundError
from core.models import Orden, OrdenItem


@pytest.fixture
def _mock_orden_service() -> AsyncMock:
    """Create a mock OrdenService with default success responses."""
    mock = AsyncMock()
    mock.list_all.return_value = [
        Orden(
            id=1,
            items=[OrdenItem(plato_id=1, cantidad=2)],
            total=3000.0,
            estado="pendiente",
        ),
    ]
    mock.get_by_id.return_value = Orden(
        id=1,
        items=[OrdenItem(plato_id=1, cantidad=2)],
        total=3000.0,
        estado="pendiente",
    )
    mock.create.return_value = Orden(
        id=2,
        items=[OrdenItem(plato_id=1, cantidad=2)],
        total=3000.0,
        estado="pendiente",
    )
    mock.update_estado.return_value = Orden(
        id=1,
        items=[OrdenItem(plato_id=1, cantidad=2)],
        total=3000.0,
        estado="entregado",
    )
    return mock


@pytest.fixture
def client(_mock_orden_service: AsyncMock, request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """Set up test client with overridden dependencies."""
    from api.deps import get_orden_service
    from main import app

    app.dependency_overrides[get_orden_service] = lambda: _mock_orden_service

    fail_marker = getattr(request, "param", "default")
    if fail_marker == "not-found":
        _mock_orden_service.get_by_id.side_effect = NotFoundError(
            "Orden with id 999 not found"
        )
    elif fail_marker == "empty":
        _mock_orden_service.list_all.return_value = []

    yield

    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(client: None) -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP client."""
    from main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


async def test_list_ordenes_empty(async_client: AsyncClient) -> None:
    """Verify GET /ordenes returns empty list when no orders."""
    from api.deps import get_orden_service
    from main import app

    mock = AsyncMock()
    mock.list_all.return_value = []
    app.dependency_overrides[get_orden_service] = lambda: mock

    response = await async_client.get("/ordenes")

    assert response.status_code == 200
    assert response.json() == []
    app.dependency_overrides.clear()


async def test_list_ordenes_with_items(async_client: AsyncClient) -> None:
    """Verify GET /ordenes returns list of orders."""
    response = await async_client.get("/ordenes")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


async def test_create_orden(async_client: AsyncClient) -> None:
    """Verify POST /ordenes returns 201 with created order."""
    response = await async_client.post(
        "/ordenes",
        json={"items": [{"plato_id": 1, "cantidad": 2}]},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["estado"] == "pendiente"


async def test_create_orden_validation_error(async_client: AsyncClient) -> None:
    """Verify POST /ordenes returns 422 for empty items."""
    response = await async_client.post("/ordenes", json={"items": []})

    assert response.status_code == 422


async def test_get_orden_found(async_client: AsyncClient) -> None:
    """Verify GET /ordenes/{id} returns OrdenResponse."""
    response = await async_client.get("/ordenes/1")

    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "pendiente"


async def test_get_orden_not_found(async_client: AsyncClient) -> None:
    """Verify GET /ordenes/{id} returns 404 when not found."""
    from api.deps import get_orden_service
    from main import app

    mock = AsyncMock()
    mock.get_by_id.side_effect = NotFoundError("Orden with id 999 not found")
    app.dependency_overrides[get_orden_service] = lambda: mock

    response = await async_client.get("/ordenes/999")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "999" in str(data["detail"])
    app.dependency_overrides.clear()


async def test_update_estado(async_client: AsyncClient) -> None:
    """Verify PUT /ordenes/{id}/estado returns updated order."""
    response = await async_client.put("/ordenes/1/estado", json={"estado": "entregado"})

    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "entregado"
