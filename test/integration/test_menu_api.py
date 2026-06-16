"""Integration tests for menu API via main.app with dependency overrides.

Tests the refactored menu router through the actual FastAPI application,
using a file-based SQLite test database isolated via dependency_overrides.
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from api.deps import get_menu_service
from main import app
from repositories.menu import MenuRepository
from services.menu import MenuService

TEST_DB_URL = "sqlite+aiosqlite:///./test_menu_migrated.db"


@pytest_asyncio.fixture(autouse=True)
async def _setup_db():
    """Create fresh tables and override DI before each test; clean up after."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async def _get_test_service():
        async with AsyncSession(engine) as session:
            repository = MenuRepository(session)
            yield MenuService(repository)
            await session.commit()

    app.dependency_overrides[get_menu_service] = _get_test_service
    yield
    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def client() -> TestClient:
    """Return a sync TestClient wrapping main.app."""
    return TestClient(app)


class TestListMenu:
    """GET /menu — list all menu items."""

    def test_list_empty(self, client: TestClient) -> None:
        """Returns 200 with empty list when no dishes exist."""
        response = client.get("/menu")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_populated(self, client: TestClient) -> None:
        """Returns 200 with all dishes when items exist."""
        client.post("/menu", json={"nombre": "Pasta", "precio": 12.5})
        client.post("/menu", json={"nombre": "Pizza", "precio": 15.0})
        response = client.get("/menu")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["nombre"] == "Pasta"
        assert data[0]["precio"] == 12.5
        assert data[1]["nombre"] == "Pizza"
        assert data[1]["precio"] == 15.0


class TestCreateMenuItem:
    """POST /menu — create a new menu item."""

    def test_create_valid(self, client: TestClient) -> None:
        """Returns 201 with the created dish including an int id."""
        response = client.post("/menu", json={"nombre": "Pasta", "precio": 12.5})
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Pasta"
        assert data["precio"] == 12.5
        assert isinstance(data["id"], int)

    def test_create_invalid_empty_nombre(self, client: TestClient) -> None:
        """Returns 422 when nombre is an empty string."""
        response = client.post("/menu", json={"nombre": "", "precio": 12.5})
        assert response.status_code == 422
        assert "nombre" in response.json()["detail"]

    def test_create_invalid_zero_precio(self, client: TestClient) -> None:
        """Returns 422 when precio is zero."""
        response = client.post("/menu", json={"nombre": "X", "precio": 0})
        assert response.status_code == 422
        assert "precio" in response.json()["detail"]

    def test_create_extra_fields_silently_dropped(self, client: TestClient) -> None:
        """Extra fields in the payload are silently dropped by Pydantic."""
        response = client.post(
            "/menu", json={"nombre": "X", "precio": 1, "extra": "ignored"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "extra" not in data


class TestGetMenuItem:
    """GET /menu/{plato_id} — retrieve a single menu item."""

    def test_get_existing(self, client: TestClient) -> None:
        """Returns 200 with the stored dish data."""
        create_resp = client.post("/menu", json={"nombre": "Pasta", "precio": 12.5})
        plato_id = create_resp.json()["id"]
        response = client.get(f"/menu/{plato_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Pasta"
        assert data["precio"] == 12.5

    def test_get_missing(self, client: TestClient) -> None:
        """Returns 404 when the dish does not exist."""
        response = client.get("/menu/999")
        assert response.status_code == 404
        assert "999" in response.json()["detail"]


class TestUpdateMenuItem:
    """PUT /menu/{plato_id} — update an existing menu item."""

    def test_update_existing(self, client: TestClient) -> None:
        """Returns 200 with updated fields; unset fields preserved."""
        create_resp = client.post("/menu", json={"nombre": "Pasta", "precio": 12.5})
        plato_id = create_resp.json()["id"]
        response = client.put(f"/menu/{plato_id}", json={"nombre": "Pizza"})
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Pizza"
        assert data["precio"] == 12.5

    def test_update_missing(self, client: TestClient) -> None:
        """Returns 404 when updating a non-existent dish."""
        response = client.put("/menu/999", json={"nombre": "Pizza"})
        assert response.status_code == 404


class TestDeleteMenuItem:
    """DELETE /menu/{plato_id} — remove a menu item."""

    def test_delete_existing(self, client: TestClient) -> None:
        """Returns 204 with empty body on successful deletion."""
        create_resp = client.post("/menu", json={"nombre": "Pasta", "precio": 12.5})
        plato_id = create_resp.json()["id"]
        response = client.delete(f"/menu/{plato_id}")
        assert response.status_code == 204
        assert response.content == b""

    def test_delete_missing(self, client: TestClient) -> None:
        """Returns 404 when deleting a non-existent dish."""
        response = client.delete("/menu/999")
        assert response.status_code == 404


class TestDIWiring:
    """Verify the full DI chain (service -> repository -> DB) works."""

    def test_di_wiring_full_chain(self, client: TestClient) -> None:
        """Proves get_menu_service returns a working MenuService."""
        response = client.post("/menu", json={"nombre": "Ensalada", "precio": 8.5})
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Ensalada"
        assert data["precio"] == 8.5
        assert isinstance(data["id"], int)
