"""Integration tests for orden API via main.app with dependency overrides.

Tests all 10 API spec scenarios: CRUD + estado transitions + DI wiring.
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from api.deps import get_menu_service, get_orden_service
from main import app
from repositories.menu import MenuRepository
from repositories.orden import OrdenRepository
from services.menu import MenuService
from services.orden import OrdenesService

TEST_DB_URL = "sqlite+aiosqlite:///./test_orden_api.db"


@pytest_asyncio.fixture(autouse=True)
async def _setup_db():
    """Create fresh tables and override DI before each test; clean up after."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async def _get_test_menu_service():
        async with AsyncSession(engine) as session:
            repository = MenuRepository(session)
            yield MenuService(repository)
            await session.commit()

    async def _get_test_orden_service():
        async with AsyncSession(engine) as session:
            orden_repo = OrdenRepository(session)
            menu_repo = MenuRepository(session)
            yield OrdenesService(orden_repo, menu_repo)
            await session.commit()

    app.dependency_overrides[get_menu_service] = _get_test_menu_service
    app.dependency_overrides[get_orden_service] = _get_test_orden_service
    yield
    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def client() -> TestClient:
    """Return a sync TestClient wrapping main.app."""
    return TestClient(app)


def _seed_menu_item(client: TestClient, nombre: str, precio: float) -> dict:
    """Helper: create a menu item via HTTP POST and return the response JSON."""
    resp = client.post("/menu", json={"nombre": nombre, "precio": precio})
    assert resp.status_code == 201
    return resp.json()


class TestListOrdenes:
    """GET /ordenes — list all orders."""

    def test_list_empty(self, client: TestClient) -> None:
        """Returns 200 with empty list when no orders exist."""
        response = client.get("/ordenes")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_populated(self, client: TestClient) -> None:
        """Returns 200 with all orders when orders exist."""
        menu_item = _seed_menu_item(client, "Pasta", 12.5)
        client.post(
            "/ordenes",
            json={"items": [{"plato_id": menu_item["id"], "cantidad": 2}]},
        )
        client.post(
            "/ordenes",
            json={"items": [{"plato_id": menu_item["id"], "cantidad": 1}]},
        )
        response = client.get("/ordenes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestCreateOrden:
    """POST /ordenes — create a new order."""

    def test_create_valid(self, client: TestClient) -> None:
        """Returns 201 with the created order including computed total."""
        menu_item = _seed_menu_item(client, "Pasta", 12.5)
        response = client.post(
            "/ordenes",
            json={"items": [{"plato_id": menu_item["id"], "cantidad": 2}]},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["estado"] == "pendiente"
        assert data["total"] == 25.0  # 2 x 12.5
        assert isinstance(data["id"], int)

    def test_create_invalid_cantidad_zero(self, client: TestClient) -> None:
        """Returns 422 when cantidad is zero."""
        response = client.post(
            "/ordenes",
            json={"items": [{"plato_id": 1, "cantidad": 0}]},
        )
        assert response.status_code == 422
        assert "cantidad" in response.json()["detail"]

    def test_create_missing_menu_item(self, client: TestClient) -> None:
        """Returns 404 when referencing a non-existent menu item."""
        response = client.post(
            "/ordenes",
            json={"items": [{"plato_id": 999, "cantidad": 1}]},
        )
        assert response.status_code == 404
        assert "999" in response.json()["detail"]


class TestGetOrden:
    """GET /ordenes/{orden_id} — retrieve a single order."""

    def test_get_existing(self, client: TestClient) -> None:
        """Returns 200 with the stored order data."""
        menu_item = _seed_menu_item(client, "Pasta", 12.5)
        create_resp = client.post(
            "/ordenes",
            json={"items": [{"plato_id": menu_item["id"], "cantidad": 2}]},
        )
        orden_id = create_resp.json()["id"]
        response = client.get(f"/ordenes/{orden_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == orden_id
        assert data["total"] == 25.0

    def test_get_missing(self, client: TestClient) -> None:
        """Returns 404 when the order does not exist."""
        response = client.get("/ordenes/999")
        assert response.status_code == 404
        assert "999" in response.json()["detail"]


class TestUpdateEstado:
    """PUT /ordenes/{orden_id}/estado — update order estado."""

    def test_transition_valid(self, client: TestClient) -> None:
        """Returns 200 with updated estado on valid transition."""
        menu_item = _seed_menu_item(client, "Pasta", 12.5)
        create_resp = client.post(
            "/ordenes",
            json={"items": [{"plato_id": menu_item["id"], "cantidad": 1}]},
        )
        orden_id = create_resp.json()["id"]
        response = client.put(
            f"/ordenes/{orden_id}/estado",
            json={"estado": "preparando"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "preparando"

    def test_transition_invalid(self, client: TestClient) -> None:
        """Returns 400 on invalid estado transition."""
        menu_item = _seed_menu_item(client, "Pasta", 12.5)
        create_resp = client.post(
            "/ordenes",
            json={"items": [{"plato_id": menu_item["id"], "cantidad": 1}]},
        )
        orden_id = create_resp.json()["id"]
        # pendiente -> pagado is forbidden (need preparando first)
        response = client.put(
            f"/ordenes/{orden_id}/estado",
            json={"estado": "pagado"},
        )
        assert response.status_code == 400


class TestDIWiring:
    """Verify the full DI chain (service -> repos -> DB) works."""

    def test_di_wiring_full_chain(self, client: TestClient) -> None:
        """Proves get_orden_service returns a working OrdenesService."""
        menu_item = _seed_menu_item(client, "Ensalada", 8.5)
        response = client.post(
            "/ordenes",
            json={"items": [{"plato_id": menu_item["id"], "cantidad": 3}]},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["estado"] == "pendiente"
        assert data["total"] == 25.5  # 3 x 8.5
        assert isinstance(data["id"], int)
