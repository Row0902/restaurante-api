"""OrdenesService — business logic orchestration for order operations.

Receives OrdenRepository and MenuRepository via constructor injection.
Validates input schemas polymorphically, resolves menu prices, then
delegates to the repository layer. Zero knowledge of HTTP or sessions.
"""

from core.estado_orden import validar_transicion
from core.models.orden import Orden
from core.schemas.orden import OrdenCreate, OrdenUpdateEstado
from repositories.menu import MenuRepository
from repositories.orden import OrdenRepository


class OrdenesService:
    """Business logic for order operations.

    Orchestrates order creation with menu price lookup, estado transitions
    with polymorphic validation, and read operations via repository delegation.
    """

    def __init__(
        self,
        orden_repo: OrdenRepository,
        menu_repo: MenuRepository,
    ) -> None:
        """Inject both repositories — service never creates its own."""
        self._orden_repo = orden_repo
        self._menu_repo = menu_repo

    async def get_all(self) -> list[Orden]:
        """Return all orders via repository."""
        return await self._orden_repo.get_all()

    async def get_by_id(self, orden_id: int) -> Orden:
        """Return one order by ID via repository.

        Raises OrdenNotFoundError when the order does not exist.
        """
        return await self._orden_repo.get_by_id(orden_id)

    async def create(self, data: OrdenCreate) -> Orden:
        """Validate, resolve prices, compute total, and persist a new order.

        Raises InvalidOrdenDataError on validation failure.
        Raises MenuNotFoundError when a menu item does not exist.
        Repository is NOT called when validation fails.
        """
        data.validate()
        items_data: list[dict] = []
        total = 0.0

        for item in data.items:
            menu_item = await self._menu_repo.get_by_id(item.plato_id)
            items_data.append(
                {
                    "plato_id": item.plato_id,
                    "cantidad": item.cantidad,
                    "precio_unitario": menu_item.precio,
                    "nombre": menu_item.nombre,
                }
            )
            total += menu_item.precio * item.cantidad

        return await self._orden_repo.create(data, items_data, total)

    async def cambiar_estado(
        self,
        orden_id: int,
        nuevo_estado: str,
    ) -> Orden:
        """Validate and apply an estado transition.

        Raises OrdenNotFoundError when the order does not exist.
        Raises InvalidEstadoTransitionError when the transition is forbidden.
        """
        orden = await self._orden_repo.get_by_id(orden_id)
        validar_transicion(orden.estado, nuevo_estado)
        data = OrdenUpdateEstado(estado=nuevo_estado)
        return await self._orden_repo.update(orden_id, data)

    async def delete(self, orden_id: int) -> None:
        """Delete an order by ID via repository.

        Raises OrdenNotFoundError when the order does not exist.
        """
        await self._orden_repo.delete(orden_id)
