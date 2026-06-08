"""API de restaurante."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.menu import router as menu_router
from api.ordenes import router as ordenes_router
from core.config import settings
from database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API para la gestión de menú y órdenes de un restaurante",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(menu_router)

app.include_router(ordenes_router)


@app.get("/")
async def raiz():
    """Health check."""
    return {"mensaje": "API corriendo 👋"}