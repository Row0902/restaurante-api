from fastapi import HTTPException

from core.models import Plato
from repositories.menu import MenuRepository


class MenuService:
    """Servicio encargado de la lógica de negocio del menú."""
    def __init__(self, repository: MenuRepository):
        self.repository = repository

    async def listar(self):
        """Obtiene todos los platos disponibles."""
        return await self.repository.get_all()

    async def obtener(self, plato_id: int):
        plato = await self.repository.get_by_id(plato_id)

        if not plato:
            raise HTTPException(
                status_code=404,
                detail="Plato no encontrado",
            )
        
        return plato

    async def crear(self, data):
        plato = Plato(**data.model_dump())
        return await self.repository.create(plato)

    async def actualizar(self, plato_id: int, data):
        plato = await self.obtener(plato_id)

        plato.nombre = data.nombre
        plato.descripcion = data.descripcion
        plato.precio = data.precio

        return await self.repository.update(plato)

    async def eliminar(self, plato_id: int):
        plato = await self.obtener(plato_id)

        await self.repository.delete(plato)

        return {"mensaje": "Plato eliminado"}