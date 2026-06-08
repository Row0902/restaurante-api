from fastapi import HTTPException

from core.models import Orden
from repositories.menu import MenuRepository
from repositories.ordenes import OrdenRepository


class OrdenService:
    def __init__(
        self,
        orden_repository: OrdenRepository,
        menu_repository: MenuRepository,
    ):
        self.orden_repository = orden_repository
        self.menu_repository = menu_repository

    async def listar(self):
        return await self.orden_repository.get_all()

    async def obtener(self, orden_id: int):
        orden = await self.orden_repository.get_by_id(
            orden_id
        )

        if not orden:
            raise HTTPException(
                status_code=404,
                detail="Orden no encontrada",
            )

        return orden

    async def crear(self, data):
        total = 0

        for item in data.items:
            plato = await self.menu_repository.get_by_id(
                item.plato_id
            )

            if not plato:
                raise HTTPException(
                    status_code=404,
                    detail=f"Plato {item.plato_id} no encontrado",
                )

            total += plato.precio * item.cantidad

        orden = Orden(
            items=[
                item.model_dump()
                for item in data.items
            ],
            total=total,
            estado="pendiente",
        )

        return await self.orden_repository.create(
            orden
        )

    async def cambiar_estado(
        self,
        orden_id: int,
        nuevo_estado: str,
    ):
        orden = await self.obtener(orden_id)

        orden.estado = nuevo_estado

        return await self.orden_repository.update(
            orden
        )