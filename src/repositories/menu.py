"""MenuRepository — async CRUD over MenuItem via SQLModel AsyncSession.

Repository flushes but never commits — transaction boundary is external.
"""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.exceptions import MenuNotFoundError
from core.models.menu import MenuItem
from core.schemas.menu import PlatoCreate, PlatoUpdate


class MenuRepository:
    """Async CRUD repository for MenuItem.

    Receives an AsyncSession via constructor injection.
    All five public methods are async. Each ≤ 20 lines (Rule 8).
    """

    def __init__(self, session: AsyncSession) -> None:
        """Inject the async session.

        Repository flushes but never commits — the caller
        (service layer) owns the transaction boundary.
        """
        self._session = session

    async def get_all(self) -> list[MenuItem]:
        """Return all menu items from the database."""
        result = await self._session.exec(select(MenuItem))
        return list(result.all())

    async def get_by_id(self, plato_id: int) -> MenuItem:
        """Return one menu item by primary key.

        Raises MenuNotFoundError when the item does not exist.
        """
        item = await self._session.get(MenuItem, plato_id)
        if item is None:
            raise MenuNotFoundError(plato_id)
        return item

    async def create(self, data: PlatoCreate) -> MenuItem:
        """Persist a new menu item and return it with generated id."""
        item = MenuItem(**data.model_dump())
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)
        return item

    async def update(self, plato_id: int, data: PlatoUpdate) -> MenuItem:
        """Apply partial updates to an existing menu item.

        Only fields explicitly provided in PlatoUpdate are changed.
        """
        item = await self.get_by_id(plato_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        await self._session.flush()
        await self._session.refresh(item)
        return item

    async def delete(self, plato_id: int) -> None:
        """Delete a menu item by primary key.

        Raises MenuNotFoundError when the item does not exist.
        """
        item = await self.get_by_id(plato_id)
        await self._session.delete(item)
        await self._session.flush()
