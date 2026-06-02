# src/api/ordenes.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from core.schemas import OrdenCreate, OrdenEstadoUpdate, OrdenResponse
from repositories.menu import MenuRepository
from repositories.ordenes import OrdenesRepository
from services.ordenes import OrdenesService

router = APIRouter(prefix="/ordenes", tags=["Órdenes"])


def get_ordenes_service(session: AsyncSession = Depends(get_session)) -> OrdenesService:
    return OrdenesService(OrdenesRepository(session), MenuRepository(session))


@router.get("/", response_model=list[OrdenResponse])
async def listar_ordenes(service: OrdenesService = Depends(get_ordenes_service)):
    return await service.listar()


@router.post("/", response_model=OrdenResponse, status_code=status.HTTP_201_CREATED)
async def crear_orden(
    data: OrdenCreate,
    service: OrdenesService = Depends(get_ordenes_service),
):
    return await service.crear(data)


@router.get("/{orden_id}", response_model=OrdenResponse)
async def obtener_orden(
    orden_id: int,
    service: OrdenesService = Depends(get_ordenes_service),
):
    return await service.obtener(orden_id)


@router.put("/{orden_id}/estado", response_model=OrdenResponse)
async def cambiar_estado_orden(
    orden_id: int,
    data: OrdenEstadoUpdate,
    service: OrdenesService = Depends(get_ordenes_service),
):
    return await service.cambiar_estado(orden_id, data)
