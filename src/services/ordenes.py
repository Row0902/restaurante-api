"""Service layer for order business logic."""

from core.exceptions import NotFoundError
from core.models import Orden, OrdenItem
from core.schemas import OrdenCreate, OrdenItemSchema
from repositories.menu import MenuRepository
from repositories.ordenes import OrdenRepository


class OrdenService:
    """Service for order business logic."""

    def __init__(
        self,
        orden_repo: OrdenRepository,
        menu_repo: MenuRepository,
    ) -> None:
        """Initialize service with order and menu repositories."""
        self.orden_repo = orden_repo
        self.menu_repo = menu_repo

    async def list_all(self) -> list[Orden]:
        """Retrieve all orders."""
        return await self.orden_repo.get_all()

    async def get_by_id(self, orden_id: int) -> Orden:
        """Retrieve an order by ID."""
        orden = await self.orden_repo.get_by_id(orden_id)
        if orden is None:
            raise NotFoundError(f"Orden with id {orden_id} not found")
        return orden

    async def create(self, data: OrdenCreate) -> Orden:
        """Create a new order with calculated total."""
        total = await self._calculate_total(data.items)
        items = [OrdenItem(**item.model_dump()) for item in data.items]
        orden = Orden(items=items, total=total)
        return await self.orden_repo.add(orden)

    async def update_estado(self, orden_id: int, estado: str) -> Orden:
        """Update order status."""
        orden = await self.orden_repo.update_estado(orden_id, estado)
        if orden is None:
            raise NotFoundError(f"Orden with id {orden_id} not found")
        return orden

    async def _calculate_total(self, items: list[OrdenItemSchema]) -> float:
        """Calculate order total from menu prices."""
        total = 0.0
        for item in items:
            plato = await self.menu_repo.get_by_id(item.plato_id)
            if plato is None:
                raise NotFoundError(f"Menu item {item.plato_id} not found")
            total += plato.precio * item.cantidad
        return total
