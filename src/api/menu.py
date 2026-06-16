"""API router for menu endpoints."""

from fastapi import APIRouter, status

from api.deps import MenuServiceDep
from core.models import Plato
from core.schemas import PlatoCreate, PlatoResponse, PlatoUpdate

router = APIRouter(prefix="/menu", tags=["Menú"])


@router.get("", response_model=list[PlatoResponse])
async def list_menu(service: MenuServiceDep) -> list[Plato]:
    """List all menu items."""
    return await service.list_all()


@router.post(
    "",
    response_model=PlatoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_plato(
    data: PlatoCreate,
    service: MenuServiceDep,
) -> Plato:
    """Create a new menu item."""
    return await service.create(data)


@router.get("/{plato_id}", response_model=PlatoResponse)
async def get_plato(plato_id: int, service: MenuServiceDep) -> Plato:
    """Get a menu item by ID."""
    return await service.get_by_id(plato_id)


@router.put("/{plato_id}", response_model=PlatoResponse)
async def update_plato(
    plato_id: int,
    data: PlatoUpdate,
    service: MenuServiceDep,
) -> Plato:
    """Update an existing menu item."""
    return await service.update(plato_id, data)


@router.delete("/{plato_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plato(plato_id: int, service: MenuServiceDep) -> None:
    """Delete a menu item."""
    await service.delete(plato_id)
