"""Tests para database.py — engine, sesión y creación de tablas."""

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from core.database import create_engine, get_session, init_db, session_factory


class TestCreateEngine:
    def test_crea_engine_async(self):
        engine = create_engine("sqlite+aiosqlite://")
        assert isinstance(engine, AsyncEngine)

    def test_engine_tiene_url_sqlite(self):
        engine = create_engine("sqlite+aiosqlite:///./test.db")
        assert "test.db" in str(engine.url)


class TestSessionFactory:
    def test_crea_session_async(self):
        engine = create_engine("sqlite+aiosqlite://")
        factory = session_factory(engine)
        assert isinstance(factory, async_sessionmaker)


class TestGetSession:
    @pytest.mark.anyio
    async def test_genera_session(self):
        engine = create_engine("sqlite+aiosqlite://")
        factory = session_factory(engine)
        gen = get_session(factory)
        session = await anext(gen)
        assert isinstance(session, AsyncSession)
        await gen.aclose()


class TestInitDB:
    @pytest.mark.anyio
    async def test_init_db_no_explota(self):
        engine = create_engine("sqlite+aiosqlite://")
        await init_db(engine)
