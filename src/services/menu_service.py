"""Lógica de negocio para menú."""

from typing import List

from core.exceptions import PlatoNotFoundError
from core.models import Plato
from core.schemas import PlatoCreate, PlatoUpdate
from repositories.menu_repository import MenuRepository


class MenuService:
    """Servicio para gestionar el menú."""

    def __init__(self, menu_repo: MenuRepository):
        """Inicializa el servicio con su repositorio."""
        self.menu_repo = menu_repo

    async def obtener_todos(self) -> List[Plato]:
        """Obtiene todos los platos del menú."""
        return await self.menu_repo.get_all()

    async def obtener_por_id(self, plato_id: str) -> Plato:
        """Obtiene un plato específico o lanza excepción."""
        plato = await self.menu_repo.get_by_id(plato_id)
        if not plato:
            raise PlatoNotFoundError(f"Plato con ID {plato_id} no encontrado.")
        return plato

    async def crear(self, plato_data: PlatoCreate) -> Plato:
        """Crea un nuevo plato."""
        plato = Plato(**plato_data.model_dump())
        return await self.menu_repo.add(plato)

    async def actualizar(self, plato_id: str, plato_data: PlatoUpdate) -> Plato:
        """Actualiza un plato existente."""
        plato = await self.obtener_por_id(plato_id)
        update_data = plato_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(plato, key, value)
        return await self.menu_repo.update(plato)

    async def eliminar(self, plato_id: str) -> None:
        """Elimina un plato."""
        plato = await self.obtener_por_id(plato_id)
        await self.menu_repo.delete(plato)
