"""Tests de integración — validan la app refactorizada contra especificaciones.

Usa SQLite en memoria mediante ``app.dependency_overrides``,
sin contaminar el estado global de otros módulos de test.
"""

from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from api.deps import get_db
from core.database import create_engine, init_db, session_factory
from main import app

# ---------------------------------------------------------------------------
# Motor de test — siempre en memoria, aislado del motor de producción
# ---------------------------------------------------------------------------

_test_engine = create_engine("sqlite+aiosqlite://")
_TestSessionFactory = session_factory(_test_engine)


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield una sesión de la base de datos en memoria."""
    async with _TestSessionFactory() as session:
        yield session


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session", autouse=True)
def _setup_test_db() -> Generator[None]:
    """Crea tablas una vez al iniciar la sesión de tests."""
    import asyncio

    asyncio.run(init_db(_test_engine))
    yield
    import asyncio

    asyncio.run(_test_engine.dispose())


@pytest.fixture(autouse=True)
def _override_deps() -> Generator[None]:
    """Sobrescribe ``get_db`` para usar la base en memoria en cada test.

    La dependencia original (``api.deps.get_db``) se restaura automáticamente
    al terminar cada test, evitando fugas entre tests.
    """
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clean_db() -> Generator[None]:
    """Limpia todas las tablas entre tests — evita acoplamiento."""
    import asyncio

    asyncio.run(_clean_tables())
    yield
    asyncio.run(_clean_tables())


async def _clean_tables() -> None:
    """Elimina datos de todas las tablas en orden inverso (FK safe).

    Usa comillas dobles en el nombre de la tabla para evitar conflictos
    con palabras reservadas de SQLite (``order``).
    """
    async with _test_engine.begin() as conn:
        for table in reversed(SQLModel.metadata.sorted_tables):
            await conn.execute(text(f'DELETE FROM "{table.name}"'))


@pytest.fixture
def client() -> Generator[TestClient]:
    """Provee un TestClient para la app refactorizada."""
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _crear_plato_base(client: TestClient) -> dict:
    """Crea un plato base 'Pizza' y retorna su JSON."""
    return client.post(
        "/menu",
        json={"nombre": "Pizza", "precio": 12.5},
    ).json()


# ---------------------------------------------------------------------------
# Raíz / Health Check
# ---------------------------------------------------------------------------


class TestRaiz:
    def test_health_check(self, client: TestClient) -> None:
        """GET / → 200 con mensaje de bienvenida."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"mensaje": "API corriendo 👋"}


# ---------------------------------------------------------------------------
# Menú — GET /menu
# ---------------------------------------------------------------------------


class TestListarMenu:
    def test_listar_vacio(self, client: TestClient) -> None:
        """GET /menu sin platos → lista vacía."""
        response = client.get("/menu")
        assert response.status_code == 200
        assert response.json() == []

    def test_listar_con_platos(self, client: TestClient) -> None:
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
    def test_crear_plato_basico(self, client: TestClient) -> None:
        """POST /menu con nombre y precio → plato creado con ID entero."""
        response = client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1  # int, no string — mejora deliberada
        assert data["nombre"] == "Pizza"
        assert data["precio"] == 12.5

    def test_crear_plato_con_categoria_y_descripcion(
        self, client: TestClient
    ) -> None:
        """POST /menu acepta categoría y descripción."""
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

    def test_crear_plato_ids_secuenciales(self, client: TestClient) -> None:
        """POST /menu genera IDs secuenciales 1, 2, 3."""
        r1 = client.post("/menu", json={"nombre": "A", "precio": 1})
        r2 = client.post("/menu", json={"nombre": "B", "precio": 2})
        r3 = client.post("/menu", json={"nombre": "C", "precio": 3})
        assert r1.json()["id"] == 1
        assert r2.json()["id"] == 2
        assert r3.json()["id"] == 3


# ---------------------------------------------------------------------------
# Menú — GET /menu/{plato_id}
# ---------------------------------------------------------------------------


class TestObtenerPlato:
    def test_obtener_existente(self, client: TestClient) -> None:
        """GET /menu/{id} → plato correspondiente."""
        _crear_plato_base(client)
        response = client.get("/menu/1")
        assert response.status_code == 200
        assert response.json()["nombre"] == "Pizza"

    def test_obtener_inexistente_devuelve_404(self, client: TestClient) -> None:
        """GET /menu/{id} inexistente → 404 (antes KeyError → 500)."""
        response = client.get("/menu/999")
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Menú — PUT /menu/{plato_id}
# ---------------------------------------------------------------------------


class TestActualizarPlato:
    def test_actualizar_existente(self, client: TestClient) -> None:
        """PUT /menu/{id} → actualiza todos los campos."""
        _crear_plato_base(client)
        response = client.put(
            "/menu/1",
            json={
                "nombre": "Pizza Grande",
                "precio": 15.0,
                "categoria": "Especial",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Pizza Grande"
        assert data["precio"] == 15.0
        assert data["categoria"] == "Especial"

    def test_actualizar_parcial_devuelve_422(self, client: TestClient) -> None:
        """PUT /menu/{id} con datos parciales → 422.

        Mejora deliberada: el monolito original sobrescribía con campos
        incompletos. Ahora CreatePlatoRequest exige nombre y precio.
        """
        _crear_plato_base(client)
        response = client.put("/menu/1", json={"precio": 99.0})
        assert response.status_code == 422  # falta 'nombre'


# ---------------------------------------------------------------------------
# Menú — DELETE /menu/{plato_id}
# ---------------------------------------------------------------------------


class TestEliminarPlato:
    def test_eliminar_existente(self, client: TestClient) -> None:
        """DELETE /menu/{id} → elimina y retorna confirmación."""
        _crear_plato_base(client)
        response = client.delete("/menu/1")
        assert response.status_code == 200
        assert response.json() == {"mensaje": "Plato eliminado", "id": 1}

    def test_eliminar_inexistente_devuelve_404(self, client: TestClient) -> None:
        """DELETE /menu/{id} inexistente → 404."""
        response = client.delete("/menu/999")
        assert response.status_code == 404

    def test_eliminar_lo_remueve_de_lista(self, client: TestClient) -> None:
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
    def test_listar_vacio(self, client: TestClient) -> None:
        """GET /ordenes sin órdenes → lista vacía."""
        response = client.get("/ordenes")
        assert response.status_code == 200
        assert response.json() == []

    def test_listar_con_ordenes(self, client: TestClient) -> None:
        """GET /ordenes con órdenes → lista."""
        _crear_plato_base(client)
        client.post("/ordenes", json={"items": [{"plato_id": 1, "cantidad": 1}]})
        response = client.get("/ordenes")
        assert response.status_code == 200
        assert len(response.json()) == 1


# ---------------------------------------------------------------------------
# Órdenes — POST /ordenes
# ---------------------------------------------------------------------------


class TestCrearOrden:
    def test_crear_orden_con_total(self, client: TestClient) -> None:
        """POST /ordenes → calcula total = plato.precio × cantidad."""
        _crear_plato_base(client)
        response = client.post(
            "/ordenes",
            json={"items": [{"plato_id": 1, "cantidad": 2}]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25.0
        assert data["estado"] == "pendiente"

    def test_crear_orden_con_varios_items(self, client: TestClient) -> None:
        """POST /ordenes → suma precios de múltiples items."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 12.5})
        client.post("/menu", json={"nombre": "Ensalada", "precio": 8.0})
        response = client.post(
            "/ordenes",
            json={
                "items": [
                    {"plato_id": 1, "cantidad": 2},
                    {"plato_id": 2, "cantidad": 1},
                ]
            },
        )
        assert response.status_code == 200
        assert response.json()["total"] == 33.0  # 12.5*2 + 8.0*1

    def test_crear_orden_sin_cantidad_default_1(self, client: TestClient) -> None:
        """POST /ordenes sin cantidad → default 1."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 10.0})
        response = client.post(
            "/ordenes",
            json={"items": [{"plato_id": 1}]},  # sin cantidad explícita
        )
        assert response.status_code == 200
        assert response.json()["total"] == 10.0

    def test_crear_orden_con_plato_inexistente_404(
        self, client: TestClient
    ) -> None:
        """POST /ordenes con plato_id inválido → 404."""
        response = client.post(
            "/ordenes",
            json={"items": [{"plato_id": 999, "cantidad": 1}]},
        )
        assert response.status_code == 404

    def test_crear_orden_ids_secuenciales(self, client: TestClient) -> None:
        """POST /ordenes genera IDs 1, 2 secuenciales."""
        client.post("/menu", json={"nombre": "Pizza", "precio": 10.0})
        r1 = client.post(
            "/ordenes", json={"items": [{"plato_id": 1, "cantidad": 1}]}
        )
        r2 = client.post(
            "/ordenes", json={"items": [{"plato_id": 1, "cantidad": 1}]}
        )
        assert r1.json()["id"] == 1
        assert r2.json()["id"] == 2


# ---------------------------------------------------------------------------
# Órdenes — GET /ordenes/{orden_id}
# ---------------------------------------------------------------------------


class TestObtenerOrden:
    def test_obtener_existente(self, client: TestClient) -> None:
        """GET /ordenes/{id} → orden correspondiente."""
        _crear_plato_base(client)
        client.post("/ordenes", json={"items": [{"plato_id": 1, "cantidad": 1}]})
        response = client.get("/ordenes/1")
        assert response.status_code == 200
        assert response.json()["id"] == 1

    def test_obtener_inexistente_devuelve_404(self, client: TestClient) -> None:
        """GET /ordenes/{id} inexistente → 404."""
        response = client.get("/ordenes/999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Órdenes — PUT /ordenes/{orden_id}/estado
# ---------------------------------------------------------------------------


class TestCambiarEstadoOrden:
    def test_cambiar_estado_valido(self, client: TestClient) -> None:
        """PUT /ordenes/{id}/estado → actualiza estado.

        Transición válida: pendiente → preparando (R1).
        """
        _crear_plato_base(client)
        client.post("/ordenes", json={"items": [{"plato_id": 1, "cantidad": 1}]})
        response = client.put(
            "/ordenes/1/estado",
            json={"estado": "preparando"},
        )
        assert response.status_code == 200
        assert response.json()["estado"] == "preparando"

    def test_cambiar_estado_orden_inexistente_404(
        self, client: TestClient
    ) -> None:
        """PUT /ordenes/{id}/estado con orden inexistente → 404."""
        response = client.put(
            "/ordenes/999/estado",
            json={"estado": "entregado"},
        )
        assert response.status_code == 404

    def test_cambiar_estado_sin_campo_estado_422(
        self, client: TestClient
    ) -> None:
        """PUT /ordenes/{id}/estado sin clave 'estado' → 422.

        Mejora deliberada: el monolito original asignaba None silenciosamente
        (bug documentado). Ahora EstadoUpdateRequest exige el campo.
        """
        _crear_plato_base(client)
        client.post("/ordenes", json={"items": [{"plato_id": 1, "cantidad": 1}]})
        response = client.put(
            "/ordenes/1/estado",
            json={"otra_cosa": "x"},
        )
        assert response.status_code == 422
