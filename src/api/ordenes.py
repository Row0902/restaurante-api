"""Router de órdenes — endpoints CRUD y cambio de estado.

Dependencia: ``OrderService`` inyectado via ``Depends``.
"""

from fastapi import APIRouter, Depends

from api.deps import get_order_service
from core.schemas.order import (
    CreateOrdenRequest,
    EstadoUpdateRequest,
    OrdenResponse,
)
from services.ordenes import OrderService

router = APIRouter(prefix="/ordenes", tags=["Órdenes"])


@router.get("/", response_model=list[OrdenResponse])
async def listar_ordenes(
    service: OrderService = Depends(get_order_service),
) -> list[OrdenResponse]:
    """Devuelve todas las órdenes registradas."""
    return await service.listar()


@router.post("/", response_model=OrdenResponse)
async def crear_orden(
    request: CreateOrdenRequest,
    service: OrderService = Depends(get_order_service),
) -> OrdenResponse:
    """Crea una nueva orden calculando el total desde los precios del menú.

    Args:
        request: Items de la orden con plato_id y cantidad.
        service: Servicio de órdenes inyectado.

    Returns:
        Orden creada con ID, total calculado y estado \"pendiente\".
    """
    return await service.crear(request)


@router.get("/{orden_id}", response_model=OrdenResponse)
async def obtener_orden(
    orden_id: int,
    service: OrderService = Depends(get_order_service),
) -> OrdenResponse:
    """Obtiene una orden por su ID.

    Args:
        orden_id: ID numérico de la orden.

    Returns:
        Orden encontrada con sus items.

    Raises:
        404: Si la orden no existe.
    """
    return await service.obtener_por_id(orden_id)


@router.put("/{orden_id}/estado", response_model=OrdenResponse)
async def cambiar_estado_orden(
    orden_id: int,
    request: EstadoUpdateRequest,
    service: OrderService = Depends(get_order_service),
) -> OrdenResponse:
    """Cambia el estado de una orden con validación de transiciones — R1.

    Args:
        orden_id: ID de la orden.
        request: Nuevo estado válido.

    Returns:
        Orden con el estado actualizado.

    Raises:
        400: Si la transición no es válida.
        404: Si la orden no existe.
    """
    return await service.cambiar_estado(orden_id, request)
