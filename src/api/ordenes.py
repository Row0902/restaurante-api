from fastapi import APIRouter, Depends

from core.schemas import (
    EstadoOrdenUpdate,
    OrdenCreate,
)
from database import get_session
from repositories.menu import MenuRepository
from repositories.ordenes import OrdenRepository
from services.ordenes import OrdenService

router = APIRouter(
    prefix="/ordenes",
    tags=["Órdenes"],
)


async def get_orden_service(
    session=Depends(get_session),
):
    orden_repo = OrdenRepository(session)
    menu_repo = MenuRepository(session)

    return OrdenService(
        orden_repo,
        menu_repo,
    )


@router.get("/")
async def listar_ordenes(
    service: OrdenService = Depends(
        get_orden_service
    ),
):
    return await service.listar()


@router.post("/")
async def crear_orden(
    orden: OrdenCreate,
    service: OrdenService = Depends(
        get_orden_service
    ),
):
    return await service.crear(orden)


@router.get("/{orden_id}")
async def obtener_orden(
    orden_id: int,
    service: OrdenService = Depends(
        get_orden_service
    ),
):
    return await service.obtener(
        orden_id
    )


@router.put("/{orden_id}/estado")
async def cambiar_estado(
    orden_id: int,
    estado: EstadoOrdenUpdate,
    service: OrdenService = Depends(
        get_orden_service
    ),
):
    return await service.cambiar_estado(
        orden_id,
        estado.estado,
    )