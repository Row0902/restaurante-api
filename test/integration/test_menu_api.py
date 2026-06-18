"""Tests de integración para el menú."""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_listar_menu_vacio(client: AsyncClient):
    """Verifica que el menú vacío devuelva lista vacía."""
    response = await client.get("/menu")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_crear_y_obtener_plato(client: AsyncClient):
    """Verifica crear un plato y luego obtenerlo."""
    plato_data = {"nombre": "Milanesa", "precio": 4500.0}
    response = await client.post("/menu", json=plato_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Milanesa"
    assert data["precio"] == 4500.0
    assert "id" in data
    
    plato_id = data["id"]
    
    # Obtener el plato
    response_get = await client.get(f"/menu/{plato_id}")
    assert response_get.status_code == 200
    assert response_get.json()["id"] == plato_id


@pytest.mark.anyio
async def test_eliminar_plato(client: AsyncClient):
    """Verifica que se elimine correctamente un plato."""
    plato_data = {"nombre": "Pizza", "precio": 3000.0}
    response = await client.post("/menu", json=plato_data)
    plato_id = response.json()["id"]
    
    response_delete = await client.delete(f"/menu/{plato_id}")
    assert response_delete.status_code == 204
    
    response_get = await client.get(f"/menu/{plato_id}")
    assert response_get.status_code == 404
