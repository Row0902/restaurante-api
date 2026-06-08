"""Repositorio de acceso a datos para la entidad Plato."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.models.plato import Plato


class MenuRepository:
    """Acceso a datos de Plato. Sin lógica de negocio."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> list[Plato]:
        result = await self._session.execute(select(Plato))
        return list(result.scalars().all())

    async def get_by_id(self, plato_id: int) -> Plato | None:
        result = await self._session.execute(select(Plato).where(Plato.id == plato_id))
        return result.scalar_one_or_none()

    async def add(self, plato: Plato) -> Plato:
        self._session.add(plato)
        await self._session.commit()
        await self._session.refresh(plato)
        return plato

    async def update(self, plato_id: int, datos: dict) -> Plato | None:
        plato = await self.get_by_id(plato_id)
        if plato is None:
            return None
        for campo, valor in datos.items():
            setattr(plato, campo, valor)
        await self._session.commit()
        await self._session.refresh(plato)
        return plato

    async def delete(self, plato_id: int) -> bool:
        plato = await self.get_by_id(plato_id)
        if plato is None:
            return False
        await self._session.delete(plato)
        await self._session.commit()
        return True
