"""Tests unitarios para OrdenService."""

import asyncio
from unittest.mock import AsyncMock

import pytest

from core.dominio_error import DominioError
from core.recurso_no_encontrado_error import RecursoNoEncontradoError
from services.orden_service import OrdenService


def test_listar_ordenes_delega_en_repositorio() -> None:
    """Verifica listado de ordenes desde repositorio inyectado."""
    orden_repo = AsyncMock()
    menu_repo = AsyncMock()
    orden_repo.listar.return_value = [{"id": "1", "items": []}]
    service = OrdenService(orden_repo, menu_repo)

    resultado = asyncio.run(service.listar())

    assert resultado == [{"id": "1", "items": []}]
    orden_repo.listar.assert_awaited_once_with()


def test_crear_orden_calcula_total_y_persiste() -> None:
    """Verifica calculo de total usando el repositorio de menu."""
    orden_repo = AsyncMock()
    menu_repo = AsyncMock()
    orden_repo.listar.return_value = []
    orden_repo.guardar.return_value = {
        "id": "1",
        "items": [{"plato_id": "1", "cantidad": 2}, {"plato_id": "2"}],
        "total": 23.5,
        "estado": "pendiente",
    }
    menu_repo.obtener.side_effect = [
        {"id": "1", "precio": 10.0},
        {"id": "2", "precio": 3.5},
    ]
    service = OrdenService(orden_repo, menu_repo)

    resultado = asyncio.run(
        service.crear(
            {"items": [{"plato_id": "1", "cantidad": 2}, {"plato_id": "2"}]},
        ),
    )

    assert resultado["total"] == 23.5
    orden_repo.guardar.assert_awaited_once_with("1", resultado)


def test_crear_orden_fallida_no_persiste() -> None:
    """Verifica que una orden con error no se guarde parcialmente."""
    orden_repo = AsyncMock()
    menu_repo = AsyncMock()
    orden_repo.listar.return_value = []
    menu_repo.obtener.side_effect = [
        {"id": "1", "precio": 10.0},
        RecursoNoEncontradoError("plato no encontrado"),
    ]
    service = OrdenService(orden_repo, menu_repo)

    with pytest.raises(RecursoNoEncontradoError, match="plato no encontrado"):
        asyncio.run(
            service.crear(
                {
                    "items": [
                        {"plato_id": "1", "cantidad": 1},
                        {"plato_id": "404", "cantidad": 1},
                    ],
                },
            ),
        )

    orden_repo.guardar.assert_not_awaited()


def test_cambiar_estado_valida_transicion_y_persiste() -> None:
    """Verifica cambio de estado usando reglas de dominio."""
    orden_repo = AsyncMock()
    menu_repo = AsyncMock()
    orden_repo.obtener.return_value = {
        "id": "1",
        "items": [],
        "total": 0,
        "estado": "pendiente",
    }
    orden_repo.actualizar.return_value = {
        "id": "1",
        "items": [],
        "total": 0,
        "estado": "en_preparacion",
    }
    service = OrdenService(orden_repo, menu_repo)

    resultado = asyncio.run(service.cambiar_estado("1", {"estado": "en_preparacion"}))

    assert resultado == {
        "id": "1",
        "items": [],
        "total": 0,
        "estado": "en_preparacion",
    }
    orden_repo.actualizar.assert_awaited_once_with(
        "1",
        {"id": "1", "items": [], "total": 0, "estado": "en_preparacion"},
    )


def test_cambiar_estado_rechaza_transicion_invalida() -> None:
    """Verifica que no se salte la preparacion."""
    orden_repo = AsyncMock()
    menu_repo = AsyncMock()
    orden_repo.obtener.return_value = {
        "id": "1",
        "items": [],
        "total": 0,
        "estado": "pendiente",
    }
    service = OrdenService(orden_repo, menu_repo)

    with pytest.raises(DominioError, match="transicion de estado invalida"):
        asyncio.run(service.cambiar_estado("1", {"estado": "entregada"}))

    orden_repo.actualizar.assert_not_awaited()


def test_cambiar_estado_rechaza_estado_desconocido() -> None:
    """Verifica rechazo de estados fuera del dominio."""
    orden_repo = AsyncMock()
    menu_repo = AsyncMock()
    orden_repo.obtener.return_value = {
        "id": "1",
        "items": [],
        "total": 0,
        "estado": "pendiente",
    }
    service = OrdenService(orden_repo, menu_repo)

    with pytest.raises(DominioError, match="estado de orden invalido"):
        asyncio.run(service.cambiar_estado("1", {"estado": "fantasma"}))

    orden_repo.actualizar.assert_not_awaited()
