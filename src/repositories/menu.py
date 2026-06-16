"""Repository for menu item data access."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import Plato


class MenuRepository:
    """Repository for menu item data access."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with async database session."""
        self.session = session

    async def get_all(self) -> list[Plato]:
        """Retrieve all menu items."""
        statement = select(Plato)
        result = await self.session.exec(statement)
        return list(result.all())

    async def get_by_id(self, plato_id: int) -> Plato | None:
        """Retrieve a menu item by ID. Returns None if not found."""
        return await self.session.get(Plato, plato_id)

    async def add(self, plato: Plato) -> Plato:
        """Add a new menu item to the database."""
        self.session.add(plato)
        await self.session.commit()
        await self.session.refresh(plato)
        return plato

    async def update(self, plato_id: int, data: dict) -> Plato | None:
        """Update an existing menu item. Returns None if not found."""
        plato = await self.get_by_id(plato_id)
        if plato is None:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(plato, key, value)
        self.session.add(plato)
        await self.session.commit()
        await self.session.refresh(plato)
        return plato

    async def delete(self, plato_id: int) -> bool:
        """Delete a menu item. Returns True if deleted, False if not found."""
        plato = await self.get_by_id(plato_id)
        if plato is None:
            return False
        await self.session.delete(plato)
        await self.session.commit()
        return True
