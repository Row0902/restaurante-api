# src/repositories/menu.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.models import Plato
from core.schemas import PlatoCreate, PlatoUpdate


class MenuRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Plato]:
        result = await self.session.execute(select(Plato))
        return result.scalars().all()

    async def get_by_id(self, plato_id: int) -> Plato | None:
        return await self.session.get(Plato, plato_id)

    async def add(self, data: PlatoCreate) -> Plato:
        plato = Plato(**data.model_dump())
        self.session.add(plato)
        await self.session.commit()
        await self.session.refresh(plato)
        return plato

    async def update(self, plato: Plato, data: PlatoUpdate) -> Plato:
        changes = data.model_dump(exclude_unset=True)
        for key, value in changes.items():
            setattr(plato, key, value)
        self.session.add(plato)
        await self.session.commit()
        await self.session.refresh(plato)
        return plato

    async def delete(self, plato: Plato) -> None:
        await self.session.delete(plato)
        await self.session.commit()
