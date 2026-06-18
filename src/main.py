"""API de restaurante — menú y órdenes.

Arquitectura limpia con FastAPI + SQLModel + SQLite asíncrona.
Capas: api/ → services/ → repositories/ → core/ — R4.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.deps import engine
from api.errors import (
    app_base_error_handler,
    invalid_order_state_handler,
    menu_item_not_found_handler,
    order_not_found_handler,
)
from api.menu import router as menu_router
from api.ordenes import router as ordenes_router
from core.database import init_db
from core.exceptions.base import AppBaseError
from core.exceptions.invalid_state import InvalidOrderStateError
from core.exceptions.not_found import MenuItemNotFoundError, OrderNotFoundError

APP_NAME = "Restaurante API"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "API para la gestión de menú y órdenes de un restaurante."


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Crea tablas al iniciar y libera recursos al cerrar.

    El motor asíncrono se crea una vez en ``api.deps``.
    """
    await init_db(engine)
    yield
    await engine.dispose()


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    lifespan=lifespan,
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Exception handlers — R15 ---
app.add_exception_handler(MenuItemNotFoundError, menu_item_not_found_handler)
app.add_exception_handler(OrderNotFoundError, order_not_found_handler)
app.add_exception_handler(InvalidOrderStateError, invalid_order_state_handler)
app.add_exception_handler(AppBaseError, app_base_error_handler)

# --- Routers ---
app.include_router(menu_router)
app.include_router(ordenes_router)


@app.get("/")
async def raiz() -> dict[str, str]:
    """Endpoint raíz — health check.

    Returns:
        Mensaje de bienvenida.
    """
    return {"mensaje": "API corriendo 👋"}
