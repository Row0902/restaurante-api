"""Integration tests for the refactored menu API router.

Tests the new APIRouter-based endpoints with a real SQLite database
via httpx.ASGITransport. Uses dependency_overrides to isolate the
test database from the development database.
"""

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from api.deps import get_menu_service
from api.routers.menu import router as menu_router
from repositories.menu import MenuRepository
from services.menu import MenuService

TEST_DB_URL = "sqlite+aiosqlite:///./test_menu_refactored.db"


@pytest_asyncio.fixture
async def test_engine():
    """Create a test engine with fresh tables per test function."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_app(test_engine):
    """Build a standalone FastAPI app with overridden DI for testing."""
    app = FastAPI()
    app.include_router(menu_router)

    async def get_test_service():
        async with AsyncSession(test_engine) as session:
            repository = MenuRepository(session)
            service = MenuService(repository)
            yield service
            await session.commit()

    app.dependency_overrides[get_menu_service] = get_test_service
    return app


@pytest_asyncio.fixture
async def client(test_app):
    """Create an async HTTP client scoped to one test."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        yield ac


class TestListMenu:
    """GET /menu — list all menu items."""

    async def test_list_empty(self, client: AsyncClient) -> None:
        """Returns 200 with empty list when no dishes exist."""
        response = await client.get("/menu")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_populated(self, client: AsyncClient) -> None:
        """Returns 200 with all dishes when items exist."""
        await client.post("/menu", json={"nombre": "Pasta", "precio": 12.5})
        await client.post("/menu", json={"nombre": "Pizza", "precio": 15.0})
        response = await client.get("/menu")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["nombre"] == "Pasta"
        assert data[0]["precio"] == 12.5
        assert data[1]["nombre"] == "Pizza"
        assert data[1]["precio"] == 15.0


class TestCreateMenuItem:
    """POST /menu — create a new menu item."""

    async def test_create_valid(self, client: AsyncClient) -> None:
        """Returns 201 with the created dish including assigned id."""
        response = await client.post("/menu", json={"nombre": "Pasta", "precio": 12.5})
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Pasta"
        assert data["precio"] == 12.5
        assert isinstance(data["id"], int)

    async def test_create_invalid_empty_nombre(self, client: AsyncClient) -> None:
        """Returns 422 when nombre is empty."""
        response = await client.post("/menu", json={"nombre": "", "precio": 12.5})
        assert response.status_code == 422
        assert "nombre" in response.json()["detail"]


class TestGetMenuItem:
    """GET /menu/{plato_id} — retrieve a single menu item."""

    async def test_get_existing(self, client: AsyncClient) -> None:
        """Returns 200 with the stored dish data."""
        create_resp = await client.post(
            "/menu", json={"nombre": "Pasta", "precio": 12.5}
        )
        plato_id = create_resp.json()["id"]
        response = await client.get(f"/menu/{plato_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Pasta"
        assert data["precio"] == 12.5

    async def test_get_missing(self, client: AsyncClient) -> None:
        """Returns 404 when the dish does not exist."""
        response = await client.get("/menu/999")
        assert response.status_code == 404
        assert "999" in response.json()["detail"]


class TestUpdateMenuItem:
    """PUT /menu/{plato_id} — update an existing menu item."""

    async def test_update_existing(self, client: AsyncClient) -> None:
        """Returns 200 with updated fields; unset fields preserved."""
        create_resp = await client.post(
            "/menu", json={"nombre": "Pasta", "precio": 12.5}
        )
        plato_id = create_resp.json()["id"]
        response = await client.put(f"/menu/{plato_id}", json={"nombre": "Pizza"})
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Pizza"
        assert data["precio"] == 12.5

    async def test_update_missing(self, client: AsyncClient) -> None:
        """Returns 404 when updating a non-existent dish."""
        response = await client.put("/menu/999", json={"nombre": "Pizza"})
        assert response.status_code == 404


class TestDeleteMenuItem:
    """DELETE /menu/{plato_id} — remove a menu item."""

    async def test_delete_existing(self, client: AsyncClient) -> None:
        """Returns 204 with empty body on successful deletion."""
        create_resp = await client.post(
            "/menu", json={"nombre": "Pasta", "precio": 12.5}
        )
        plato_id = create_resp.json()["id"]
        response = await client.delete(f"/menu/{plato_id}")
        assert response.status_code == 204
        assert response.content == b""

    async def test_delete_missing(self, client: AsyncClient) -> None:
        """Returns 404 when deleting a non-existent dish."""
        response = await client.delete("/menu/999")
        assert response.status_code == 404


class TestDIWiring:
    """Verify the full DI chain (service -> repository -> DB) works."""

    async def test_di_wiring(self, client: AsyncClient) -> None:
        """Proves get_menu_service returns a working MenuService."""
        response = await client.post(
            "/menu", json={"nombre": "Ensalada", "precio": 8.5}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Ensalada"
        assert data["precio"] == 8.5
        assert isinstance(data["id"], int)
