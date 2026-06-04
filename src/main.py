"""API de restaurante — menú y órdenes (refactor parcial).

This module keeps route paths in Spanish for backwards compatibility but uses
Pydantic schemas for validation (internal names are English; public JSON keys are Spanish).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4, UUID
from core.schemas import DishCreate, OrderCreate
from repositories.in_memory_repository import InMemoryRepository

# instantiate the in-memory repository (will be injected later)
repo = InMemoryRepository()

APP_NAME = "Restaurante API"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "API para la gestión de menú y órdenes de un restaurante."

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)

# Keep permissive CORS for local development; tighten later via env config.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def raiz():
    """Endpoint raíz — health check."""
    return {"mensaje": "API corriendo 👋"}


# In-memory storage (temporary). Keys are string UUIDs.
menu = {}
ordenes = {}


# --- MENU ---


@app.get("/menu", tags=["Menú"])
async def listar_menu():
    """Devuelve todos los platos del menú."""
    dishes = await repo.list_dishes()
    # serialize to Spanish-keyed dicts
    return [d.dict(by_alias=True) for d in dishes]


@app.post("/menu", tags=["Menú"], status_code=201)
async def crear_plato(plato: DishCreate):
    """Crea un nuevo plato validado por Pydantic (aliases en español)."""
    created = await repo.create_dish(plato)
    return created.dict(by_alias=True)


@app.get("/menu/{plato_id}", tags=["Menú"])
async def obtener_plato(plato_id: UUID):
    """Obtiene un plato por su ID (UUID validation done by FastAPI)."""
    dish = await repo.get_dish(plato_id)
    return dish.dict(by_alias=True)


@app.put("/menu/{plato_id}", tags=["Menú"])
async def actualizar_plato(plato_id: UUID, plato: DishCreate):
    """Actualiza un plato existente."""
    updated = await repo.update_dish(plato_id, plato)
    return updated.dict(by_alias=True)


@app.delete("/menu/{plato_id}", tags=["Menú"])
async def eliminar_plato(plato_id: UUID):
    """Elimina un plato del menú."""
    await repo.delete_dish(plato_id)
    return {"mensaje": "Plato eliminado", "id": str(plato_id)}


# --- ORDENES ---


@app.get("/ordenes", tags=["Órdenes"])
async def listar_ordenes():
    """Devuelve todas las órdenes registradas."""
    orders = await repo.list_orders()
    return [o.dict(by_alias=True) for o in orders]


@app.post("/ordenes", tags=["Órdenes"], status_code=201)
async def crear_orden(orden: OrderCreate):
    """Crea una nueva orden con ítems del menú y calcula el total."""
    created = await repo.create_order(orden)
    return created.dict(by_alias=True)


@app.get("/ordenes/{orden_id}", tags=["Órdenes"])
async def obtener_orden(orden_id: UUID):
    order = await repo.get_order(orden_id)
    return order.dict(by_alias=True)


@app.put("/ordenes/{orden_id}/estado", tags=["Órdenes"])
async def cambiar_estado_orden(orden_id: UUID, estado: dict):
    updated = await repo.update_order_status(orden_id, estado.get("estado"))
    return updated.dict(by_alias=True)
