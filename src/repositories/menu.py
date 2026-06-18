"""Implementación SQLModel del repositorio de menú.

Operaciones asíncronas con SQLAlchemy — R14.
Implementa AbstractMenuRepository — R7.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions.not_found import MenuItemNotFoundError
from core.models.menu_item import MenuItem
from core.repositories.menu import AbstractMenuRepository


class MenuRepository(AbstractMenuRepository):
    """Acceso a datos de platos del menú via SQLModel."""

    def __init__(self, session: AsyncSession) -> None:
        """Inicializa el repositorio con una sesión activa.

        Args:
            session: Sesión asíncrona SQLAlchemy.
        """
        self._session = session

    async def get_all(self) -> list[MenuItem]:
        """Obtiene todos los platos del menú."""
        result = await self._session.execute(select(MenuItem))
        return list(result.scalars().all())

    async def get_by_id(self, menu_item_id: int) -> MenuItem:
        """Busca un plato por ID. Lanza MenuItemNotFoundError si no existe."""
        item = await self._session.get(MenuItem, menu_item_id)
        if item is None:
            raise MenuItemNotFoundError(plato_id=menu_item_id)
        return item

    async def add(self, item: MenuItem) -> MenuItem:
        """Agrega un plato y retorna con ID asignado."""
        self._session.add(item)
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def delete(self, menu_item_id: int) -> None:
        """Elimina un plato por ID. Lanza MenuItemNotFoundError si no existe."""
        item = await self._session.get(MenuItem, menu_item_id)
        if item is None:
            raise MenuItemNotFoundError(plato_id=menu_item_id)
        await self._session.delete(item)
        await self._session.commit()
