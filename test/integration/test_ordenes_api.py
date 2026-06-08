from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_crear_orden():
    response = client.post(
        "/ordenes/",
        json={
            "items": [
                {
                    "plato_id": 1,
                    "cantidad": 1,
                }
            ]
        },
    )

    assert response.status_code in [200, 201]


def test_obtener_orden():
    response = client.get("/ordenes/1")

    assert response.status_code == 200


def test_actualizar_estado():
    response = client.put(
        "/ordenes/1/estado",
        json={
            "estado": "entregado"
        },
    )

    assert response.status_code == 200