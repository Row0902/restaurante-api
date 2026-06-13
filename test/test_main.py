"""Tests de caracterizacion para la API de restaurante."""

import pytest
from fastapi.testclient import TestClient

from main import app, menu, ordenes

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def limpiar_estado_en_memoria():
    """Aisla los diccionarios globales del monolito entre tests."""
    menu.clear()
    ordenes.clear()
    yield
    menu.clear()
    ordenes.clear()


def test_raiz():
    """Verifica que el endpoint raiz responda correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"mensaje": "API corriendo \U0001f44b"}


def test_listar_menu_vacio():
    """Verifica que el menu vacio devuelva lista vacia."""
    response = client.get("/menu")
    assert response.status_code == 200
    assert response.json() == []


def test_listar_ordenes_vacio():
    """Verifica que las ordenes vacias devuelvan lista vacia."""
    response = client.get("/ordenes")

    assert response.status_code == 200
    assert response.json() == []


def test_crear_dos_platos_asigna_ids_consecutivos_y_respeta_orden():
    """Caracteriza IDs consecutivos y orden de listado del menu."""
    primero = client.post("/menu", json={"nombre": "Pizza", "precio": 10.0})
    segundo = client.post("/menu", json={"nombre": "Pasta", "precio": 8.5})

    assert primero.status_code == 200
    assert primero.json() == {"id": "1", "nombre": "Pizza", "precio": 10.0}
    assert segundo.status_code == 200
    assert segundo.json() == {"id": "2", "nombre": "Pasta", "precio": 8.5}
    assert client.get("/menu").json() == [primero.json(), segundo.json()]


def test_crear_plato_despues_de_borrar_reutiliza_id_y_sobrescribe():
    """Caracteriza la fragilidad actual de calcular ID con len(menu) + 1."""
    client.post("/menu", json={"nombre": "Pizza", "precio": 10.0})
    client.post("/menu", json={"nombre": "Pasta", "precio": 8.5})
    client.delete("/menu/1")

    response = client.post("/menu", json={"nombre": "Sopa", "precio": 6.0})

    assert response.status_code == 200
    assert response.json() == {"id": "2", "nombre": "Sopa", "precio": 6.0}
    assert client.get("/menu").json() == [response.json()]


def test_crud_basico_de_menu():
    """Caracteriza creacion, lectura, actualizacion y borrado de platos."""
    plato = {"nombre": "Hamburguesa", "precio": 12.5, "categoria": "Fuerte"}

    creado = client.post("/menu", json=plato)
    assert creado.status_code == 200
    assert creado.json() == {"id": "1", **plato}

    listado = client.get("/menu")
    assert listado.status_code == 200
    assert listado.json() == [{"id": "1", **plato}]

    detalle = client.get("/menu/1")
    assert detalle.status_code == 200
    assert detalle.json() == {"id": "1", **plato}

    actualizado = client.put(
        "/menu/1",
        json={"nombre": "Hamburguesa doble", "precio": 15.0},
    )
    assert actualizado.status_code == 200
    assert actualizado.json() == {
        "id": "1",
        "nombre": "Hamburguesa doble",
        "precio": 15.0,
    }

    eliminado = client.delete("/menu/1")
    assert eliminado.status_code == 200
    assert eliminado.json() == {"mensaje": "Plato eliminado", "id": "1"}
    assert client.get("/menu").json() == []


def test_actualizacion_parcial_descarta_campos_previos():
    """Caracteriza que PUT reemplaza el plato en vez de mezclar campos."""
    client.post(
        "/menu",
        json={"nombre": "Hamburguesa", "precio": 12.5, "categoria": "Fuerte"},
    )

    response = client.put("/menu/1", json={"nombre": "Hamburguesa doble"})

    assert response.status_code == 200
    assert response.json() == {"id": "1", "nombre": "Hamburguesa doble"}
    assert client.get("/menu/1").json() == response.json()


def test_actualizar_plato_inexistente_crea_registro():
    """Caracteriza que PUT no valida existencia previa del plato."""
    response = client.put(
        "/menu/99",
        json={"nombre": "Sopa", "precio": 8.0},
    )

    assert response.status_code == 200
    assert response.json() == {"id": "99", "nombre": "Sopa", "precio": 8.0}
    assert client.get("/menu/99").json() == response.json()


def test_plato_inexistente_devuelve_error_500():
    """Caracteriza el error actual para lectura de plato inexistente."""
    response = client.get("/menu/404")

    assert response.status_code == 500
    assert response.text == "Internal Server Error"


def test_eliminar_plato_inexistente_devuelve_error_500():
    """Caracteriza el error actual al eliminar plato inexistente."""
    response = client.delete("/menu/404")

    assert response.status_code == 500
    assert response.text == "Internal Server Error"


def test_crear_orden_calcula_total_y_estado_pendiente():
    """Caracteriza calculo de total, estado inicial y consulta de ordenes."""
    client.post("/menu", json={"nombre": "Pizza", "precio": 10.0})
    client.post("/menu", json={"nombre": "Refresco", "precio": 3.5})

    response = client.post(
        "/ordenes",
        json={
            "items": [
                {"plato_id": "1", "cantidad": 2},
                {"plato_id": "2"},
            ],
        },
    )

    orden = response.json()
    assert response.status_code == 200
    assert orden == {
        "id": "1",
        "items": [{"plato_id": "1", "cantidad": 2}, {"plato_id": "2"}],
        "total": 23.5,
        "estado": "pendiente",
    }
    assert client.get("/ordenes").json() == [orden]
    assert client.get("/ordenes/1").json() == orden


def test_crear_orden_con_cantidad_cero_y_negativa_calcula_total_actual():
    """Caracteriza que cantidades cero y negativas se aceptan actualmente."""
    client.post("/menu", json={"nombre": "Pizza", "precio": 10.0})

    response = client.post(
        "/ordenes",
        json={
            "items": [
                {"plato_id": "1", "cantidad": 0},
                {"plato_id": "1", "cantidad": -2},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "items": [
            {"plato_id": "1", "cantidad": 0},
            {"plato_id": "1", "cantidad": -2},
        ],
        "total": -20.0,
        "estado": "pendiente",
    }


@pytest.mark.parametrize("cantidad", ["2", None])
def test_crear_orden_con_cantidad_no_numerica_devuelve_error_500(cantidad):
    """Caracteriza el error actual para cantidad string o None."""
    client.post("/menu", json={"nombre": "Pizza", "precio": 10.0})

    response = client.post(
        "/ordenes",
        json={"items": [{"plato_id": "1", "cantidad": cantidad}]},
    )

    assert response.status_code == 500
    assert response.text == "Internal Server Error"
    assert client.get("/ordenes").json() == []


@pytest.mark.parametrize("item", [{}, {"plato_id": None}])
def test_crear_orden_con_plato_id_omitido_o_none_devuelve_error_500(item):
    """Caracteriza el error actual cuando plato_id falta o es None."""
    client.post("/menu", json={"nombre": "Pizza", "precio": 10.0})

    response = client.post("/ordenes", json={"items": [item]})

    assert response.status_code == 500
    assert response.text == "Internal Server Error"
    assert client.get("/ordenes").json() == []


@pytest.mark.parametrize(
    "plato",
    [
        {"nombre": "Sin precio"},
        {"nombre": "Precio texto", "precio": "caro"},
    ],
)
def test_crear_orden_con_precio_faltante_o_no_numerico_devuelve_error_500(plato):
    """Caracteriza errores actuales al calcular total con precio invalido."""
    client.post("/menu", json=plato)

    response = client.post(
        "/ordenes",
        json={"items": [{"plato_id": "1", "cantidad": 2}]},
    )

    assert response.status_code == 500
    assert response.text == "Internal Server Error"
    assert client.get("/ordenes").json() == []


def test_crear_orden_sin_items_genera_total_cero():
    """Caracteriza que una orden sin items se acepta actualmente."""
    response = client.post("/ordenes", json={})

    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "items": [],
        "total": 0,
        "estado": "pendiente",
    }


def test_cambiar_estado_de_orden():
    """Caracteriza cambio de estado sin validacion de valores permitidos."""
    client.post("/ordenes", json={})

    response = client.put("/ordenes/1/estado", json={"estado": "entregado"})

    assert response.status_code == 200
    assert response.json()["estado"] == "entregado"


def test_cambiar_estado_de_orden_con_body_vacio_guarda_estado_none():
    """Caracteriza que body vacio cambia el estado a None."""
    client.post("/ordenes", json={})

    response = client.put("/ordenes/1/estado", json={})

    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "items": [],
        "total": 0,
        "estado": None,
    }
    assert client.get("/ordenes/1").json() == response.json()


def test_orden_con_plato_inexistente_devuelve_error_500():
    """Caracteriza el error actual cuando un item referencia plato inexistente."""
    response = client.post(
        "/ordenes",
        json={"items": [{"plato_id": "404", "cantidad": 1}]},
    )

    assert response.status_code == 500
    assert response.text == "Internal Server Error"


def test_orden_fallida_no_queda_persistida_parcialmente():
    """Caracteriza que una orden con error no aparece en el listado."""
    client.post("/menu", json={"nombre": "Pizza", "precio": 10.0})

    response = client.post(
        "/ordenes",
        json={
            "items": [
                {"plato_id": "1", "cantidad": 1},
                {"plato_id": "404", "cantidad": 1},
            ],
        },
    )

    assert response.status_code == 500
    assert response.text == "Internal Server Error"
    assert client.get("/ordenes").json() == []


def test_orden_inexistente_devuelve_error_500():
    """Caracteriza el error actual para lectura de orden inexistente."""
    response = client.get("/ordenes/404")

    assert response.status_code == 500
    assert response.text == "Internal Server Error"


def test_cambiar_estado_de_orden_inexistente_devuelve_error_500():
    """Caracteriza el error actual al cambiar una orden inexistente."""
    response = client.put("/ordenes/404/estado", json={"estado": "entregado"})

    assert response.status_code == 500
    assert response.text == "Internal Server Error"
