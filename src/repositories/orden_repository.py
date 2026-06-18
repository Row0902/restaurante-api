"""Repositorio para órdenes."""

from typing import Any, List, Optional

from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import Orden
from repositories.base_repository import BaseRepository


class OrdenRepository(BaseRepository[Orden]):
    """Repositorio específico para Orden."""

    def __init__(self, session: AsyncSession):
        """Inicializa el repositorio de órdenes."""
        super().__init__(session, Orden)

    async def get_by_id_with_items(self, id: Any) -> Optional[Orden]:
        """Obtiene una orden con sus ítems cargados."""
        statement = select(Orden).where(Orden.id == id).options(selectinload(Orden.items))
        result = await self.session.exec(statement)
        return result.first()

    async def get_all_with_items(self) -> List[Orden]:
        """Obtiene todas las órdenes con sus ítems cargados."""
        statement = select(Orden).options(selectinload(Orden.items))
        result = await self.session.exec(statement)
        return list(result.all())
