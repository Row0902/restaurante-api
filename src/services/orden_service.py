"""Lógica de negocio para órdenes."""

from typing import List

from core.exceptions import OrdenNotFoundError, PlatoNotFoundError
from core.models import Orden, OrdenItem
from core.schemas import OrdenCreate
from repositories.menu_repository import MenuRepository
from repositories.orden_repository import OrdenRepository


class OrdenService:
    """Servicio para gestionar órdenes."""

    def __init__(self, orden_repo: OrdenRepository, menu_repo: MenuRepository):
        """Inicializa el servicio con sus repositorios."""
        self.orden_repo = orden_repo
        self.menu_repo = menu_repo

    async def obtener_todas(self) -> List[Orden]:
        """Obtiene todas las órdenes."""
        return await self.orden_repo.get_all_with_items()

    async def obtener_por_id(self, orden_id: str) -> Orden:
        """Obtiene una orden específica."""
        orden = await self.orden_repo.get_by_id_with_items(orden_id)
        if not orden:
            raise OrdenNotFoundError(f"Orden con ID {orden_id} no encontrada.")
        return orden

    async def crear(self, orden_data: OrdenCreate) -> Orden:
        """Crea una orden validando platos y calculando el total."""
        total = 0.0
        items_db = []
        
        for item in orden_data.items:
            plato = await self.menu_repo.get_by_id(item.plato_id)
            if not plato:
                raise PlatoNotFoundError(f"Plato con ID {item.plato_id} no existe.")
            
            total += plato.precio * item.cantidad
            items_db.append(OrdenItem(plato_id=item.plato_id, cantidad=item.cantidad))
            
        orden = Orden(total=total, estado="pendiente", items=items_db)
        orden = await self.orden_repo.add(orden)
        return await self.obtener_por_id(orden.id)
    async def cambiar_estado(self, orden_id: str, nuevo_estado: str) -> Orden:
        """Cambia el estado de una orden."""
        orden = await self.obtener_por_id(orden_id)
        orden.estado = nuevo_estado
        return await self.orden_repo.update(orden)

    async def eliminar(self, orden_id: str) -> None:
        """Elimina una orden por su ID."""
        orden = await self.obtener_por_id(orden_id)
        await self.orden_repo.delete(orden)
