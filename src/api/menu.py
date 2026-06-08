from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from core.schemas import PlatoCreate, PlatoUpdate
from database import get_session
from repositories.menu import MenuRepository
from services.menu import MenuService

router = APIRouter(
    prefix="/menu",
    tags=["Menú"],
)

def get_menu_service(
    session: AsyncSession = Depends(get_session),
):
    repository = MenuRepository(session)
    return MenuService(repository)


@router.get("/")
async def listar_menu(
    service: MenuService = Depends(get_menu_service),
):
    return await service.listar()


@router.post("/")
async def crear_plato(
    plato: PlatoCreate,
    service: MenuService = Depends(get_menu_service),
):
    return await service.crear(plato)


@router.get("/{plato_id}")
async def obtener_plato(
    plato_id: int,
    service: MenuService = Depends(get_menu_service),
):
    return await service.obtener(plato_id)


@router.put("/{plato_id}")
async def actualizar_plato(
    plato_id: int,
    plato: PlatoUpdate,
    service: MenuService = Depends(get_menu_service),
):
    return await service.actualizar(plato_id, plato)


@router.delete("/{plato_id}")
async def eliminar_plato(
    plato_id: int,
    service: MenuService = Depends(get_menu_service),
):
    return await service.eliminar(plato_id)