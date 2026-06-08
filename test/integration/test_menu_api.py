from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_crear_plato():
    response = client.post(
        "/menu/",
        json={
            "nombre": "Pizza",
            "descripcion": "Muzzarella",
            "precio": 10000,
        },
    )

    assert response.status_code in [200, 201]


def test_listar_menu():
    response = client.get("/menu/")

    assert response.status_code == 200