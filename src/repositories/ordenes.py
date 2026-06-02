# src/repositories/ordenes.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.models import Orden, OrdenItem


class OrdenesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Orden]:
        result = await self.session.execute(
            select(Orden).options(selectinload(Orden.items))
        )
        return result.scalars().all()

    async def get_by_id(self, orden_id: int) -> Orden | None:
        result = await self.session.execute(
            select(Orden)
            .where(Orden.id == orden_id)
            .options(selectinload(Orden.items))
        )
        return result.scalars().first()

    async def add(self, orden: Orden, items: list[OrdenItem]) -> Orden:
        self.session.add(orden)
        await self.session.flush()
        for item in items:
            item.orden_id = orden.id
            self.session.add(item)
        await self.session.commit()
        return await self.get_by_id(orden.id)

    async def update_estado(self, orden: Orden, estado: str) -> Orden:
        orden.estado = estado
        self.session.add(orden)
        await self.session.commit()
        return await self.get_by_id(orden.id)