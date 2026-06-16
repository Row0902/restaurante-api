"""Orden API router — CRUD + estado transition endpoints for orders.

All handlers delegate to OrdenesService via dependency injection.
Domain exceptions are translated to HTTP status codes.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_orden_service
from core.exceptions import (
    InvalidEstadoTransitionError,
    InvalidOrdenDataError,
    MenuNotFoundError,
    OrdenNotFoundError,
)
from core.models.orden import Orden
from core.schemas.orden import OrdenCreate, OrdenResponse, OrdenUpdateEstado
from services.orden import OrdenesService

router = APIRouter(prefix="/ordenes", tags=["Órdenes"])


@router.get("", response_model=list[OrdenResponse])
async def listar_ordenes(
    service: OrdenesService = Depends(get_orden_service),  # noqa: B008
) -> list[Orden]:
    """Return all orders."""
    return await service.get_all()


@router.post("", response_model=OrdenResponse, status_code=status.HTTP_201_CREATED)
async def crear_orden(
    data: OrdenCreate,
    service: OrdenesService = Depends(get_orden_service),  # noqa: B008
) -> Orden:
    """Create a new order after validation and price resolution."""
    try:
        return await service.create(data)
    except InvalidOrdenDataError as e:
        raise HTTPException(status_code=422, detail=str(e)) from None
    except MenuNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.get("/{orden_id}", response_model=OrdenResponse)
async def obtener_orden(
    orden_id: int,
    service: OrdenesService = Depends(get_orden_service),  # noqa: B008
) -> Orden:
    """Return an order by its ID."""
    try:
        return await service.get_by_id(orden_id)
    except OrdenNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.put("/{orden_id}/estado", response_model=OrdenResponse)
async def cambiar_estado(
    orden_id: int,
    data: OrdenUpdateEstado,
    service: OrdenesService = Depends(get_orden_service),  # noqa: B008
) -> Orden:
    """Change the estado of an order with polymorphic transition validation."""
    try:
        return await service.cambiar_estado(orden_id, data.estado)
    except OrdenNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
    except InvalidEstadoTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
