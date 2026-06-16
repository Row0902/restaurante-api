"""Menu API router — CRUD endpoints for menu items.

All handlers delegate to MenuService via dependency injection.
Domain exceptions are translated to HTTP status codes.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_menu_service
from core.exceptions import InvalidMenuDataError, MenuNotFoundError
from core.models.menu import MenuItem
from core.schemas.menu import PlatoCreate, PlatoResponse, PlatoUpdate
from services.menu import MenuService

router = APIRouter(prefix="/menu", tags=["Menú"])


@router.get("", response_model=list[PlatoResponse])
async def listar_menu(
    service: MenuService = Depends(get_menu_service),  # noqa: B008
) -> list[MenuItem]:
    """Return all menu items."""
    return await service.get_all()


@router.post("", response_model=PlatoResponse, status_code=status.HTTP_201_CREATED)
async def crear_plato(
    data: PlatoCreate,
    service: MenuService = Depends(get_menu_service),  # noqa: B008
) -> MenuItem:
    """Create a new menu item after validation."""
    try:
        return await service.create(data)
    except InvalidMenuDataError as e:
        raise HTTPException(status_code=422, detail=str(e)) from None


@router.get("/{plato_id}", response_model=PlatoResponse)
async def obtener_plato(
    plato_id: int,
    service: MenuService = Depends(get_menu_service),  # noqa: B008
) -> MenuItem:
    """Return a menu item by its ID."""
    try:
        return await service.get_by_id(plato_id)
    except MenuNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.put("/{plato_id}", response_model=PlatoResponse)
async def actualizar_plato(
    plato_id: int,
    data: PlatoUpdate,
    service: MenuService = Depends(get_menu_service),  # noqa: B008
) -> MenuItem:
    """Update a menu item after validation."""
    try:
        return await service.update(plato_id, data)
    except MenuNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
    except InvalidMenuDataError as e:
        raise HTTPException(status_code=422, detail=str(e)) from None


@router.delete("/{plato_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_plato(
    plato_id: int,
    service: MenuService = Depends(get_menu_service),  # noqa: B008
) -> None:
    """Delete a menu item by its ID."""
    try:
        await service.delete(plato_id)
    except MenuNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
