"""Tests unitarios para OrdenService."""

from unittest.mock import AsyncMock

import pytest

from core.exceptions import PlatoNotFoundError
from core.models import Orden
from core.schemas import OrdenCreate, OrdenItemSchema
from services.orden_service import OrdenService


@pytest.mark.anyio
async def test_crear_orden_plato_inexistente():
    """Prueba crear orden con plato inexistente."""
    orden_repo_mock = AsyncMock()
    menu_repo_mock = AsyncMock()
    menu_repo_mock.get_by_id.return_value = None
    
    service = OrdenService(orden_repo_mock, menu_repo_mock)
    orden_in = OrdenCreate(items=[OrdenItemSchema(plato_id="invalido", cantidad=2)])
    
    with pytest.raises(PlatoNotFoundError):
        await service.crear(orden_in)


@pytest.mark.anyio
async def test_cambiar_estado():
    """Prueba el cambio de estado de una orden."""
    orden_repo_mock = AsyncMock()
    menu_repo_mock = AsyncMock()
    
    orden = Orden(id="1", estado="pendiente", total=10.0)
    orden_repo_mock.get_by_id_with_items.return_value = orden
    orden_repo_mock.update.return_value = orden
    
    service = OrdenService(orden_repo_mock, menu_repo_mock)
    
    resultado = await service.cambiar_estado("1", "entregado")
    assert resultado.estado == "entregado"
    orden_repo_mock.update.assert_called_once()
