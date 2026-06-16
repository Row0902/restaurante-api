"""Repository for order data access."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import Orden


class OrdenRepository:
    """Repository for order data access."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with async database session."""
        self.session = session

    async def get_all(self) -> list[Orden]:
        """Retrieve all orders."""
        statement = select(Orden)
        result = await self.session.exec(statement)
        return list(result.all())

    async def get_by_id(self, orden_id: int) -> Orden | None:
        """Retrieve an order by ID. Returns None if not found."""
        return await self.session.get(Orden, orden_id)

    async def add(self, orden: Orden) -> Orden:
        """Add a new order to the database."""
        self.session.add(orden)
        await self.session.commit()
        await self.session.refresh(orden)
        return orden

    async def update_estado(self, orden_id: int, estado: str) -> Orden | None:
        """Update order status. Returns None if not found."""
        orden = await self.get_by_id(orden_id)
        if orden is None:
            return None
        orden.estado = estado
        self.session.add(orden)
        await self.session.commit()
        await self.session.refresh(orden)
        return orden
