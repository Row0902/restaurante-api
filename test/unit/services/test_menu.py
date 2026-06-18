"""Tests unitarios para MenuService con repositorio mockeado (R11)."""

from unittest.mock import AsyncMock

import pytest

from core.exceptions.not_found import MenuItemNotFoundError
from core.models.menu_item import MenuItem
from core.schemas.menu_item import CreatePlatoRequest, PlatoResponse
from services.menu import MenuService


@pytest.fixture
def repo():
    """Mock de AbstractMenuRepository."""
    return AsyncMock()


@pytest.fixture
def service(repo):
    """MenuService con repositorio mockeado."""
    return MenuService(repo)


class TestMenuServiceListar:
    @pytest.mark.anyio
    async def test_listar_vacio(self, service, repo):
        repo.get_all.return_value = []
        result = await service.listar()
        assert result == []
        repo.get_all.assert_awaited_once()

    @pytest.mark.anyio
    async def test_listar_con_platos(self, service, repo):
        pizza = MenuItem(id=1, nombre="Pizza", precio=12.5)
        repo.get_all.return_value = [pizza]
        result = await service.listar()
        assert len(result) == 1
        assert isinstance(result[0], PlatoResponse)
        assert result[0].nombre == "Pizza"


class TestMenuServiceObtenerPorId:
    @pytest.mark.anyio
    async def test_encontrado(self, service, repo):
        item = MenuItem(id=1, nombre="Pizza", precio=12.5)
        repo.get_by_id.return_value = item
        result = await service.obtener_por_id(1)
        assert result.id == 1
        assert result.nombre == "Pizza"
        repo.get_by_id.assert_awaited_once_with(1)

    @pytest.mark.anyio
    async def test_no_encontrado(self, service, repo):
        repo.get_by_id.side_effect = MenuItemNotFoundError(plato_id=999)
        with pytest.raises(MenuItemNotFoundError):
            await service.obtener_por_id(999)


class TestMenuServiceCrear:
    @pytest.mark.anyio
    async def test_crear_plato(self, service, repo):
        request = CreatePlatoRequest(nombre="Pizza", precio=12.5)
        repo.add.return_value = MenuItem(id=1, nombre="Pizza", precio=12.5)
        result = await service.crear(request)
        assert result.id == 1
        assert result.nombre == "Pizza"
        repo.add.assert_awaited_once()


class TestMenuServiceActualizar:
    @pytest.mark.anyio
    async def test_actualizar_existente(self, service, repo):
        existing = MenuItem(id=1, nombre="Pizza", precio=12.5)
        repo.get_by_id.return_value = existing
        repo.add.return_value = MenuItem(id=1, nombre="Pizza Grande", precio=15.0)

        request = CreatePlatoRequest(nombre="Pizza Grande", precio=15.0)
        result = await service.actualizar(1, request)

        assert result.nombre == "Pizza Grande"
        assert result.precio == 15.0
        repo.get_by_id.assert_awaited_once_with(1)
        repo.add.assert_awaited_once()

    @pytest.mark.anyio
    async def test_actualizar_inexistente(self, service, repo):
        repo.get_by_id.side_effect = MenuItemNotFoundError(plato_id=999)
        request = CreatePlatoRequest(nombre="X", precio=1.0)
        with pytest.raises(MenuItemNotFoundError):
            await service.actualizar(999, request)


class TestMenuServiceEliminar:
    @pytest.mark.anyio
    async def test_eliminar_existente(self, service, repo):
        repo.delete.return_value = None
        result = await service.eliminar(1)
        assert result == {"mensaje": "Plato eliminado", "id": 1}
        repo.delete.assert_awaited_once_with(1)

    @pytest.mark.anyio
    async def test_eliminar_inexistente(self, service, repo):
        repo.delete.side_effect = MenuItemNotFoundError(plato_id=999)
        with pytest.raises(MenuItemNotFoundError):
            await service.eliminar(999)
