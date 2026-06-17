# test/integration/test_ordenes.py
"""Tests de integración para los endpoints de órdenes."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_listar_ordenes_vacio(client: AsyncClient):
    """GET /ordenes/ devuelve una lista vacía si no hay órdenes."""
    response = await client.get("/ordenes/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_crear_orden_plato_inexistente(client: AsyncClient):
    """POST /ordenes/ falla con 404 al ordenar un plato que no existe."""
    orden_data = {"items": [{"plato_id": 9999, "cantidad": 1}]}
    response = await client.post("/ordenes/", json=orden_data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_flujo_completo_orden(client: AsyncClient):
    """POST /ordenes/ crea una orden, se obtiene por ID y se actualiza su estado."""
    # Crear platos
    response = await client.post(
        "/menu/", json={"nombre": "Milanesa", "precio": 1500.0}
    )
    plato1_id = response.json()["id"]
    response = await client.post("/menu/", json={"nombre": "Gaseosa", "precio": 500.0})
    plato2_id = response.json()["id"]

    # Crear orden
    orden_data = {
        "items": [
            {"plato_id": plato1_id, "cantidad": 1},
            {"plato_id": plato2_id, "cantidad": 2},
        ]
    }
    response = await client.post("/ordenes/", json=orden_data)
    assert response.status_code == 201
    orden = response.json()
    assert orden["total"] == 2500.0
    assert orden["estado"] == "pendiente"

    orden_id = orden["id"]

    # Obtener por ID
    response = await client.get(f"/ordenes/{orden_id}")
    assert response.status_code == 200
    assert response.json() == orden

    # Cambiar estado (válido)
    response = await client.put(
        f"/ordenes/{orden_id}/estado", json={"estado": "preparando"}
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "preparando"

    # Cambiar estado (inválido 422)
    response = await client.put(
        f"/ordenes/{orden_id}/estado", json={"estado": "invalido"}
    )
    assert response.status_code == 422
