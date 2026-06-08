"""Tests unitarios de servicios con repositorios mockeados."""

import unittest
from unittest.mock import AsyncMock

from core.exceptions import EstadoInvalido, PlatoNoEncontrado
from core.models.orden import Orden
from core.models.orden_item import OrdenItem
from core.models.plato import Plato
from core.schemas.estado_update import EstadoUpdate
from core.schemas.orden_create import OrdenCreate
from core.schemas.orden_item_create import OrdenItemCreate
from core.schemas.plato_create import PlatoCreate
from repositories.menu import MenuRepository
from repositories.ordenes import OrdenRepository
from services.menu import MenuService
from services.ordenes import OrdenService


class TestOrdenService(unittest.IsolatedAsyncioTestCase):
    """Prueba OrdenService con repositorios mockeados."""

    def setUp(self) -> None:
        self.mock_menu_repo = AsyncMock(spec=MenuRepository)
        self.mock_orden_repo = AsyncMock(spec=OrdenRepository)
        self.service = OrdenService(self.mock_orden_repo, self.mock_menu_repo)

    async def test_crear_orden_calcula_total(self) -> None:
        """El total se calcula como suma de precio * cantidad de cada item."""
        plato1 = Plato(id=1, nombre="Coca", precio=500, categoria="bebida")
        plato2 = Plato(id=2, nombre="Bife", precio=1500, categoria="principal")

        async def get_by_id(plato_id: int) -> Plato | None:
            return {1: plato1, 2: plato2}.get(plato_id)

        self.mock_menu_repo.get_by_id.side_effect = get_by_id
        self.mock_orden_repo.add.side_effect = self._simular_add_orden

        datos = OrdenCreate(
            items=[
                OrdenItemCreate(plato_id=1, cantidad=2),
                OrdenItemCreate(plato_id=2, cantidad=1),
            ]
        )

        resultado = await self.service.crear(datos)

        total_esperado = 500 * 2 + 1500 * 1  # 2500
        self.assertEqual(resultado.total, total_esperado)
        self.assertEqual(len(resultado.items), 2)

    async def test_crear_orden_plato_no_existe(self) -> None:
        """Lanza PlatoNoEncontrado si un plato del pedido no existe."""
        self.mock_menu_repo.get_by_id.return_value = None

        datos = OrdenCreate(items=[OrdenItemCreate(plato_id=999, cantidad=1)])

        with self.assertRaises(PlatoNoEncontrado):
            await self.service.crear(datos)

    async def test_cambiar_estado_valido(self) -> None:
        """Cambiar a un estado válido actualiza y devuelve la orden."""
        orden = Orden(
            id=1,
            total=500.0,
            estado="entregado",
            items=[OrdenItem(id=1, plato_id=1, cantidad=1)],
        )
        self.mock_orden_repo.update_estado.return_value = orden

        resultado = await self.service.cambiar_estado(
            1, EstadoUpdate(estado="entregado")
        )

        self.assertEqual(resultado.estado, "entregado")
        self.assertEqual(resultado.id, 1)
        self.mock_orden_repo.update_estado.assert_called_once_with(1, "entregado")

    async def test_cambiar_estado_invalido(self) -> None:
        """Lanza EstadoInvalido si el estado no está en el set permitido."""
        with self.assertRaises(EstadoInvalido):
            await self.service.cambiar_estado(1, EstadoUpdate(estado="cocinado"))

    # ── Helper ──────────────────────────────────────────────

    def _simular_add_orden(self, orden: Orden) -> Orden:
        """Simula la DB asignando IDs a orden e items."""
        orden.id = 1
        for i, item in enumerate(orden.items):
            item.id = i + 1
        return orden


class TestMenuService(unittest.IsolatedAsyncioTestCase):
    """Prueba MenuService con repositorio mockeado."""

    def setUp(self) -> None:
        self.mock_repo = AsyncMock(spec=MenuRepository)
        self.service = MenuService(self.mock_repo)

    async def test_crear_plato_llama_validacion(self) -> None:
        """Al crear un plato se persiste y retorna PlatoRead con id."""
        self.mock_repo.add.side_effect = self._simular_add_plato

        datos = PlatoCreate(nombre="Cafe", precio=200, categoria="bebida")
        resultado = await self.service.crear(datos)

        self.assertEqual(resultado.id, 1)
        self.assertEqual(resultado.nombre, "Cafe")
        self.assertEqual(resultado.precio, 200.0)
        self.mock_repo.add.assert_called_once()

    def _simular_add_plato(self, plato: Plato) -> Plato:
        """Simula la DB asignando un ID al plato."""
        plato.id = 1
        return plato
