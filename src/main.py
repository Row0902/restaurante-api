"""Ensamblador principal de FastAPI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from api.routers.health_router import router as health_router
from api.routers.menu_router import router as menu_router
from api.routers.orden_router import router as orden_router
from config import Config, cargar_config
from repositories.database import (
    construir_engine,
    construir_session_maker,
    crear_tablas,
)

APP_VERSION = "0.1.0"
APP_DESCRIPTION = "API para la gestion de menu y ordenes de un restaurante."


def crear_app(config: Config | None = None) -> FastAPI:
    """Construye la aplicacion FastAPI."""
    config = config or cargar_config()
    engine = construir_engine(config.database_url)
    session_maker = construir_session_maker(engine)
    app = _crear_fastapi(config, _lifespan(engine))
    _configurar_estado(app, session_maker)
    _registrar_middleware(app)
    _registrar_routers(app)
    return app


def _crear_fastapi(config: Config, lifespan) -> FastAPI:
    return FastAPI(
        title=config.app_name,
        debug=config.debug,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        lifespan=lifespan,
    )


def _lifespan(engine: AsyncEngine):
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        await crear_tablas(engine)
        yield
        await engine.dispose()

    return lifespan


def _configurar_estado(
    app: FastAPI,
    session_maker: async_sessionmaker[AsyncSession],
) -> None:
    app.state.session_maker = session_maker


def _registrar_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _registrar_routers(app: FastAPI) -> None:
    app.include_router(health_router)
    app.include_router(menu_router)
    app.include_router(orden_router)


app = crear_app()
