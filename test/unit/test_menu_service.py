"""Tests unitarios para MenuService."""

from unittest.mock import AsyncMock

import pytest

from core.exceptions import PlatoNotFoundError
from core.models import Plato
from core.schemas import PlatoCreate
from services.menu_service import MenuService


@pytest.mark.anyio
async def test_obtener_todos():
    """Prueba listar todos los platos del menú."""
    repo_mock = AsyncMock()
    repo_mock.get_all.return_value = [Plato(nombre="Pizza", precio=10.0)]
    service = MenuService(repo_mock)
    
    resultado = await service.obtener_todos()
    assert len(resultado) == 1
    assert resultado[0].nombre == "Pizza"


@pytest.mark.anyio
async def test_obtener_por_id_no_encontrado():
    """Prueba obtener un plato que no existe lanza error."""
    repo_mock = AsyncMock()
    repo_mock.get_by_id.return_value = None
    service = MenuService(repo_mock)
    
    with pytest.raises(PlatoNotFoundError):
        await service.obtener_por_id("invalido")


@pytest.mark.anyio
async def test_crear_plato():
    """Prueba crear un plato."""
    repo_mock = AsyncMock()
    plato_creado = Plato(id="1", nombre="Pasta", precio=15.0)
    repo_mock.add.return_value = plato_creado
    service = MenuService(repo_mock)
    
    plato_in = PlatoCreate(nombre="Pasta", precio=15.0)
    resultado = await service.crear(plato_in)
    
    assert resultado.id == "1"
    assert resultado.nombre == "Pasta"
    repo_mock.add.assert_called_once()
