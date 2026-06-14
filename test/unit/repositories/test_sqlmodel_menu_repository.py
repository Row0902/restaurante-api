"""Tests unitarios para SqlModelMenuRepository."""

from collections.abc import AsyncIterator
from pathlib import Path
from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession

from core.recurso_no_encontrado_error import RecursoNoEncontradoError
from core.registro import Registro
from repositories.database import (
    construir_engine,
    construir_session_maker,
    crear_tablas,
)
from repositories.sqlmodel_menu_repository import SqlModelMenuRepository

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    """Fuerza backend asyncio para los tests async."""
    return "asyncio"


def sqlite_url(path: Path) -> str:
    """Construye URL SQLite async para un archivo temporal."""
    return f"sqlite+aiosqlite:///{path.as_posix()}"


@pytest.fixture
async def session(tmp_path: Path) -> AsyncIterator[AsyncSession]:
    """Entrega una sesion SQLModel async con SQLite temporal."""
    engine = construir_engine(sqlite_url(tmp_path / "menu.db"))
    await crear_tablas(engine)
    async with construir_session_maker(engine)() as session:
        yield session
    await engine.dispose()


async def test_guardar_y_listar_menu_sqlmodel(session: AsyncSession) -> None:
    """Verifica CRUD basico de platos en SQLite."""
    repo = SqlModelMenuRepository(session)

    await repo.guardar("1", {"id": "1", "nombre": "Pizza", "precio": 10})
    await repo.guardar("2", {"id": "2", "nombre": "Pasta", "precio": 12.5})

    assert isinstance(session.bind, AsyncEngine)
    assert await repo.listar() == [
        {"id": "1", "nombre": "Pizza", "precio": 10},
        {"id": "2", "nombre": "Pasta", "precio": 12.5},
    ]


async def test_menu_sqlmodel_preserva_extras(session: AsyncSession) -> None:
    """Verifica persistencia de campos extra permitidos por API."""
    plato: Registro = {
        "id": "1",
        "nombre": "Pizza",
        "precio": 10,
        "categoria": "Fuerte",
        "tags": ["horno"],
    }
    repo = SqlModelMenuRepository(session)

    guardado = await repo.guardar("1", plato)
    tags = cast(list[object], guardado["tags"])
    tags.append("externo")

    assert await repo.obtener("1") == plato


async def test_actualizar_menu_sqlmodel_reemplaza_registro(
    session: AsyncSession,
) -> None:
    """Verifica actualizacion persistida de plato."""
    repo = SqlModelMenuRepository(session)
    await repo.guardar("1", {"id": "1", "nombre": "Pizza", "precio": 10})

    resultado = await repo.actualizar(
        "1",
        {"id": "1", "nombre": "Sopa", "precio": 8, "categoria": "Entrada"},
    )

    assert resultado == {
        "id": "1",
        "nombre": "Sopa",
        "precio": 8,
        "categoria": "Entrada",
    }


async def test_menu_sqlmodel_inexistente_propaga_error(
    session: AsyncSession,
) -> None:
    """Verifica error de dominio para plato inexistente."""
    repo = SqlModelMenuRepository(session)

    with pytest.raises(RecursoNoEncontradoError, match="plato no encontrado"):
        await repo.obtener("404")
