"""API de restaurante — menú y órdenes.

Monolito inicial para el curso de AI-Driven Development.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from repositories.in_memory_menu_repository import InMemoryMenuRepository
from repositories.in_memory_orden_repository import InMemoryOrdenRepository
from services.menu_service import MenuService
from services.orden_service import OrdenService

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
def raiz() -> dict[str, str]:
    """Endpoint raíz — health check."""
    return {"mensaje": "API corriendo 👋"}


# "Base de datos" — un dict en memoria, sin tipos, sin nada
menu: dict[str, dict[str, object]] = {}
ordenes: dict[str, dict[str, object]] = {}
menu_repository = InMemoryMenuRepository(menu)
orden_repository = InMemoryOrdenRepository(ordenes)
menu_service = MenuService(menu_repository)
orden_service = OrdenService(orden_repository, menu_repository)


# --- MENU ---


@app.get("/menu", tags=["Menú"])
async def listar_menu() -> list[dict[str, object]]:
    """Devuelve todos los platos del menú.

    Returns:
        list: Lista de platos almacenados en memoria.
    """
    return await menu_service.listar()


@app.post("/menu", tags=["Menú"])
async def crear_plato(plato: dict[str, object]) -> dict[str, object]:
    """Crea un nuevo plato en el menú.

    Args:
        plato (dict): Datos del plato sin validar.

    Returns:
        dict: Plato creado con ID asignado.
    """
    return await menu_service.crear(plato)


@app.get("/menu/{plato_id}", tags=["Menú"])
async def obtener_plato(plato_id: str) -> dict[str, object]:
    """Obtiene un plato por su ID.

    Args:
        plato_id (str): ID del plato.

    Returns:
        dict: Datos del plato.

    Raises:
        KeyError: Si el plato no existe.
    """
    return await menu_service.obtener(plato_id)


@app.put("/menu/{plato_id}", tags=["Menú"])
async def actualizar_plato(
    plato_id: str,
    plato: dict[str, object],
) -> dict[str, object]:
    """Actualiza un plato existente.

    Args:
        plato_id (str): ID del plato a actualizar.
        plato (dict): Nuevos datos del plato.

    Returns:
        dict: Plato actualizado.
    """
    return await menu_service.actualizar(plato_id, plato)


@app.delete("/menu/{plato_id}", tags=["Menú"])
async def eliminar_plato(plato_id: str) -> dict[str, object]:
    """Elimina un plato del menú.

    Args:
        plato_id (str): ID del plato a eliminar.

    Returns:
        dict: Mensaje de confirmación e ID eliminado.

    Raises:
        KeyError: Si el plato no existe.
    """
    return await menu_service.eliminar(plato_id)


# --- ORDENES ---


@app.get("/ordenes", tags=["Órdenes"])
async def listar_ordenes() -> list[dict[str, object]]:
    """Devuelve todas las órdenes registradas.

    Returns:
        list: Lista de órdenes almacenadas en memoria.
    """
    return await orden_service.listar()


@app.post("/ordenes", tags=["Órdenes"])
async def crear_orden(orden: dict[str, object]) -> dict[str, object]:
    """Crea una nueva orden con ítems del menú.

    Calcula el total automáticamente a partir de los precios del menú.

    Args:
        orden (dict): Orden con lista de ítems (plato_id, cantidad).

    Returns:
        dict: Orden creada con ID, total calculado y estado "pendiente".

    Raises:
        KeyError: Si algún plato_id no existe en el menú.
    """
    return await orden_service.crear(orden)


@app.get("/ordenes/{orden_id}", tags=["Órdenes"])
async def obtener_orden(orden_id: str) -> dict[str, object]:
    """Obtiene una orden por su ID.

    Args:
        orden_id (str): ID de la orden.

    Returns:
        dict: Datos de la orden.

    Raises:
        KeyError: Si la orden no existe.
    """
    return await orden_service.obtener(orden_id)


@app.put("/ordenes/{orden_id}/estado", tags=["Órdenes"])
async def cambiar_estado_orden(
    orden_id: str,
    estado: dict[str, object],
) -> dict[str, object]:
    """Cambia el estado de una orden.

    Args:
        orden_id (str): ID de la orden.
        estado (dict): Nuevo estado (ej. {"estado": "entregado"}).

    Returns:
        dict: Orden con el estado actualizado.

    Raises:
        KeyError: Si la orden no existe.
    """
    return await orden_service.cambiar_estado(orden_id, estado)
