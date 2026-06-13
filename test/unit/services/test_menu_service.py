"""Tests unitarios para MenuService."""

import asyncio
from unittest.mock import AsyncMock

from services.menu_service import MenuService


def test_listar_menu_delega_en_repositorio() -> None:
    """Verifica listado de platos desde repositorio inyectado."""
    repo = AsyncMock()
    repo.listar.return_value = [{"id": "1", "nombre": "Pizza"}]
    service = MenuService(repo)

    resultado = asyncio.run(service.listar())

    assert resultado == [{"id": "1", "nombre": "Pizza"}]
    repo.listar.assert_awaited_once_with()


def test_crear_plato_asigna_id_y_persiste() -> None:
    """Verifica creacion de plato conservando la regla len(menu) + 1."""
    repo = AsyncMock()
    repo.listar.return_value = [{"id": "1", "nombre": "Pizza"}]
    repo.guardar.return_value = {"id": "2", "nombre": "Pasta", "precio": 8.5}
    service = MenuService(repo)

    resultado = asyncio.run(service.crear({"nombre": "Pasta", "precio": 8.5}))

    assert resultado == {"id": "2", "nombre": "Pasta", "precio": 8.5}
    repo.guardar.assert_awaited_once_with(
        "2",
        {"id": "2", "nombre": "Pasta", "precio": 8.5},
    )


def test_actualizar_plato_reemplaza_datos() -> None:
    """Verifica actualizacion completa del plato."""
    repo = AsyncMock()
    repo.actualizar.return_value = {"id": "9", "nombre": "Sopa"}
    service = MenuService(repo)

    resultado = asyncio.run(service.actualizar("9", {"nombre": "Sopa"}))

    assert resultado == {"id": "9", "nombre": "Sopa"}
    repo.actualizar.assert_awaited_once_with("9", {"id": "9", "nombre": "Sopa"})


def test_eliminar_plato_devuelve_mensaje_actual() -> None:
    """Verifica mensaje publico de eliminacion."""
    repo = AsyncMock()
    repo.eliminar.return_value = {"id": "1", "nombre": "Pizza"}
    service = MenuService(repo)

    resultado = asyncio.run(service.eliminar("1"))

    assert resultado == {"mensaje": "Plato eliminado", "id": "1"}
    repo.eliminar.assert_awaited_once_with("1")
