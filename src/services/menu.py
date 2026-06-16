"""MenuService — business logic orchestration for menu CRUD.

Receives MenuRepository via constructor injection. Delegates data
validation to schema-level polymorphic validate() before persisting.
Zero knowledge of HTTP, sessions, or infrastructure.
"""

from core.models.menu import MenuItem
from core.schemas.menu import PlatoCreate, PlatoUpdate
from repositories.menu import MenuRepository


class MenuService:
    """Business logic for menu operations.

    Validates input schemas polymorphically, then delegates to the
    repository layer. Domain exceptions propagate to the API layer.
    """

    def __init__(self, repository: MenuRepository) -> None:
        """Inject MenuRepository — service never creates its own."""
        self._repository = repository

    async def get_all(self) -> list[MenuItem]:
        """Return all menu items via repository."""
        return await self._repository.get_all()

    async def get_by_id(self, plato_id: int) -> MenuItem:
        """Return one menu item by ID via repository.

        Raises MenuNotFoundError when the item does not exist.
        """
        return await self._repository.get_by_id(plato_id)

    async def create(self, data: PlatoCreate) -> MenuItem:
        """Validate and persist a new menu item.

        Raises InvalidMenuDataError on validation failure.
        Repository is NOT called when validation fails.
        """
        data.validate()
        return await self._repository.create(data)

    async def update(self, plato_id: int, data: PlatoUpdate) -> MenuItem:
        """Validate and apply partial updates to a menu item.

        Raises InvalidMenuDataError on validation failure.
        Raises MenuNotFoundError when the item does not exist.
        """
        data.validate()
        return await self._repository.update(plato_id, data)

    async def delete(self, plato_id: int) -> None:
        """Delete a menu item by ID via repository.

        Raises MenuNotFoundError when the item does not exist.
        """
        await self._repository.delete(plato_id)
