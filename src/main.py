"""API de restaurante — menú y órdenes.

Aplicación FastAPI con routers modulares para menú y órdenes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.menu import router as menu_router
from api.routers.orden import router as orden_router

APP_NAME = "Restaurante API"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "API para la gestión de menú y órdenes de un restaurante."

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)

# Esto es terrible, pero funciona
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def raiz():
    """Endpoint raíz — health check."""
    return {"mensaje": "API corriendo 👋"}


app.include_router(menu_router)
app.include_router(orden_router)
