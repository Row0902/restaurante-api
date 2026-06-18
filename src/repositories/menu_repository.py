"""Repositorio para platos del menú."""

from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import Plato
from repositories.base_repository import BaseRepository


class MenuRepository(BaseRepository[Plato]):
    """Repositorio específico para operaciones de Plato."""

    def __init__(self, session: AsyncSession):
        """Inicializa el repositorio de menú."""
        super().__init__(session, Plato)
