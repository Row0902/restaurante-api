# src/services/menu.py
from fastapi import HTTPException, status

from core.models import Plato
from core.schemas import PlatoCreate, PlatoUpdate
from repositories.menu import MenuRepository


class MenuService:
    def __init__(self, repo: MenuRepository):
        self.repo = repo

    async def listar(self) -> list[Plato]:
        return await self.repo.get_all()

    async def obtener(self, plato_id: int) -> Plato:
        plato = await self.repo.get_by_id(plato_id)
        if not plato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plato {plato_id} no encontrado",
            )
        return plato

    async def crear(self, data: PlatoCreate) -> Plato:
        return await self.repo.add(data)

    async def actualizar(self, plato_id: int, data: PlatoUpdate) -> Plato:
        plato = await self.obtener(plato_id)
        return await self.repo.update(plato, data)

    async def eliminar(self, plato_id: int) -> None:
        plato = await self.obtener(plato_id)
        await self.repo.delete(plato)