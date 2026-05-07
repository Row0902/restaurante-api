"""Tests para la API de restaurante."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_raiz():
    """Verifica que el endpoint raíz responda correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"mensaje": "API corriendo 👋"}


def test_listar_menu_vacio():
    """Verifica que el menú vacío devuelva lista vacía."""
    response = client.get("/menu")
    assert response.status_code == 200
    assert response.json() == []
