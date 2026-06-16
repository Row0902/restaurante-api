"""API router for order endpoints."""

from fastapi import APIRouter, status

from api.deps import OrdenServiceDep
from core.models import Orden
from core.schemas import EstadoUpdate, OrdenCreate, OrdenResponse

router = APIRouter(prefix="/ordenes", tags=["Órdenes"])


@router.get("", response_model=list[OrdenResponse])
async def list_ordenes(service: OrdenServiceDep) -> list[Orden]:
    """List all orders."""
    return await service.list_all()


@router.post(
    "",
    response_model=OrdenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_orden(
    data: OrdenCreate,
    service: OrdenServiceDep,
) -> Orden:
    """Create a new order with calculated total."""
    return await service.create(data)


@router.get("/{orden_id}", response_model=OrdenResponse)
async def get_orden(orden_id: int, service: OrdenServiceDep) -> Orden:
    """Get an order by ID."""
    return await service.get_by_id(orden_id)


@router.put("/{orden_id}/estado", response_model=OrdenResponse)
async def update_estado(
    orden_id: int,
    data: EstadoUpdate,
    service: OrdenServiceDep,
) -> Orden:
    """Update order status."""
    return await service.update_estado(orden_id, data.estado)
