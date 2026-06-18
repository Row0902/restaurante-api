"""Repositorio base para operaciones asíncronas."""

from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    """Implementación base de un repositorio CRUD."""

    def __init__(self, session: AsyncSession, model: Type[T]):
        """Inicializa el repositorio con la sesión y el modelo."""
        self.session = session
        self.model = model

    async def get_all(self) -> List[T]:
        """Obtiene todos los registros."""
        result = await self.session.exec(select(self.model))
        return list(result.all())

    async def get_by_id(self, id: Any) -> Optional[T]:
        """Obtiene un registro por su ID."""
        return await self.session.get(self.model, id)

    async def add(self, entity: T) -> T:
        """Agrega un nuevo registro."""
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        """Actualiza un registro existente."""
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        """Elimina un registro."""
        await self.session.delete(entity)
        await self.session.commit()
