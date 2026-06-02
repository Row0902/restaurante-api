# src/services/ordenes.py
from fastapi import HTTPException, status

from core.models import Orden, OrdenItem
from core.schemas import OrdenCreate, OrdenEstadoUpdate
from repositories.menu import MenuRepository
from repositories.ordenes import OrdenesRepository

ESTADOS_VALIDOS = {"pendiente", "preparando", "listo", "entregado", "cancelado"}


class OrdenesService:
    def __init__(self, repo: OrdenesRepository, menu_repo: MenuRepository):
        self.repo = repo
        self.menu_repo = menu_repo

    async def listar(self) -> list[Orden]:
        return await self.repo.get_all()

    async def obtener(self, orden_id: int) -> Orden:
        orden = await self.repo.get_by_id(orden_id)
        if not orden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden {orden_id} no encontrada",
            )
        return orden

    async def crear(self, data: OrdenCreate) -> Orden:
        total = 0.0
        items = []
        for item_data in data.items:
            plato = await self.menu_repo.get_by_id(item_data.plato_id)
            if not plato:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Plato {item_data.plato_id} no encontrado",
                )
            total += plato.precio * item_data.cantidad
            items.append(OrdenItem(
                plato_id=item_data.plato_id,
                cantidad=item_data.cantidad,
            ))
        orden = Orden(total=total)
        return await self.repo.add(orden, items)

    async def cambiar_estado(self, orden_id: int, data: OrdenEstadoUpdate) -> Orden:
        if data.estado not in ESTADOS_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Estado inválido. Válidos: {ESTADOS_VALIDOS}",
            )
        orden = await self.obtener(orden_id)
        return await self.repo.update_estado(orden, data.estado)