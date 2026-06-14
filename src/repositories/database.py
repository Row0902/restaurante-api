"""Infraestructura de base de datos async."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from repositories.database_settings import DatabaseSettings


def construir_engine(database_url: str) -> AsyncEngine:
    """Construye un engine async para SQLAlchemy."""
    return create_async_engine(database_url)


def construir_session_maker(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Construye factory de sesiones async."""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def importar_modelos() -> None:
    """Carga modelos para registrar metadata de SQLModel."""
    import repositories.models.orden_item_model  # noqa: F401
    import repositories.models.orden_model  # noqa: F401
    import repositories.models.plato_model  # noqa: F401


async def crear_tablas(engine: AsyncEngine) -> None:
    """Crea tablas declaradas en metadata."""
    importar_modelos()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def obtener_sesion() -> AsyncIterator[AsyncSession]:
    """Entrega una sesion async por request."""
    async with session_maker() as session:
        yield session


settings = DatabaseSettings()
engine = construir_engine(settings.database_url)
session_maker = construir_session_maker(engine)
