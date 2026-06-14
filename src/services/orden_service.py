"""Servicio de aplicacion para ordenes."""

from decimal import Decimal
from typing import cast

from core.cantidad import Cantidad
from core.dominio_error import DominioError
from core.estado_orden import EstadoOrden
from core.item_orden import ItemOrden
from core.orden import Orden
from core.precio import Precio
from core.registro import Registro
from repositories.menu_repository import MenuRepository
from repositories.orden_repository import OrdenRepository


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
        items_dominio = await self._construir_items(items)
        orden_dominio = Orden(id=orden_id, items=tuple(items_dominio))
        nueva_orden = self._construir_registro(orden_dominio, items)
        return await self._orden_repo.guardar(orden_id, nueva_orden)

    async def obtener(self, orden_id: str) -> Registro:
        """Devuelve una orden por ID."""
        return await self._orden_repo.obtener(orden_id)

    async def cambiar_estado(self, orden_id: str, estado: Registro) -> Registro:
        """Cambia el estado de una orden validando el ciclo de vida."""
        registro = await self._orden_repo.obtener(orden_id)
        orden = self._orden_desde_registro(registro)
        actualizada = orden.cambiar_estado(self._estado_desde_valor(estado.get("estado")))
        registro_actualizado = {**registro, "estado": actualizada.estado.value}
        return await self._orden_repo.actualizar(orden_id, registro_actualizado)

    async def _construir_items(self, items: list[Registro]) -> list[ItemOrden]:
        return [await self._construir_item(item) for item in items]

    async def _construir_item(self, item: Registro) -> ItemOrden:
        plato_id = str(item.get("plato_id", ""))
        cantidad = Cantidad(item.get("cantidad", 1))
        plato = await self._menu_repo.obtener(plato_id)
        precio = Precio(str(plato["precio"]))
        return ItemOrden(plato_id=plato_id, cantidad=cantidad, precio_unitario=precio)

    def _orden_desde_registro(self, registro: Registro) -> Orden:
        estado = self._estado_desde_valor(registro.get("estado"))
        return Orden(id=str(registro.get("id", "")), items=(), estado=estado)

    def _estado_desde_valor(self, valor: object) -> EstadoOrden:
        try:
            return EstadoOrden(str(valor))
        except ValueError as exc:
            raise DominioError("estado de orden invalido") from exc

    def _construir_registro(self, orden: Orden, items: list[Registro]) -> Registro:
        return {
            "id": orden.id,
            "items": items,
            "total": self._serializar_total(orden.total().monto),
            "estado": orden.estado.value,
        }

    def _serializar_total(self, total: Decimal) -> int | float:
        if total == total.to_integral_value():
            return int(total)
        return float(total)
