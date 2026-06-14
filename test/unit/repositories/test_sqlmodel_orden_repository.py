"""Tests unitarios para SqlModelOrdenRepository."""

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession

from core.recurso_no_encontrado_error import RecursoNoEncontradoError
from repositories.database import (
    construir_engine,
    construir_session_maker,
    crear_tablas,
)
from repositories.sqlmodel_orden_repository import SqlModelOrdenRepository

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
    engine = construir_engine(sqlite_url(tmp_path / "ordenes.db"))
    await crear_tablas(engine)
    async with construir_session_maker(engine)() as session:
        yield session
    await engine.dispose()


async def test_guardar_y_listar_ordenes_sqlmodel(session: AsyncSession) -> None:
    """Verifica persistencia de ordenes con items."""
    repo = SqlModelOrdenRepository(session)

    await repo.guardar(
        "1",
        {
            "id": "1",
            "items": [{"plato_id": "1", "cantidad": 2}],
            "total": 20,
            "estado": "pendiente",
        },
    )

    assert isinstance(session.bind, AsyncEngine)
    assert await repo.listar() == [
        {
            "id": "1",
            "items": [{"plato_id": "1", "cantidad": 2}],
            "total": 20,
            "estado": "pendiente",
        },
    ]


async def test_actualizar_orden_sqlmodel_reemplaza_estado_e_items(
    session: AsyncSession,
) -> None:
    """Verifica actualizacion persistida de orden."""
    repo = SqlModelOrdenRepository(session)
    await repo.guardar(
        "1",
        {
            "id": "1",
            "items": [{"plato_id": "1", "cantidad": 1}],
            "total": 10,
            "estado": "pendiente",
        },
    )

    resultado = await repo.actualizar(
        "1",
        {
            "id": "1",
            "items": [{"plato_id": "2", "cantidad": 3}],
            "total": 30,
            "estado": "en_preparacion",
        },
    )

    assert resultado == {
        "id": "1",
        "items": [{"plato_id": "2", "cantidad": 3}],
        "total": 30,
        "estado": "en_preparacion",
    }


async def test_orden_sqlmodel_inexistente_propaga_error(
    session: AsyncSession,
) -> None:
    """Verifica error de dominio para orden inexistente."""
    repo = SqlModelOrdenRepository(session)

    with pytest.raises(RecursoNoEncontradoError, match="orden no encontrada"):
        await repo.obtener("404")
