"""API de restaurante — menú y órdenes (refactor parcial).

This module keeps route paths in Spanish for backwards compatibility but uses
Pydantic schemas for validation (internal names are English; public JSON keys are Spanish).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4, UUID
from core.schemas import DishCreate, OrderCreate

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
    return list(menu.values())


@app.post("/menu", tags=["Menú"], status_code=201)
async def crear_plato(plato: DishCreate):
    """Crea un nuevo plato validado por Pydantic (aliases en español)."""
    new_id = str(uuid4())
    # plato attributes are accessible by field names (name, description, price)
    menu[new_id] = {
        "id": new_id,
        "nombre": plato.name,
        "descripcion": plato.description,
        "precio": plato.price,
    }
    return menu[new_id]


@app.get("/menu/{plato_id}", tags=["Menú"])
async def obtener_plato(plato_id: UUID):
    """Obtiene un plato por su ID (UUID validation done by FastAPI)."""
    key = str(plato_id)
    return menu[key]


@app.put("/menu/{plato_id}", tags=["Menú"])
async def actualizar_plato(plato_id: UUID, plato: DishCreate):
    """Actualiza un plato existente."""
    key = str(plato_id)
    menu[key] = {
        "id": key,
        "nombre": plato.name,
        "descripcion": plato.description,
        "precio": plato.price,
    }
    return menu[key]


@app.delete("/menu/{plato_id}", tags=["Menú"])
async def eliminar_plato(plato_id: UUID):
    """Elimina un plato del menú."""
    key = str(plato_id)
    eliminado = menu.pop(key)
    return {"mensaje": "Plato eliminado", "id": key}


# --- ORDENES ---


@app.get("/ordenes", tags=["Órdenes"])
async def listar_ordenes():
    """Devuelve todas las órdenes registradas."""
    return list(ordenes.values())


@app.post("/ordenes", tags=["Órdenes"], status_code=201)
async def crear_orden(orden: OrderCreate):
    """Crea una nueva orden con ítems del menú y calcula el total."""
    new_id = str(uuid4())
    total = 0.0
    items_out = []
    for item in orden.items:
        dish_key = str(item.dish_id)
        cantidad = item.quantity
        # If dish_key not present this will raise KeyError -> 500 for now.
        dish = menu[dish_key]
        total += dish["precio"] * cantidad
        items_out.append({"plato_id": dish_key, "cantidad": cantidad})
    ordenes[new_id] = {
        "id": new_id,
        "items": items_out,
        "total": total,
        "estado": "pendiente",
    }
    return ordenes[new_id]


@app.get("/ordenes/{orden_id}", tags=["Órdenes"])
async def obtener_orden(orden_id: UUID):
    key = str(orden_id)
    return ordenes[key]


@app.put("/ordenes/{orden_id}/estado", tags=["Órdenes"])
async def cambiar_estado_orden(orden_id: UUID, estado: dict):
    key = str(orden_id)
    ordenes[key]["estado"] = estado.get("estado")
    return ordenes[key]
