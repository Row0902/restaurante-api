from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import Plato


class MenuRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self):
        result = await self.session.exec(select(Plato))
        return result.all()

    async def get_by_id(self, plato_id: int):
        return await self.session.get(Plato, plato_id)

    async def create(self, plato: Plato):
        self.session.add(plato)
        await self.session.commit()
        await self.session.refresh(plato)
        return plato

    async def update(self, plato: Plato):
        self.session.add(plato)
        await self.session.commit()
        await self.session.refresh(plato)
        return plato

    async def delete(self, plato: Plato):
        await self.session.delete(plato)
        await self.session.commit()