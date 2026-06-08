"""Repositorio de acceso a datos para la entidad Orden."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from core.models.orden import Orden


class OrdenRepository:
    """Acceso a datos de Orden. Sin lógica de negocio."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> list[Orden]:
        result = await self._session.execute(
            select(Orden).options(selectinload(Orden.items))  # type: ignore
        )
        return list(result.scalars().all())

    async def get_by_id(self, orden_id: int) -> Orden | None:
        result = await self._session.execute(
            select(Orden).where(Orden.id == orden_id).options(selectinload(Orden.items))  # type: ignore
        )
        return result.scalar_one_or_none()

    async def add(self, orden: Orden) -> Orden:
        self._session.add(orden)
        await self._session.commit()
        await self._session.refresh(orden)
        await self._session.refresh(orden, ["items"])
        return orden

    async def update_estado(self, orden_id: int, estado: str) -> Orden | None:
        orden = await self.get_by_id(orden_id)
        if orden is None:
            return None
        orden.estado = estado
        await self._session.commit()
        await self._session.refresh(orden)
        await self._session.refresh(orden, ["items"])
        return orden
