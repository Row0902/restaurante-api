"""API de restaurante — menú y órdenes."""

from fastapi import FastAPI

from api.config import configure_app
from api.menu import router as menu_router
from api.ordenes import router as ordenes_router
from repositories.database import lifespan

app = FastAPI(
    title="Restaurante API",
    version="0.1.0",
    description="API para la gestión de menú y órdenes de un restaurante.",
    lifespan=lifespan,
)

configure_app(app)
app.include_router(menu_router)
app.include_router(ordenes_router)


@app.get("/")
async def raiz() -> dict[str, str]:
    return {"mensaje": "API corriendo"}
