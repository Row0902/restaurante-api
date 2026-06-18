"""Dependencias compartidas para la capa API.

Provee:
- ``get_db``: sesión asíncrona SQLAlchemy via FastAPI ``Depends``.
- ``get_menu_service``: ``MenuService`` con repositorio inyectado.
- ``get_order_service``: ``OrderService`` con repositorios inyectados.

El motor se crea una sola vez a nivel de módulo. ``main.py`` lo importa
para lifecycle (``init_db`` / ``dispose``). R7, R14.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import Settings
from core.database import create_engine, get_session, session_factory
from repositories.menu import MenuRepository
from repositories.ordenes import OrderRepository
from services.menu import MenuService
from services.ordenes import OrderService

settings = Settings()
engine = create_engine(settings.DATABASE_URL)
SessionFactory = session_factory(engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provee una sesión asíncrona de base de datos.

    Yields:
        Una instancia de AsyncSession lista para usar.
    """
    async for session in get_session(SessionFactory):
        yield session


async def get_menu_service(
    session: AsyncSession = Depends(get_db),
) -> MenuService:
    """Provee un MenuService con inyección del repositorio."""
    repo = MenuRepository(session)
    return MenuService(repo)


async def get_order_service(
    session: AsyncSession = Depends(get_db),
) -> OrderService:
    """Provee un OrderService con inyección de repositorios."""
    order_repo = OrderRepository(session)
    menu_repo = MenuRepository(session)
    return OrderService(order_repo, menu_repo)
