"""Tests de integracion async para la capa API."""

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from api.dependencies import obtener_menu_service, obtener_orden_service
from main import app
from repositories.database import (
    construir_engine,
    construir_session_maker,
    crear_tablas,
)
from services.container import construir_menu_service, construir_orden_service
from services.menu_service import MenuService
from services.orden_service import OrdenService

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    """Fuerza backend asyncio para los tests async."""
    return "asyncio"


def sqlite_url(path: Path) -> str:
    """Construye URL SQLite async para un archivo temporal."""
    return f"sqlite+aiosqlite:///{path.as_posix()}"


@pytest.fixture
async def cliente(tmp_path: Path) -> AsyncIterator[AsyncClient]:
    """Cliente HTTP async contra la app ASGI."""
    engine = construir_engine(sqlite_url(tmp_path / "api.db"))
    session_maker = construir_session_maker(engine)
    await crear_tablas(engine)
    _configurar_overrides(session_maker)
    transporte = ASGITransport(app=app)
    async with AsyncClient(transport=transporte, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
    await engine.dispose()


def _configurar_overrides(
    session_maker: async_sessionmaker[AsyncSession],
) -> None:
    app.dependency_overrides[obtener_menu_service] = _menu_override(session_maker)
    app.dependency_overrides[obtener_orden_service] = _orden_override(session_maker)


def _menu_override(session_maker: async_sessionmaker[AsyncSession]):
    async def override() -> AsyncIterator[MenuService]:
        async with session_maker() as session:
            yield construir_menu_service(session)

    return override


def _orden_override(session_maker: async_sessionmaker[AsyncSession]):
    async def override() -> AsyncIterator[OrdenService]:
        async with session_maker() as session:
            yield construir_orden_service(session)

    return override


async def test_raiz(cliente: AsyncClient) -> None:
    """Verifica que el health check responda correctamente."""
    response = await cliente.get("/")

    assert response.status_code == 200
    assert response.json() == {"mensaje": "API corriendo \U0001f44b"}


async def test_crud_basico_de_menu(cliente: AsyncClient) -> None:
    """Verifica creacion, lectura, actualizacion y borrado de platos."""
    plato = {"nombre": "Hamburguesa", "precio": 12.5, "categoria": "Fuerte"}

    creado = await cliente.post("/menu", json=plato)
    listado = await cliente.get("/menu")
    detalle = await cliente.get("/menu/1")
    actualizado = await cliente.put("/menu/1", json={"nombre": "Sopa"})
    eliminado = await cliente.delete("/menu/1")

    assert creado.status_code == 200
    assert creado.json() == {"id": "1", **plato}
    assert listado.json() == [creado.json()]
    assert detalle.json() == creado.json()
    assert actualizado.json() == {
        "id": "1",
        "nombre": "Sopa",
        "precio": 12.5,
        "categoria": "Fuerte",
    }
    assert eliminado.json() == {"mensaje": "Plato eliminado", "id": "1"}


async def test_menu_persiste_entre_requests(cliente: AsyncClient) -> None:
    """Verifica que la API persiste menu en SQLite entre requests."""
    await cliente.post("/menu", json={"nombre": "Pizza", "precio": 10})

    listado = await cliente.get("/menu")

    assert listado.json() == [{"id": "1", "nombre": "Pizza", "precio": 10}]


async def test_plato_inexistente_devuelve_404(cliente: AsyncClient) -> None:
    """Verifica traduccion de recurso inexistente a 404."""
    lectura = await cliente.get("/menu/404")
    actualizacion = await cliente.put("/menu/404", json={"nombre": "Sopa"})
    eliminacion = await cliente.delete("/menu/404")

    assert lectura.status_code == 404
    assert actualizacion.status_code == 404
    assert eliminacion.status_code == 404
    assert lectura.json() == {"detail": "plato no encontrado"}


async def test_crear_plato_invalido_devuelve_422(cliente: AsyncClient) -> None:
    """Verifica validacion de payload en la frontera HTTP."""
    response = await cliente.post("/menu", json={"nombre": "Sin precio"})

    assert response.status_code == 422


async def test_crear_plato_con_precio_negativo_devuelve_400(
    cliente: AsyncClient,
) -> None:
    """Verifica traduccion de error de dominio a 400."""
    response = await cliente.post("/menu", json={"nombre": "Pizza", "precio": -1})

    assert response.status_code == 400
    assert response.json() == {"detail": "precio no puede ser negativo"}


async def test_crear_plato_con_nombre_vacio_devuelve_400(
    cliente: AsyncClient,
) -> None:
    """Verifica validacion de nombre desde el dominio."""
    response = await cliente.post("/menu", json={"nombre": "   ", "precio": 10})

    assert response.status_code == 400
    assert response.json() == {"detail": "nombre de plato requerido"}


async def test_crear_orden_calcula_total(cliente: AsyncClient) -> None:
    """Verifica creacion de orden con total calculado."""
    await cliente.post("/menu", json={"nombre": "Pizza", "precio": 10.0})
    await cliente.post("/menu", json={"nombre": "Refresco", "precio": 3.5})

    response = await cliente.post(
        "/ordenes",
        json={
            "items": [
                {"plato_id": "1", "cantidad": 2},
                {"plato_id": "2"},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "items": [{"plato_id": "1", "cantidad": 2}, {"plato_id": "2", "cantidad": 1}],
        "total": 23.5,
        "estado": "pendiente",
    }


async def test_orden_con_plato_inexistente_devuelve_404(
    cliente: AsyncClient,
) -> None:
    """Verifica traduccion de dominio a 404 al crear orden."""
    response = await cliente.post(
        "/ordenes",
        json={"items": [{"plato_id": "404", "cantidad": 1}]},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "plato no encontrado"}


async def test_orden_con_cantidad_invalida_devuelve_422(
    cliente: AsyncClient,
) -> None:
    """Verifica validacion de cantidad en schemas Pydantic."""
    response = await cliente.post(
        "/ordenes",
        json={"items": [{"plato_id": "1", "cantidad": 0}]},
    )

    assert response.status_code == 422


async def test_cambiar_estado_de_orden_con_transicion_valida(
    cliente: AsyncClient,
) -> None:
    """Verifica cambio de estado desde la capa HTTP."""
    creada = await cliente.post("/ordenes", json={})

    preparacion = await cliente.put(
        "/ordenes/1/estado",
        json={"estado": "en_preparacion"},
    )
    entregada = await cliente.put("/ordenes/1/estado", json={"estado": "entregada"})

    assert creada.status_code == 200
    assert preparacion.status_code == 200
    assert preparacion.json()["estado"] == "en_preparacion"
    assert entregada.status_code == 200
    assert entregada.json()["estado"] == "entregada"


async def test_cambiar_estado_rechaza_transicion_directa_a_entregada(
    cliente: AsyncClient,
) -> None:
    """Verifica que la API no salte estados del dominio."""
    creada = await cliente.post("/ordenes", json={})

    response = await cliente.put("/ordenes/1/estado", json={"estado": "entregada"})

    assert creada.status_code == 200
    assert response.status_code == 400
    assert response.json() == {"detail": "transicion de estado invalida"}


async def test_cambiar_estado_rechaza_estado_desconocido(
    cliente: AsyncClient,
) -> None:
    """Verifica rechazo de valores fuera del dominio."""
    creada = await cliente.post("/ordenes", json={})

    response = await cliente.put("/ordenes/1/estado", json={"estado": "fantasma"})

    assert creada.status_code == 200
    assert response.status_code == 400
    assert response.json() == {"detail": "estado de orden invalido"}


async def test_orden_inexistente_devuelve_404(cliente: AsyncClient) -> None:
    """Verifica traduccion de orden inexistente a 404."""
    response = await cliente.get("/ordenes/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "orden no encontrada"}
