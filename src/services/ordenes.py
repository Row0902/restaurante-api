"""Casos de uso para la gestión de órdenes."""

from core.exceptions import (
    EstadoInvalido,
    OrdenNoEncontrada,
    PlatoNoEncontrado,
)
from core.models.orden import Orden
from core.models.orden_item import OrdenItem
from core.schemas.estado_update import EstadoUpdate
from core.schemas.orden_create import OrdenCreate
from core.schemas.orden_item_create import OrdenItemCreate
from core.schemas.orden_read import OrdenRead
from repositories.menu import MenuRepository
from repositories.ordenes import OrdenRepository

_ESTADOS_VALIDOS = {"pendiente", "en_preparacion", "entregado", "cancelado"}


class OrdenService:
    """Casos de uso para órdenes. Inyección de repositorios por constructor."""

    def __init__(
        self,
        orden_repo: OrdenRepository,
        menu_repo: MenuRepository,
    ) -> None:
        self._orden_repo = orden_repo
        self._menu_repo = menu_repo

    async def listar(self) -> list[OrdenRead]:
        ordenes = await self._orden_repo.get_all()
        return [OrdenRead.model_validate(o) for o in ordenes]

    async def obtener(self, orden_id: int) -> OrdenRead:
        orden = await self._orden_repo.get_by_id(orden_id)
        if orden is None:
            raise OrdenNoEncontrada(orden_id)
        return OrdenRead.model_validate(orden)

    async def crear(self, datos: OrdenCreate) -> OrdenRead:
        items_modelo, total = await self._validar_y_calcular(datos.items)
        orden = Orden(total=total, items=items_modelo)
        creada = await self._orden_repo.add(orden)
        return OrdenRead.model_validate(creada)

    async def cambiar_estado(self, orden_id: int, datos: EstadoUpdate) -> OrdenRead:
        if datos.estado not in _ESTADOS_VALIDOS:
            raise EstadoInvalido(datos.estado)
        orden = await self._orden_repo.update_estado(orden_id, datos.estado)
        if orden is None:
            raise OrdenNoEncontrada(orden_id)
        return OrdenRead.model_validate(orden)

    # ── Métodos auxiliares ───────────────────────────────────

    async def _validar_y_calcular(
        self, items: list[OrdenItemCreate]
    ) -> tuple[list[OrdenItem], float]:
        items_modelo: list[OrdenItem] = []
        total = 0.0
        for item in items:
            plato = await self._menu_repo.get_by_id(item.plato_id)
            if plato is None:
                raise PlatoNoEncontrado(item.plato_id)
            items_modelo.append(
                OrdenItem(plato_id=item.plato_id, cantidad=item.cantidad)
            )
            total += plato.precio * item.cantidad
        return items_modelo, total
