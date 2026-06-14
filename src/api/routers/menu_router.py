"""Router HTTP para menu."""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import obtener_menu_service
from api.http_errors import ejecutar_caso_de_uso
from api.schemas.plato_eliminado_response import PlatoEliminadoResponse
from api.schemas.plato_request import PlatoRequest
from api.schemas.plato_response import PlatoResponse
from api.schemas.plato_update_request import PlatoUpdateRequest
from services.menu_service import MenuService

router = APIRouter(prefix="/menu", tags=["Menu"])
MenuServiceDep = Annotated[MenuService, Depends(obtener_menu_service)]


@router.get("", response_model=list[PlatoResponse], response_model_exclude_none=True)
async def listar_menu(
    service: MenuServiceDep,
) -> list[dict[str, object]]:
    """Devuelve todos los platos del menu."""
    return await ejecutar_caso_de_uso(service.listar())


@router.post("", response_model=PlatoResponse, response_model_exclude_none=True)
async def crear_plato(
    plato: PlatoRequest,
    service: MenuServiceDep,
) -> dict[str, object]:
    """Crea un nuevo plato en el menu."""
    datos = plato.model_dump()
    return await ejecutar_caso_de_uso(service.crear(datos))


@router.get(
    "/{plato_id}",
    response_model=PlatoResponse,
    response_model_exclude_none=True,
)
async def obtener_plato(
    plato_id: str,
    service: MenuServiceDep,
) -> dict[str, object]:
    """Obtiene un plato por su ID."""
    return await ejecutar_caso_de_uso(service.obtener(plato_id))


@router.put(
    "/{plato_id}",
    response_model=PlatoResponse,
    response_model_exclude_none=True,
)
async def actualizar_plato(
    plato_id: str,
    plato: PlatoUpdateRequest,
    service: MenuServiceDep,
) -> dict[str, object]:
    """Actualiza un plato existente."""
    datos = plato.model_dump(exclude_none=True)
    return await ejecutar_caso_de_uso(service.actualizar(plato_id, datos))


@router.delete("/{plato_id}", response_model=PlatoEliminadoResponse)
async def eliminar_plato(
    plato_id: str,
    service: MenuServiceDep,
) -> dict[str, object]:
    """Elimina un plato del menu."""
    return await ejecutar_caso_de_uso(service.eliminar(plato_id))
