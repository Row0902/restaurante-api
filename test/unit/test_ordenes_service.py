# test/unit/test_ordenes_service.py
"""Tests unitarios para OrdenesService."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from core.models import Orden, Plato
from core.schemas import OrdenCreate, OrdenEstadoUpdate, OrdenItemCreate
from services.ordenes import OrdenesService


@pytest.fixture
def repo():
    """Proporciona un mock para el repositorio de órdenes."""
    return MagicMock()


@pytest.fixture
def menu_repo():
    """Proporciona un mock para el repositorio de menú."""
    return MagicMock()


@pytest.fixture
def service(repo, menu_repo):
    """Proporciona una instancia de OrdenesService con mocks inyectados."""
    return OrdenesService(repo, menu_repo)


@pytest.mark.asyncio
async def test_listar_ordenes(service, repo):
    """listar() devuelve todas las órdenes del repositorio."""
    repo.get_all = AsyncMock(
        return_value=[Orden(id=1, total=1500.0, estado="pendiente")]
    )
    result = await service.listar()
    assert len(result) == 1
    assert result[0].total == 1500.0
    assert result[0].estado == "pendiente"


@pytest.mark.asyncio
async def test_obtener_orden_existente(service, repo):
    """obtener() devuelve la orden cuando existe."""
    repo.get_by_id = AsyncMock(
        return_value=Orden(id=1, total=1500.0, estado="pendiente")
    )
    result = await service.obtener(1)
    assert result.id == 1
    assert result.total == 1500.0


@pytest.mark.asyncio
async def test_obtener_orden_inexistente(service, repo):
    """obtener() lanza 404 cuando la orden no existe."""
    repo.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc:
        await service.obtener(99)
    assert exc.value.status_code == 404
    assert "Orden 99 no encontrada" in exc.value.detail


@pytest.mark.asyncio
async def test_crear_orden_exitosa(service, repo, menu_repo):
    """crear() calcula el total llamando al menú y agrega la orden."""
    # Simular platos en el menú
    plato1 = Plato(id=1, nombre="Milanesa", precio=1500.0)
    plato2 = Plato(id=2, nombre="Gaseosa", precio=500.0)

    # get_by_ids del menú devuelve los platos simulados
    async def mock_get_by_ids(plato_ids):
        res = []
        if 1 in plato_ids:
            res.append(plato1)
        if 2 in plato_ids:
            res.append(plato2)
        return res

    menu_repo.get_by_ids = AsyncMock(side_effect=mock_get_by_ids)

    # Datos para crear la orden: 1 Milanesa (1500) y 2 Gaseosas (1000). Total = 2500.
    items_create = [
        OrdenItemCreate(plato_id=1, cantidad=1),
        OrdenItemCreate(plato_id=2, cantidad=2),
    ]
    data = OrdenCreate(items=items_create)

    # Mock de agregar en repositorio
    expected_orden = Orden(id=1, total=2500.0, estado="pendiente")
    repo.add = AsyncMock(return_value=expected_orden)

    result = await service.crear(data)

    # Verificar que el total se calculó correctamente (1500*1 + 500*2 = 2500)
    # y que se llamó a repo.add con la orden adecuada e ítems construidos
    assert repo.add.call_count == 1
    called_orden = repo.add.call_args[0][0]
    called_items = repo.add.call_args[0][1]

    assert called_orden.total == 2500.0
    assert len(called_items) == 2
    assert called_items[0].plato_id == 1
    assert called_items[0].cantidad == 1
    assert called_items[1].plato_id == 2
    assert called_items[1].cantidad == 2

    assert result.total == 2500.0
    assert result.estado == "pendiente"


@pytest.mark.asyncio
async def test_crear_orden_plato_inexistente(service, menu_repo):
    """crear() lanza 404 si algún plato de la orden no existe."""
    menu_repo.get_by_ids = AsyncMock(return_value=[])
    data = OrdenCreate(items=[OrdenItemCreate(plato_id=99, cantidad=1)])

    with pytest.raises(HTTPException) as exc:
        await service.crear(data)
    assert exc.value.status_code == 404
    assert "Plato 99 no encontrado" in exc.value.detail


@pytest.mark.asyncio
async def test_cambiar_estado_valido(service, repo):
    """cambiar_estado() actualiza el estado si es válido."""
    orden_existente = Orden(id=1, total=1500.0, estado="pendiente")
    repo.get_by_id = AsyncMock(return_value=orden_existente)

    expected_orden = Orden(id=1, total=1500.0, estado="preparando")
    repo.update_estado = AsyncMock(return_value=expected_orden)

    data = OrdenEstadoUpdate(estado="preparando")
    result = await service.cambiar_estado(1, data)

    repo.update_estado.assert_called_once_with(orden_existente, "preparando")
    assert result.estado == "preparando"


@pytest.mark.asyncio
async def test_cambiar_estado_invalido(service, repo):
    """cambiar_estado() lanza 422 si el estado no es válido."""
    data = OrdenEstadoUpdate(estado="entregado_y_comido")
    with pytest.raises(HTTPException) as exc:
        await service.cambiar_estado(1, data)
    assert exc.value.status_code == 422
    assert "Estado inválido" in exc.value.detail
