"""Router con los endpoints del menú de platos."""

from fastapi import APIRouter, Depends

from api.deps import get_menu_service
from core.schemas.plato_create import PlatoCreate
from core.schemas.plato_read import PlatoRead
from core.schemas.plato_update import PlatoUpdate
from services.menu import MenuService

router = APIRouter(prefix="/menu", tags=["Menú"])


@router.get("", response_model=list[PlatoRead])
async def listar_menu(
    service: MenuService = Depends(get_menu_service),
) -> list[PlatoRead]:
    return await service.listar()


@router.post("", response_model=PlatoRead, status_code=201)
async def crear_plato(
    datos: PlatoCreate,
    service: MenuService = Depends(get_menu_service),
) -> PlatoRead:
    return await service.crear(datos)


@router.get("/{plato_id}", response_model=PlatoRead)
async def obtener_plato(
    plato_id: int,
    service: MenuService = Depends(get_menu_service),
) -> PlatoRead:
    return await service.obtener(plato_id)


@router.put("/{plato_id}", response_model=PlatoRead)
async def actualizar_plato(
    plato_id: int,
    datos: PlatoUpdate,
    service: MenuService = Depends(get_menu_service),
) -> PlatoRead:
    return await service.actualizar(plato_id, datos)


@router.delete("/{plato_id}", status_code=204)
async def eliminar_plato(
    plato_id: int,
    service: MenuService = Depends(get_menu_service),
) -> None:
    await service.eliminar(plato_id)
