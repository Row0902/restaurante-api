"""Tests para la API de restaurante (endpoints reales con SQLite en memoria)."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from main import app
from repositories.database import get_session

TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest.mark.anyio
async def test_raiz():
    """Verifica que el endpoint raíz responda correctamente."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"mensaje": "API corriendo"}


@pytest.mark.anyio
async def test_listar_menu_vacio():
    """Verifica que el menú vacío devuelva lista vacía."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    test_session_local = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_session():
        async with test_session_local() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/menu")
            assert response.status_code == 200
            assert response.json() == []
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()
