"""Router para órdenes."""

from typing import List

from fastapi import APIRouter, status

from api.deps import OrdenServiceDep
from core.schemas import OrdenCreate, OrdenResponse, OrdenUpdateEstado

router = APIRouter(prefix="/ordenes", tags=["Órdenes"])


@router.get("", response_model=List[OrdenResponse])
async def listar_ordenes(service: OrdenServiceDep) -> List[OrdenResponse]:
    """Devuelve todas las órdenes registradas."""
    return await service.obtener_todas()


@router.post("", response_model=OrdenResponse, status_code=status.HTTP_201_CREATED)
async def crear_orden(orden_in: OrdenCreate, service: OrdenServiceDep) -> OrdenResponse:
    """Crea una nueva orden con ítems del menú."""
    return await service.crear(orden_in)


@router.get("/{orden_id}", response_model=OrdenResponse)
async def obtener_orden(orden_id: str, service: OrdenServiceDep) -> OrdenResponse:
    """Obtiene una orden por su ID."""
    return await service.obtener_por_id(orden_id)


@router.put("/{orden_id}/estado", response_model=OrdenResponse)
async def cambiar_estado_orden(
    orden_id: str, estado_in: OrdenUpdateEstado, service: OrdenServiceDep
) -> OrdenResponse:
    """Cambia el estado de una orden."""
    return await service.cambiar_estado(orden_id, estado_in.estado)


@router.delete("/{orden_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_orden(orden_id: str, service: OrdenServiceDep):
    """Elimina una orden por su ID."""
    await service.eliminar(orden_id)
