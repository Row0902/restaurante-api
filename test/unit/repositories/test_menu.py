"""Tests unitarios para MenuRepository con SQLite en memoria."""

import pytest
from sqlmodel import SQLModel

from core.database import create_engine, session_factory
from core.exceptions.not_found import MenuItemNotFoundError
from core.models.menu_item import MenuItem
from repositories.menu import MenuRepository


@pytest.fixture
async def repo():
    """Provee un MenuRepository con SQLite en memoria y tablas creadas."""
    engine = create_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    factory = session_factory(engine)
    async with factory() as session:
        yield MenuRepository(session)


class TestMenuRepositoryAdd:
    @pytest.mark.anyio
    async def test_add_crea_y_retorna_con_id(self, repo):
        item = MenuItem(nombre="Pizza", precio=12.5)
        created = await repo.add(item)
        assert created.id == 1
        assert created.nombre == "Pizza"
        assert created.precio == 12.5

    @pytest.mark.anyio
    async def test_add_multiples_ids_auto_increment(self, repo):
        a = await repo.add(MenuItem(nombre="A", precio=1.0))
        b = await repo.add(MenuItem(nombre="B", precio=2.0))
        assert a.id == 1
        assert b.id == 2


class TestMenuRepositoryGetAll:
    @pytest.mark.anyio
    async def test_vacio_devuelve_lista_vacia(self, repo):
        result = await repo.get_all()
        assert result == []

    @pytest.mark.anyio
    async def test_con_datos_devuelve_todos(self, repo):
        await repo.add(MenuItem(nombre="A", precio=1.0))
        await repo.add(MenuItem(nombre="B", precio=2.0))
        result = await repo.get_all()
        assert len(result) == 2


class TestMenuRepositoryGetById:
    @pytest.mark.anyio
    async def test_encontrado_retorna_plato(self, repo):
        await repo.add(MenuItem(nombre="Pizza", precio=12.5))
        result = await repo.get_by_id(1)
        assert result.nombre == "Pizza"

    @pytest.mark.anyio
    async def test_no_encontrado_lanza_excepcion(self, repo):
        with pytest.raises(MenuItemNotFoundError):
            await repo.get_by_id(999)


class TestMenuRepositoryDelete:
    @pytest.mark.anyio
    async def test_elimina_y_verifica_que_no_existe(self, repo):
        await repo.add(MenuItem(nombre="Pizza", precio=12.5))
        await repo.delete(1)
        with pytest.raises(MenuItemNotFoundError):
            await repo.get_by_id(1)

    @pytest.mark.anyio
    async def test_eliminar_inexistente_lanza_excepcion(self, repo):
        with pytest.raises(MenuItemNotFoundError):
            await repo.delete(999)
