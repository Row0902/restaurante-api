"""Interfaz abstracta para el repositorio de menú.

Define el contrato que toda implementación debe cumplir.
Los servicios dependen de esta abstracción, no de implementaciones concretas — R7.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.menu_item import MenuItem


class AbstractMenuRepository(ABC):
    """Puerto de acceso a datos para platos del menú."""

    @abstractmethod
    async def get_all(self) -> list[MenuItem]:
        """Obtiene todos los platos del menú.

        Returns:
            Lista de platos.
        """
        ...

    @abstractmethod
    async def get_by_id(self, menu_item_id: int) -> MenuItem:
        """Busca un plato por su ID.

        Args:
            menu_item_id: ID del plato.

        Returns:
            El plato encontrado.

        Raises:
            MenuItemNotFoundError: Si el plato no existe.
        """
        ...

    @abstractmethod
    async def add(self, item: MenuItem) -> MenuItem:
        """Agrega un nuevo plato al menú.

        Args:
            item: Plato a agregar (ID ignorado, la DB lo asigna).

        Returns:
            El plato con su ID asignado.
        """
        ...

    @abstractmethod
    async def delete(self, menu_item_id: int) -> None:
        """Elimina un plato por ID.

        Args:
            menu_item_id: ID del plato.

        Raises:
            MenuItemNotFoundError: Si no existe.
        """
        ...
