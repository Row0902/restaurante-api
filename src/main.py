from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    return {"mensaje": "API corriendo 👋"}


# "Base de datos" — un dict en memoria, sin tipos, sin nada
menu = {}
ordenes = {}


# --- MENU ---


@app.get("/menu", tags=["Menú"])
def listar_menu():
    print("Listando menu...")
    return list(menu.values())


@app.post("/menu", tags=["Menú"])
def crear_plato(plato: dict):
    id = str(len(menu) + 1)
    menu[id] = {"id": id, **plato}
    print(f"Plato creado: {menu[id]}")
    return menu[id]


@app.get("/menu/{plato_id}", tags=["Menú"])
def obtener_plato(plato_id: str):
    print(f"Buscando plato: {plato_id}")
    return menu[plato_id]


@app.put("/menu/{plato_id}", tags=["Menú"])
def actualizar_plato(plato_id: str, plato: dict):
    menu[plato_id] = {"id": plato_id, **plato}
    print(f"Plato actualizado: {menu[plato_id]}")
    return menu[plato_id]


@app.delete("/menu/{plato_id}", tags=["Menú"])
def eliminar_plato(plato_id: str):
    eliminado = menu.pop(plato_id)
    print(f"Plato eliminado: {eliminado}")
    return {"mensaje": "Plato eliminado", "id": plato_id}


# --- ORDENES ---


@app.get("/ordenes", tags=["Órdenes"])
def listar_ordenes():
    print("Listando ordenes...")
    return list(ordenes.values())


@app.post("/ordenes", tags=["Órdenes"])
def crear_orden(orden: dict):
    id = str(len(ordenes) + 1)
    total = 0
    items = orden.get("items", [])
    for item in items:
        plato_id = item.get("plato_id")
        cantidad = item.get("cantidad", 1)
        plato = menu[plato_id]  # si no existe, explota con 500
        total += plato["precio"] * cantidad
    ordenes[id] = {
        "id": id,
        "items": items,
        "total": total,
        "estado": "pendiente",
    }
    print(f"Orden creada: {ordenes[id]}")
    return ordenes[id]


@app.get("/ordenes/{orden_id}", tags=["Órdenes"])
def obtener_orden(orden_id: str):
    print(f"Buscando orden: {orden_id}")
    return ordenes[orden_id]


@app.put("/ordenes/{orden_id}/estado", tags=["Órdenes"])
def cambiar_estado_orden(orden_id: str, estado: dict):
    print(f"Cambiando estado de orden {orden_id} a {estado}")
    ordenes[orden_id]["estado"] = estado.get("estado")
    return ordenes[orden_id]
