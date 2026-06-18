"""API de restaurante — menú y órdenes.

Versión refactorizada aplicando Clean Architecture.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.error_handlers import setup_exception_handlers
from api.menu_router import router as menu_router
from api.orden_router import router as orden_router
from core.config import settings
from core.models import SQLModel
from db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API para la gestión de menú y órdenes de un restaurante.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
setup_exception_handlers(app)

app.include_router(menu_router)
app.include_router(orden_router)


@app.get("/", tags=["Raíz"])
async def raiz() -> dict[str, str]:
    """Endpoint raíz — health check."""
    return {"mensaje": "API corriendo 👋"}
