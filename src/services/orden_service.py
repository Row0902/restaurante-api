"""Servicio de aplicacion para ordenes."""

from typing import cast

from repositories.menu_repository import MenuRepository
from repositories.orden_repository import OrdenRepository, Registro


class OrdenService:
    """Coordina casos de uso de ordenes."""

    def __init__(self, orden_repo: OrdenRepository, menu_repo: MenuRepository) -> None:
        """Recibe repositorios de ordenes y menu."""
        self._orden_repo = orden_repo
        self._menu_repo = menu_repo

    async def listar(self) -> list[Registro]:
        """Devuelve todas las ordenes."""
        return await self._orden_repo.listar()

    async def crear(self, orden: Registro) -> Registro:
        """Crea una orden calculando total y estado inicial."""
        orden_id = str(len(await self._orden_repo.listar()) + 1)
        items = cast(list[Registro], orden.get("items", []))
        total = await self._calcular_total(items)
        nueva_orden = self._construir_orden(orden_id, items, total)
        return await self._orden_repo.guardar(orden_id, nueva_orden)

    async def obtener(self, orden_id: str) -> Registro:
        """Devuelve una orden por ID."""
        return await self._orden_repo.obtener(orden_id)

    async def cambiar_estado(self, orden_id: str, estado: Registro) -> Registro:
        """Cambia el estado de una orden sin validar valores."""
        orden = await self._orden_repo.obtener(orden_id)
        orden["estado"] = estado.get("estado")
        return await self._orden_repo.actualizar(orden_id, orden)

    async def _calcular_total(self, items: list[Registro]) -> object:
        total = 0
        for item in items:
            plato = await self._menu_repo.obtener(cast(str, item.get("plato_id")))
            precio = cast(int | float, plato["precio"])
            cantidad = cast(int, item.get("cantidad", 1))
            total += precio * cantidad
        return total

    def _construir_orden(
        self,
        orden_id: str,
        items: list[Registro],
        total: object,
    ) -> Registro:
        return {"id": orden_id, "items": items, "total": total, "estado": "pendiente"}
