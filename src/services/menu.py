"""Service layer for menu business logic."""

from core.exceptions import NotFoundError
from core.models import Plato
from core.schemas import PlatoCreate, PlatoUpdate
from repositories.menu import MenuRepository


class MenuService:
    """Service for menu business logic."""

    def __init__(self, menu_repo: MenuRepository) -> None:
        """Initialize service with menu repository."""
        self.menu_repo = menu_repo

    async def list_all(self) -> list[Plato]:
        """Retrieve all menu items."""
        return await self.menu_repo.get_all()

    async def get_by_id(self, plato_id: int) -> Plato:
        """Retrieve a menu item by ID."""
        plato = await self.menu_repo.get_by_id(plato_id)
        if plato is None:
            raise NotFoundError(f"Plato with id {plato_id} not found")
        return plato

    async def create(self, data: PlatoCreate) -> Plato:
        """Create a new menu item."""
        plato = Plato(**data.model_dump())
        return await self.menu_repo.add(plato)

    async def update(self, plato_id: int, data: PlatoUpdate) -> Plato:
        """Update an existing menu item."""
        existing = await self.menu_repo.get_by_id(plato_id)
        if existing is None:
            raise NotFoundError(f"Plato with id {plato_id} not found")
        update_data = data.model_dump(exclude_unset=True)
        result = await self.menu_repo.update(plato_id, update_data)
        assert result is not None
        return result

    async def delete(self, plato_id: int) -> bool:
        """Delete a menu item."""
        return await self.menu_repo.delete(plato_id)
