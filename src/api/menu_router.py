"""Router para menú."""

from typing import List

from fastapi import APIRouter, status

from api.deps import MenuServiceDep
from core.schemas import PlatoCreate, PlatoResponse, PlatoUpdate

router = APIRouter(prefix="/menu", tags=["Menú"])


@router.get("", response_model=List[PlatoResponse])
async def listar_menu(service: MenuServiceDep) -> List[PlatoResponse]:
    """Devuelve todos los platos del menú."""
    return await service.obtener_todos()


@router.post("", response_model=PlatoResponse, status_code=status.HTTP_201_CREATED)
async def crear_plato(plato_in: PlatoCreate, service: MenuServiceDep) -> PlatoResponse:
    """Crea un nuevo plato en el menú."""
    return await service.crear(plato_in)


@router.get("/{plato_id}", response_model=PlatoResponse)
async def obtener_plato(plato_id: str, service: MenuServiceDep) -> PlatoResponse:
    """Obtiene un plato por su ID."""
    return await service.obtener_por_id(plato_id)


@router.put("/{plato_id}", response_model=PlatoResponse)
async def actualizar_plato(
    plato_id: str, plato_in: PlatoUpdate, service: MenuServiceDep
) -> PlatoResponse:
    """Actualiza un plato existente."""
    return await service.actualizar(plato_id, plato_in)


@router.delete("/{plato_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_plato(plato_id: str, service: MenuServiceDep) -> None:
    """Elimina un plato del menú."""
    await service.eliminar(plato_id)
