# src/api/menu.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from core.schemas import PlatoCreate, PlatoResponse, PlatoUpdate
from repositories.menu import MenuRepository
from services.menu import MenuService

router = APIRouter(prefix="/menu", tags=["Menú"])


def get_menu_service(session: AsyncSession = Depends(get_session)) -> MenuService:
    return MenuService(MenuRepository(session))


@router.get("/", response_model=list[PlatoResponse])
async def listar_menu(service: MenuService = Depends(get_menu_service)):
    return await service.listar()


@router.post("/", response_model=PlatoResponse, status_code=status.HTTP_201_CREATED)
async def crear_plato(
    data: PlatoCreate,
    service: MenuService = Depends(get_menu_service),
):
    return await service.crear(data)


@router.get("/{plato_id}", response_model=PlatoResponse)
async def obtener_plato(
    plato_id: int,
    service: MenuService = Depends(get_menu_service),
):
    return await service.obtener(plato_id)


@router.put("/{plato_id}", response_model=PlatoResponse)
async def actualizar_plato(
    plato_id: int,
    data: PlatoUpdate,
    service: MenuService = Depends(get_menu_service),
):
    return await service.actualizar(plato_id, data)


@router.delete("/{plato_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_plato(
    plato_id: int,
    service: MenuService = Depends(get_menu_service),
):
    await service.eliminar(plato_id)