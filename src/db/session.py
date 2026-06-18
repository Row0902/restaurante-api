"""Configuración de base de datos asíncrona."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Generador de sesión de base de datos."""
    async with AsyncSession(engine) as session:
        yield session
