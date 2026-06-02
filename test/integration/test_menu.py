# test/integration/test_menu.py
"""Tests de integración para los endpoints del menú."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_listar_menu_vacio(client: AsyncClient):
    """GET /menu/ devuelve una lista vacía si no hay platos."""
    response = await client.get("/menu/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_crear_y_obtener_plato(client: AsyncClient):
    """POST /menu/ crea un plato y GET /menu/{id} lo recupera."""
    plato_data = {
        "nombre": "Milanesa con Papas Fritas",
        "descripcion": "Milanesa de ternera con papas fritas bastón",
        "precio": 1500.0,
        "disponible": True,
    }
    response = await client.post("/menu/", json=plato_data)
    assert response.status_code == 201
    plato_creado = response.json()
    assert plato_creado["id"] is not None
    assert plato_creado["nombre"] == plato_data["nombre"]

    # Obtener por ID
    response = await client.get(f"/menu/{plato_creado['id']}")
    assert response.status_code == 200
    assert response.json() == plato_creado

    # Obtener no existente (404)
    response = await client.get("/menu/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_actualizar_y_eliminar_plato(client: AsyncClient):
    """PUT /menu/{id} actualiza un plato y DELETE /menu/{id} lo elimina."""
    # Crear plato
    plato_data = {"nombre": "Pizza", "precio": 1200.0}
    response = await client.post("/menu/", json=plato_data)
    plato_id = response.json()["id"]

    # Actualizar plato
    update_data = {"precio": 1400.0, "disponible": False}
    response = await client.put(f"/menu/{plato_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["precio"] == 1400.0
    assert response.json()["disponible"] is False

    # Eliminar
    response = await client.delete(f"/menu/{plato_id}")
    assert response.status_code == 204

    # Verificar borrado (404)
    response = await client.get(f"/menu/{plato_id}")
    assert response.status_code == 404
