"""Tests de caracterización — congelan el comportamiento actual del monolito.

CADA test documenta una conducta observable del monolito actual.
Estos tests son la red de seguridad: si después de una refactorización
siguen pasando, el comportamiento se preservó.

NOTA: El monolito usa estado global mutable (dicts `menu` y `ordenes`).
El fixture `reset_state()` limpia entre tests para evitar acoplamiento.
"""

import pytest
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_state():
    """Limpia los dicts globales entre tests — el monolito es stateful."""
    main.menu = {}
    main.ordenes = {}
    yield
    main.menu = {}
    main.ordenes = {}


# ---------------------------------------------------------------------------
# Raíz / Health Check
# ---------------------------------------------------------------------------


class TestRaiz:
    def test_health_check(self):
        """GET / → 200 con mensaje de bienvenida."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"mensaje": "API corriendo 👋"}


# ---------------------------------------------------------------------------
# Menú — GET /menu
# ---------------------------------------------------------------------------


class TestListarMenu:
    def test_listar_vacio(self):
        """GET /menu sin platos → lista vacía."""
        response = client.get("/menu")
        assert response.status_code == 200
        assert response.json() == []

    def test_listar_con_platos(self):
        """GET /menu con platos → lista con los platos."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        client.post("/menu", json={"nombre": "Ensalada", "precio": 8.0})

        response = client.get("/menu")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


# ---------------------------------------------------------------------------
# Menú — POST /menu
# ---------------------------------------------------------------------------


class TestCrearPlato:
    def test_crear_plato_basico(self):
        """POST /menu con nombre y precio → plato creado con ID string."""
        response = client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "1"
        assert data["nombre"] == "Pizza"
        assert data["precio"] == 12.5

    def test_crear_plato_con_campos_extra(self):
        """POST /menu acepta campos adicionales (categoría, descripción)."""
        response = client.post(
            "/menu",
            json={
                "nombre": "Pizza",
                "precio": 12.5,
                "categoria": "Principal",
                "descripcion": "Pizza margherita",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["categoria"] == "Principal"
        assert data["descripcion"] == "Pizza margherita"

    def test_crear_plato_ids_secuenciales(self):
        """POST /menu genera IDs secuenciales "1", "2", "3"."""
        r1 = client.post("/menu", json={"nombre": "A", "precio": 1})
        r2 = client.post("/menu", json={"nombre": "B", "precio": 2})
        r3 = client.post("/menu", json={"nombre": "C", "precio": 3})
        assert r1.json()["id"] == "1"
        assert r2.json()["id"] == "2"
        assert r3.json()["id"] == "3"


# ---------------------------------------------------------------------------
# Menú — GET /menu/{plato_id}
# ---------------------------------------------------------------------------


class TestObtenerPlato:
    def test_obtener_existente(self):
        """GET /menu/{id} → plato correspondiente."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        response = client.get("/menu/1")
        assert response.status_code == 200
        assert response.json()["nombre"] == "Pizza"

    def test_obtener_inexistente_lanza_keyerror(self):
        """GET /menu/{id} inexistente → KeyError (sin manejo de errores)."""
        with pytest.raises(KeyError):
            client.get("/menu/999")


# ---------------------------------------------------------------------------
# Menú — PUT /menu/{plato_id}
# ---------------------------------------------------------------------------


class TestActualizarPlato:
    def test_actualizar_existente(self):
        """PUT /menu/{id} → actualiza todos los campos."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        response = client.put(
            "/menu/1",
            json={"nombre": "Pizza Grande", "precio": 15.0, "categoria": "Especial"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Pizza Grande"
        assert data["precio"] == 15.0
        assert data["categoria"] == "Especial"

    def test_actualizar_parcial(self):
        """PUT /menu/{id} con datos parciales → solo esos campos."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        response = client.put("/menu/1", json={"precio": 99.0})
        assert response.status_code == 200
        # El PUT reemplaza TODO el plato con los nuevos datos
        data = response.json()
        assert data["precio"] == 99.0
        assert "nombre" not in data  # comportamiento actual: reemplaza, no mergea


# ---------------------------------------------------------------------------
# Menú — DELETE /menu/{plato_id}
# ---------------------------------------------------------------------------


class TestEliminarPlato:
    def test_eliminar_existente(self):
        """DELETE /menu/{id} → elimina y retorna confirmación."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        response = client.delete("/menu/1")
        assert response.status_code == 200
        assert response.json() == {"mensaje": "Plato eliminado", "id": "1"}

    def test_eliminar_inexistente_lanza_keyerror(self):
        """DELETE /menu/{id} inexistente → KeyError (sin manejo de errores)."""
        with pytest.raises(KeyError):
            client.delete("/menu/999")

    def test_eliminar_lo_remueve_de_lista(self):
        """DELETE /menu/{id} → el plato ya no aparece en GET /menu."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        client.post("/menu", json={"nombre": "Ensalada", "precio": 8.0})
        client.delete("/menu/1")
        response = client.get("/menu")
        assert len(response.json()) == 1
        assert response.json()[0]["nombre"] == "Ensalada"


# ---------------------------------------------------------------------------
# Órdenes — GET /ordenes
# ---------------------------------------------------------------------------


class TestListarOrdenes:
    def test_listar_vacio(self):
        """GET /ordenes sin órdenes → lista vacía."""
        response = client.get("/ordenes")
        assert response.status_code == 200
        assert response.json() == []

    def test_listar_con_ordenes(self):
        """GET /ordenes con órdenes → lista."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        client.post("/ordenes", json={"items": [{"plato_id": "1", "cantidad": 1}]})
        response = client.get("/ordenes")
        assert response.status_code == 200
        assert len(response.json()) == 1


# ---------------------------------------------------------------------------
# Órdenes — POST /ordenes
# ---------------------------------------------------------------------------


class TestCrearOrden:
    def test_crear_orden_con_total(self):
        """POST /ordenes → calcula total = plato.precio × cantidad."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        response = client.post(
            "/ordenes",
            json={"items": [{"plato_id": "1", "cantidad": 2}]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25.0
        assert data["estado"] == "pendiente"

    def test_crear_orden_con_varios_items(self):
        """POST /ordenes → suma precios de múltiples items."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        client.post("/menu", json={"nombre": "Ensalada", "precio": 8.0})
        response = client.post(
            "/ordenes",
            json={
                "items": [
                    {"plato_id": "1", "cantidad": 2},
                    {"plato_id": "2", "cantidad": 1},
                ]
            },
        )
        assert response.status_code == 200
        assert response.json()["total"] == 33.0  # 12.5*2 + 8.0*1

    def test_crear_orden_con_cantidad_default(self):
        """POST /ordenes sin cantidad → default 1."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 10.0})
        response = client.post(
            "/ordenes",
            json={"items": [{"plato_id": "1"}]},
        )
        assert response.status_code == 200
        assert response.json()["total"] == 10.0

    def test_crear_orden_con_plato_inexistente(self):
        """POST /ordenes con plato_id inválido → KeyError."""
        with pytest.raises(KeyError):
            client.post(
                "/ordenes",
                json={"items": [{"plato_id": "999", "cantidad": 1}]},
            )

    def test_crear_orden_ids_secuenciales(self):
        """POST /ordenes genera IDs "1", "2" secuenciales."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 10})
        r1 = client.post("/ordenes", json={"items": [{"plato_id": "1", "cantidad": 1}]})
        r2 = client.post("/ordenes", json={"items": [{"plato_id": "1", "cantidad": 1}]})
        assert r1.json()["id"] == "1"
        assert r2.json()["id"] == "2"


# ---------------------------------------------------------------------------
# Órdenes — GET /ordenes/{orden_id}
# ---------------------------------------------------------------------------


class TestObtenerOrden:
    def test_obtener_existente(self):
        """GET /ordenes/{id} → orden correspondiente."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        client.post("/ordenes", json={"items": [{"plato_id": "1", "cantidad": 1}]})
        response = client.get("/ordenes/1")
        assert response.status_code == 200
        assert response.json()["id"] == "1"

    def test_obtener_inexistente_lanza_keyerror(self):
        """GET /ordenes/{id} inexistente → KeyError."""
        with pytest.raises(KeyError):
            client.get("/ordenes/999")


# ---------------------------------------------------------------------------
# Órdenes — PUT /ordenes/{orden_id}/estado
# ---------------------------------------------------------------------------


class TestCambiarEstadoOrden:
    def test_cambiar_estado_valido(self):
        """PUT /ordenes/{id}/estado → actualiza estado."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        client.post("/ordenes", json={"items": [{"plato_id": "1", "cantidad": 1}]})
        response = client.put(
            "/ordenes/1/estado",
            json={"estado": "entregado"},
        )
        assert response.status_code == 200
        assert response.json()["estado"] == "entregado"

    def test_cambiar_estado_orden_inexistente(self):
        """PUT /ordenes/{id}/estado con orden inexistente → KeyError."""
        with pytest.raises(KeyError):
            client.put(
                "/ordenes/999/estado",
                json={"estado": "entregado"},
            )

    def test_cambiar_estado_sin_campo_estado_asigna_none(self):
        """PUT /ordenes/{id}/estado sin clave 'estado' → asigna None (bug actual)."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        client.post("/ordenes", json={"items": [{"plato_id": "1", "cantidad": 1}]})
        response = client.put(
            "/ordenes/1/estado",
            json={"otra_cosa": "x"},
        )
        assert response.status_code == 200
        assert response.json()["estado"] is None  # comportamiento actual
