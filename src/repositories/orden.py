"""OrdenRepository — async CRUD over Orden and OrdenItem via SQLModel AsyncSession.

Repository flushes but never commits — transaction boundary is external.
"""

from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.exceptions import OrdenNotFoundError
from core.models.orden import Orden, OrdenItem
from core.schemas.orden import OrdenCreate, OrdenUpdateEstado


class OrdenRepository:
    """Async CRUD repository for Orden with its OrdenItem children.

    Receives an AsyncSession via constructor injection.
    All five public methods are async. Each ≤ 20 lines (Rule 8).
    """

    def __init__(self, session: AsyncSession) -> None:
        """Inject the async session.

        Repository flushes but never commits — the caller
        (service layer) owns the transaction boundary.
        """
        self._session = session

    async def get_all(self) -> list[Orden]:
        """Return all orders from the database with items eagerly loaded."""
        result = await self._session.exec(
            select(Orden).options(selectinload(Orden.items))  # type: ignore
        )
        return list(result.all())

    async def get_by_id(self, orden_id: int) -> Orden:
        """Return one order by primary key with items eagerly loaded.

        Raises OrdenNotFoundError when the order does not exist.
        """
        query = (
            select(Orden).where(Orden.id == orden_id).options(selectinload(Orden.items))  # type: ignore
        )
        result = await self._session.exec(query)
        orden = result.one_or_none()
        if orden is None:
            raise OrdenNotFoundError(orden_id)
        return orden

    async def create(
        self,
        data: OrdenCreate,
        items_data: list[dict],
        total: float,
    ) -> Orden:
        """Persist a new order with its line items and return it with generated id."""
        orden = Orden(total=total, mesa=data.mesa, estado="pendiente")
        self._session.add(orden)
        await self._session.flush()

        assert orden.id is not None
        for item_dict in items_data:
            item = OrdenItem(orden_id=orden.id, **item_dict)
            self._session.add(item)
        await self._session.flush()

        return await self.get_by_id(orden.id)

    async def update(self, orden_id: int, data: OrdenUpdateEstado) -> Orden:
        """Update the estado of an existing order.

        Raises OrdenNotFoundError when the order does not exist.
        """
        orden = await self.get_by_id(orden_id)
        orden.estado = data.estado
        await self._session.flush()
        return await self.get_by_id(orden_id)

    async def delete(self, orden_id: int) -> None:
        """Delete an order by primary key.

        Raises OrdenNotFoundError when the order does not exist.
        """
        orden = await self.get_by_id(orden_id)
        await self._session.delete(orden)
        await self._session.flush()
