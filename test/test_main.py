"""Tests para la API de restaurante."""

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from api.deps import get_menu_service
from main import app

client = TestClient(app)


def test_raiz():
    """Verifica que el endpoint raíz responda correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"mensaje": "API corriendo 👋"}


def test_listar_menu_vacio():
    """Verifica que el menú vacío devuelva lista vacía."""
    mock = AsyncMock()
    mock.list_all.return_value = []
    app.dependency_overrides[get_menu_service] = lambda: mock

    response = client.get("/menu")

    assert response.status_code == 200
    assert response.json() == []
    app.dependency_overrides.clear()
