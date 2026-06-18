"""Router de menú — endpoints CRUD para platos del menú.

Dependencia: ``MenuService`` inyectado via ``Depends``.
"""

from fastapi import APIRouter, Depends

from api.deps import get_menu_service
from core.schemas.menu_item import CreatePlatoRequest, PlatoResponse
from services.menu import MenuService

router = APIRouter(prefix="/menu", tags=["Menú"])


@router.get("/", response_model=list[PlatoResponse])
async def listar_menu(
    service: MenuService = Depends(get_menu_service),
) -> list[PlatoResponse]:
    """Devuelve todos los platos del menú."""
    return await service.listar()


@router.post("/", response_model=PlatoResponse)
async def crear_plato(
    request: CreatePlatoRequest,
    service: MenuService = Depends(get_menu_service),
) -> PlatoResponse:
    """Crea un nuevo plato en el menú.

    Args:
        request: Datos validados del plato.
        service: Servicio de menú inyectado.

    Returns:
        Plato creado con ID asignado.
    """
    return await service.crear(request)


@router.get("/{plato_id}", response_model=PlatoResponse)
async def obtener_plato(
    plato_id: int,
    service: MenuService = Depends(get_menu_service),
) -> PlatoResponse:
    """Obtiene un plato por su ID.

    Args:
        plato_id: ID numérico del plato.

    Returns:
        Plato encontrado.

    Raises:
        404: Si el plato no existe.
    """
    return await service.obtener_por_id(plato_id)


@router.put("/{plato_id}", response_model=PlatoResponse)
async def actualizar_plato(
    plato_id: int,
    request: CreatePlatoRequest,
    service: MenuService = Depends(get_menu_service),
) -> PlatoResponse:
    """Actualiza un plato existente con todos los campos requeridos.

    Args:
        plato_id: ID del plato a actualizar.
        request: Datos validados (todos los campos requeridos).

    Returns:
        Plato actualizado.
    """
    return await service.actualizar(plato_id, request)


@router.delete("/{plato_id}")
async def eliminar_plato(
    plato_id: int,
    service: MenuService = Depends(get_menu_service),
) -> dict[str, object]:
    """Elimina un plato del menú.

    Args:
        plato_id: ID del plato a eliminar.

    Returns:
        Mensaje de confirmación con el ID eliminado.
    """
    return await service.eliminar(plato_id)
