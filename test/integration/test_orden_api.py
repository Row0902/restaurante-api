"""Tests de integración para las órdenes."""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_crear_orden_con_platos(client: AsyncClient):
    """Verifica que se cree una orden correctamente calculando el total."""
    # Primero creamos un plato
    plato_data = {"nombre": "Burger", "precio": 2500.0}
    response_plato = await client.post("/menu", json=plato_data)
    plato_id = response_plato.json()["id"]
    
    # Creamos la orden
    orden_data = {
        "items": [
            {"plato_id": plato_id, "cantidad": 2}
        ]
    }
    response_orden = await client.post("/ordenes", json=orden_data)
    assert response_orden.status_code == 201
    data = response_orden.json()
    assert data["estado"] == "pendiente"
    assert data["total"] == 5000.0
    assert len(data["items"]) == 1


@pytest.mark.anyio
async def test_crear_orden_plato_invalido(client: AsyncClient):
    """Verifica que falle crear una orden con platos que no existen."""
    orden_data = {
        "items": [
            {"plato_id": "no-existe", "cantidad": 1}
        ]
    }
    response = await client.post("/ordenes", json=orden_data)
    assert response.status_code == 400
    assert "no existe" in response.json()["detail"]
