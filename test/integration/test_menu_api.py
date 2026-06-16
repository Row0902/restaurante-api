"""Integration tests for menu API endpoints."""

from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from core.exceptions import NotFoundError
from core.models import Plato


@pytest.fixture
def _mock_menu_service() -> AsyncMock:
    """Create a mock MenuService with default success responses."""
    mock = AsyncMock()
    mock.list_all.return_value = [
        Plato(
            id=1,
            nombre="Milanesa",
            precio=1500.0,
            descripcion="Con pure",
            disponible=True,
        ),
    ]
    mock.get_by_id.return_value = Plato(
        id=1, nombre="Milanesa", precio=1500.0, descripcion="Con pure", disponible=True
    )
    mock.create.return_value = Plato(
        id=2, nombre="Ensalada", precio=800.0, descripcion=None, disponible=True
    )
    mock.update.return_value = Plato(
        id=1,
        nombre="Actualizado",
        precio=1500.0,
        descripcion="Con pure",
        disponible=True,
    )
    mock.delete.return_value = True
    return mock


@pytest.fixture
def client(_mock_menu_service: AsyncMock, request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """Set up test client with overridden dependencies."""
    from api.deps import get_menu_service
    from main import app

    app.dependency_overrides[get_menu_service] = lambda: _mock_menu_service

    fail_marker = getattr(request, "param", "default")
    if fail_marker == "not-found":
        _mock_menu_service.get_by_id.side_effect = NotFoundError(
            "Plato with id 999 not found"
        )
    elif fail_marker == "update-not-found":
        _mock_menu_service.update.side_effect = NotFoundError(
            "Plato with id 999 not found"
        )
    elif fail_marker == "empty":
        _mock_menu_service.list_all.return_value = []

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


async def test_list_menu_empty(async_client: AsyncClient) -> None:
    """Verify GET /menu returns empty list when no items."""
    from api.deps import get_menu_service
    from main import app

    mock = AsyncMock()
    mock.list_all.return_value = []
    app.dependency_overrides[get_menu_service] = lambda: mock

    response = await async_client.get("/menu")

    assert response.status_code == 200
    assert response.json() == []
    app.dependency_overrides.clear()


async def test_list_menu_with_items(async_client: AsyncClient) -> None:
    """Verify GET /menu returns list of menu items."""
    response = await async_client.get("/menu")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["nombre"] == "Milanesa"


async def test_create_plato(async_client: AsyncClient) -> None:
    """Verify POST /menu returns 201 with created item."""
    response = await async_client.post(
        "/menu", json={"nombre": "Ensalada", "precio": 800.0}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Ensalada"


async def test_create_plato_validation_error(async_client: AsyncClient) -> None:
    """Verify POST /menu returns 422 for invalid data."""
    response = await async_client.post("/menu", json={"precio": -100.0})

    assert response.status_code == 422


async def test_get_plato_found(async_client: AsyncClient) -> None:
    """Verify GET /menu/{id} returns PlatoResponse."""
    response = await async_client.get("/menu/1")

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Milanesa"
    assert data["precio"] == 1500.0


async def test_get_plato_not_found(async_client: AsyncClient) -> None:
    """Verify GET /menu/{id} returns 404 with message when not found."""
    from api.deps import get_menu_service
    from main import app

    mock = AsyncMock()
    mock.get_by_id.side_effect = NotFoundError("Plato with id 999 not found")
    app.dependency_overrides[get_menu_service] = lambda: mock

    response = await async_client.get("/menu/999")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "999" in str(data["detail"])
    app.dependency_overrides.clear()


async def test_delete_plato(async_client: AsyncClient) -> None:
    """Verify DELETE /menu/{id} returns 204."""
    response = await async_client.delete("/menu/1")

    assert response.status_code == 204
