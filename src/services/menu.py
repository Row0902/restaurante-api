"""Servicio de aplicación para la gestión del menú.

Orquesta las operaciones de negocio sobre platos.
Recibe el repositorio por constructor — R7.
"""

from __future__ import annotations

from core.models.menu_item import MenuItem
from core.repositories.menu import AbstractMenuRepository
from core.schemas.menu_item import CreatePlatoRequest, PlatoResponse


class MenuService:
    """Lógica de negocio para platos del menú."""

    def __init__(self, repo: AbstractMenuRepository) -> None:
        """Inicializa el servicio con un repositorio de menú.

        Args:
            repo: Repositorio que implementa AbstractMenuRepository.
        """
        self._repo = repo

    async def listar(self) -> list[PlatoResponse]:
        """Lista todos los platos del menú."""
        items = await self._repo.get_all()
        return [PlatoResponse.model_validate(item) for item in items]

    async def obtener_por_id(self, plato_id: int) -> PlatoResponse:
        """Obtiene un plato por ID. Lanza MenuItemNotFoundError si no existe."""
        item = await self._repo.get_by_id(plato_id)
        return PlatoResponse.model_validate(item)

    async def crear(self, request: CreatePlatoRequest) -> PlatoResponse:
        """Crea un plato nuevo a partir de los datos validados."""
        item = MenuItem(**request.model_dump())
        created = await self._repo.add(item)
        return PlatoResponse.model_validate(created)

    async def actualizar(
        self, plato_id: int, request: CreatePlatoRequest
    ) -> PlatoResponse:
        """Actualiza todos los campos de un plato existente."""
        existing = await self._repo.get_by_id(plato_id)
        existing.nombre = request.nombre
        existing.precio = request.precio
        existing.descripcion = request.descripcion
        existing.categoria = request.categoria
        updated = await self._repo.add(existing)
        return PlatoResponse.model_validate(updated)

    async def eliminar(self, plato_id: int) -> dict[str, object]:
        """Elimina un plato. Lanza MenuItemNotFoundError si no existe."""
        await self._repo.delete(plato_id)
        return {"mensaje": "Plato eliminado", "id": plato_id}
