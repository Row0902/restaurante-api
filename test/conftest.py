# test/conftest.py
"""Fixtures globales para pruebas de integración."""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from api.deps import get_session
from main import app

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(name="db_session")
async def db_session_fixture():
    """Crea una base de datos en memoria y proporciona una sesión asíncrona."""
    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture(name="client")
async def client_fixture(db_session):
    """Proporciona un cliente HTTP asíncrono configurado con la base de datos de pruebas."""

    async def _get_test_session():
        yield db_session

    app.dependency_overrides[get_session] = _get_test_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
