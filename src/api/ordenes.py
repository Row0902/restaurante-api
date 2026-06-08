"""Router con los endpoints de órdenes."""

from fastapi import APIRouter, Depends

from api.deps import get_orden_service
from core.schemas.estado_update import EstadoUpdate
from core.schemas.orden_create import OrdenCreate
from core.schemas.orden_read import OrdenRead
from services.ordenes import OrdenService

router = APIRouter(prefix="/ordenes", tags=["Órdenes"])


@router.get("", response_model=list[OrdenRead])
async def listar_ordenes(
    service: OrdenService = Depends(get_orden_service),
) -> list[OrdenRead]:
    return await service.listar()


@router.post("", response_model=OrdenRead, status_code=201)
async def crear_orden(
    datos: OrdenCreate,
    service: OrdenService = Depends(get_orden_service),
) -> OrdenRead:
    return await service.crear(datos)


@router.get("/{orden_id}", response_model=OrdenRead)
async def obtener_orden(
    orden_id: int,
    service: OrdenService = Depends(get_orden_service),
) -> OrdenRead:
    return await service.obtener(orden_id)


@router.put("/{orden_id}/estado", response_model=OrdenRead)
async def cambiar_estado_orden(
    orden_id: int,
    datos: EstadoUpdate,
    service: OrdenService = Depends(get_orden_service),
) -> OrdenRead:
    return await service.cambiar_estado(orden_id, datos)
