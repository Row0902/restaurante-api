"""Tests unitarios para InMemoryOrdenRepository."""

import asyncio
from typing import cast

import pytest

from core.recurso_no_encontrado_error import RecursoNoEncontradoError
from repositories.in_memory_orden_repository import InMemoryOrdenRepository
from repositories.orden_repository import Registro


def test_listar_ordenes_devuelve_registros_guardados() -> None:
    """Verifica persistencia async de ordenes en memoria."""
    repo = InMemoryOrdenRepository()

    asyncio.run(repo.guardar("1", {"id": "1", "items": []}))
    asyncio.run(repo.guardar("2", {"id": "2", "items": [{"plato_id": "1"}]}))

    assert asyncio.run(repo.listar()) == [
        {"id": "1", "items": []},
        {"id": "2", "items": [{"plato_id": "1"}]},
    ]


def test_orden_repository_no_expone_referencias_internas() -> None:
    """Verifica que entradas y salidas no muten el almacenamiento."""
    orden: Registro = {
        "id": "1",
        "items": [{"plato_id": "1"}],
        "estado": "pendiente",
    }
    repo = InMemoryOrdenRepository()

    guardada = asyncio.run(repo.guardar("1", orden))
    orden["estado"] = "externo"
    items = cast(list[object], guardada["items"])
    items.append({"plato_id": "2"})

    assert asyncio.run(repo.obtener("1")) == {
        "id": "1",
        "items": [{"plato_id": "1"}],
        "estado": "pendiente",
    }


def test_actualizar_orden_reemplaza_registro() -> None:
    """Verifica reemplazo completo de la orden."""
    repo = InMemoryOrdenRepository({"1": {"id": "1", "estado": "pendiente"}})

    resultado = asyncio.run(repo.actualizar("1", {"id": "1", "estado": "lista"}))

    assert resultado == {"id": "1", "estado": "lista"}
    assert asyncio.run(repo.listar()) == [{"id": "1", "estado": "lista"}]


def test_obtener_orden_inexistente_propaga_error_de_dominio() -> None:
    """Verifica error de dominio para recurso inexistente."""
    repo = InMemoryOrdenRepository()

    with pytest.raises(RecursoNoEncontradoError, match="orden no encontrada"):
        asyncio.run(repo.obtener("404"))
