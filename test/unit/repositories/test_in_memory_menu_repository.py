"""Tests unitarios para InMemoryMenuRepository."""

import asyncio
from typing import cast

import pytest

from repositories.in_memory_menu_repository import InMemoryMenuRepository
from repositories.menu_repository import Registro


def test_listar_menu_devuelve_registros_guardados() -> None:
    """Verifica persistencia async de platos en memoria."""
    repo = InMemoryMenuRepository()

    asyncio.run(repo.guardar("1", {"id": "1", "nombre": "Pizza"}))
    asyncio.run(repo.guardar("2", {"id": "2", "nombre": "Pasta"}))

    assert asyncio.run(repo.listar()) == [
        {"id": "1", "nombre": "Pizza"},
        {"id": "2", "nombre": "Pasta"},
    ]


def test_menu_repository_no_expone_referencias_internas() -> None:
    """Verifica que entradas y salidas no muten el almacenamiento."""
    plato: Registro = {"id": "1", "nombre": "Pizza", "tags": ["horno"]}
    repo = InMemoryMenuRepository()

    guardado = asyncio.run(repo.guardar("1", plato))
    plato["nombre"] = "Mutado"
    tags = cast(list[object], guardado["tags"])
    tags.append("externo")

    assert asyncio.run(repo.obtener("1")) == {
        "id": "1",
        "nombre": "Pizza",
        "tags": ["horno"],
    }


def test_actualizar_menu_reemplaza_registro() -> None:
    """Verifica reemplazo completo del plato."""
    repo = InMemoryMenuRepository({"1": {"id": "1", "nombre": "Pizza"}})

    resultado = asyncio.run(repo.actualizar("1", {"id": "1", "nombre": "Sopa"}))

    assert resultado == {"id": "1", "nombre": "Sopa"}
    assert asyncio.run(repo.listar()) == [{"id": "1", "nombre": "Sopa"}]


def test_eliminar_plato_inexistente_propaga_key_error() -> None:
    """Verifica compatibilidad con el error actual de API."""
    repo = InMemoryMenuRepository()

    with pytest.raises(KeyError):
        asyncio.run(repo.eliminar("404"))
