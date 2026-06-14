"""Router HTTP para ordenes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import obtener_orden_service
from api.http_errors import ejecutar_caso_de_uso
from api.schemas.estado_orden_request import EstadoOrdenRequest
from api.schemas.orden_request import OrdenRequest
from api.schemas.orden_response import OrdenResponse
from services.orden_service import OrdenService

router = APIRouter(prefix="/ordenes", tags=["Ordenes"])
OrdenServiceDep = Annotated[OrdenService, Depends(obtener_orden_service)]


@router.get("", response_model=list[OrdenResponse])
async def listar_ordenes(
    service: OrdenServiceDep,
) -> list[dict[str, object]]:
    """Devuelve todas las ordenes registradas."""
    return await ejecutar_caso_de_uso(service.listar())


@router.post("", response_model=OrdenResponse)
async def crear_orden(
    orden: OrdenRequest,
    service: OrdenServiceDep,
) -> dict[str, object]:
    """Crea una nueva orden con items del menu."""
    datos = orden.model_dump()
    return await ejecutar_caso_de_uso(service.crear(datos))


@router.get("/{orden_id}", response_model=OrdenResponse)
async def obtener_orden(
    orden_id: str,
    service: OrdenServiceDep,
) -> dict[str, object]:
    """Obtiene una orden por su ID."""
    return await ejecutar_caso_de_uso(service.obtener(orden_id))


@router.put("/{orden_id}/estado", response_model=OrdenResponse)
async def cambiar_estado_orden(
    orden_id: str,
    estado: EstadoOrdenRequest,
    service: OrdenServiceDep,
) -> dict[str, object]:
    """Cambia el estado de una orden."""
    datos = estado.model_dump()
    return await ejecutar_caso_de_uso(service.cambiar_estado(orden_id, datos))
