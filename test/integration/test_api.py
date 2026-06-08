"""Tests de integración: endpoints reales con SQLite en memoria."""

import unittest

from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from main import app
from repositories.database import get_session

TEST_DATABASE_URL = "sqlite+aiosqlite://"


class TestMenuAPI(unittest.IsolatedAsyncioTestCase):
    """Prueba los endpoints del menú con base de datos en memoria."""

    async def asyncSetUp(self) -> None:
        """Crea tablas, sobreescribe dependencia, prepara cliente HTTP."""
        self.engine = create_async_engine(TEST_DATABASE_URL, echo=False)
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        test_session_local = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

        async def override_get_session():
            async with test_session_local() as session:
                yield session

        app.dependency_overrides[get_session] = override_get_session

        self.client = AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        )

    async def asyncTearDown(self) -> None:
        """Limpia overrides, dropea tablas, cierra engine."""
        await self.client.aclose()
        app.dependency_overrides.clear()
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        await self.engine.dispose()

    async def _crear_plato(
        self,
        nombre: str,
        precio: float,
        categoria: str,
        descripcion: str | None = None,
    ) -> Response:
        body: dict = {
            "nombre": nombre,
            "precio": precio,
            "categoria": categoria,
        }
        if descripcion is not None:
            body["descripcion"] = descripcion
        return await self.client.post("/menu", json=body)

    async def test_crear_y_listar_menu(self) -> None:
        """Crea un plato y lo lista."""
        r = await self.client.get("/menu")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), [])

        r = await self._crear_plato("Milanesa", 1200, "principal")
        self.assertEqual(r.status_code, 201)

        r = await self.client.get("/menu")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["nombre"], "Milanesa")

    async def test_obtener_plato_por_id(self) -> None:
        """Crea un plato y lo obtiene por ID."""
        r = await self._crear_plato("Ensalada", 800, "entrada")
        plato_id = r.json()["id"]

        r = await self.client.get(f"/menu/{plato_id}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["nombre"], "Ensalada")
        self.assertEqual(r.json()["precio"], 800.0)

    async def test_actualizar_plato(self) -> None:
        """Crea un plato y actualiza solo el precio."""
        r = await self._crear_plato("Pizza", 1500, "principal")
        plato_id = r.json()["id"]

        r = await self.client.put(f"/menu/{plato_id}", json={"precio": 1800})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["precio"], 1800.0)
        self.assertEqual(r.json()["nombre"], "Pizza")  # no cambió

    async def test_eliminar_plato_y_404(self) -> None:
        """Elimina un plato y verifica que devuelva 404 al buscarlo."""
        r = await self._crear_plato("Flan", 500, "postre", descripcion="Flan casero")
        plato_id = r.json()["id"]

        r = await self.client.delete(f"/menu/{plato_id}")
        self.assertEqual(r.status_code, 204)

        r = await self.client.get(f"/menu/{plato_id}")
        self.assertEqual(r.status_code, 404)

    async def test_404_plato_inexistente(self) -> None:
        """Buscar un ID que nunca existió da 404."""
        r = await self.client.get("/menu/9999")
        self.assertEqual(r.status_code, 404)
        self.assertIn("no encontrado", r.json()["detail"])


class TestOrdenAPI(unittest.IsolatedAsyncioTestCase):
    """Prueba los endpoints de órdenes con base de datos en memoria."""

    async def asyncSetUp(self) -> None:
        """Misma configuración que TestMenuAPI."""
        self.engine = create_async_engine(TEST_DATABASE_URL, echo=False)
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        test_session_local = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

        async def override_get_session():
            async with test_session_local() as session:
                yield session

        app.dependency_overrides[get_session] = override_get_session

        self.client = AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()
        app.dependency_overrides.clear()
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        await self.engine.dispose()

    async def test_crear_orden_y_cambiar_estado(self) -> None:
        """Crea platos, crea orden con items, cambia estado."""
        r1 = await self.client.post(
            "/menu",
            json={
                "nombre": "Coca",
                "precio": 500,
                "categoria": "bebida",
            },
        )
        plato1 = r1.json()["id"]
        r2 = await self.client.post(
            "/menu",
            json={
                "nombre": "Bife",
                "precio": 1500,
                "categoria": "principal",
            },
        )
        plato2 = r2.json()["id"]

        r = await self.client.post(
            "/ordenes",
            json={
                "items": [
                    {"plato_id": plato1, "cantidad": 2},
                    {"plato_id": plato2, "cantidad": 1},
                ]
            },
        )
        self.assertEqual(r.status_code, 201)
        orden = r.json()
        self.assertEqual(orden["total"], 2500.0)
        self.assertEqual(orden["estado"], "pendiente")
        orden_id = orden["id"]

        r = await self.client.put(
            f"/ordenes/{orden_id}/estado",
            json={"estado": "entregado"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["estado"], "entregado")
