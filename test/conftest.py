"""Fixtures compartidas para los tests."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from db.session import get_session
from main import app

engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)


@pytest.fixture
def anyio_backend():
    """Backend de anyio para pytest."""
    return "asyncio"


@pytest.fixture
async def setup_db():
    """Crea y destruye las tablas de la base de datos de pruebas."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def session(setup_db):
    """Provee una sesión de base de datos aislada."""
    async with AsyncSession(engine) as session:
        yield session


@pytest.fixture
async def client(session: AsyncSession):
    """Cliente HTTP de pruebas con la dependencia de base de datos mockeada."""
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
