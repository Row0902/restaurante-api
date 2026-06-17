# test/unit/test_menu_service.py
"""Tests unitarios para MenuService."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.models import Plato
from core.schemas import PlatoCreate
from services.menu import MenuService


@pytest.fixture
def repo():
    return MagicMock()


@pytest.fixture
def service(repo):
    return MenuService(repo)


@pytest.mark.asyncio
async def test_listar_platos(service, repo):
    """listar() devuelve todos los platos del repositorio."""
    repo.get_all = AsyncMock(return_value=[Plato(id=1, nombre="Milanesa", precio=1500)])
    result = await service.listar()
    assert len(result) == 1
    assert result[0].nombre == "Milanesa"


@pytest.mark.asyncio
async def test_obtener_plato_existente(service, repo):
    """obtener() devuelve el plato cuando existe."""
    repo.get_by_id = AsyncMock(return_value=Plato(id=1, nombre="Milanesa", precio=1500))
    result = await service.obtener(1)
    assert result.id == 1


@pytest.mark.asyncio
async def test_obtener_plato_inexistente(service, repo):
    """obtener() lanza 404 cuando el plato no existe."""
    from fastapi import HTTPException

    repo.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc:
        await service.obtener(99)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_crear_plato(service, repo):
    """crear() llama al repositorio con los datos correctos."""
    data = PlatoCreate(nombre="Pizza", precio=1200)
    repo.add = AsyncMock(return_value=Plato(id=2, nombre="Pizza", precio=1200))
    result = await service.crear(data)
    repo.add.assert_called_once_with(data)
    assert result.nombre == "Pizza"


@pytest.mark.asyncio
async def test_eliminar_plato_inexistente(service, repo):
    """eliminar() lanza 404 cuando el plato no existe."""
    from fastapi import HTTPException

    repo.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc:
        await service.eliminar(99)
    assert exc.value.status_code == 404
