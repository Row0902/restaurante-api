from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import Orden


class OrdenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self):
        result = await self.session.exec(
            select(Orden)
        )
        return result.all()

    async def get_by_id(self, orden_id: int):
        return await self.session.get(
            Orden,
            orden_id,
        )

    async def create(self, orden: Orden):
        self.session.add(orden)

        await self.session.commit()
        await self.session.refresh(orden)

        return orden

    async def update(self, orden: Orden):
        self.session.add(orden)

        await self.session.commit()
        await self.session.refresh(orden)

        return orden