"""Entidad de dominio Orden."""

from dataclasses import dataclass, replace

from core.dominio_error import DominioError
from core.estado_orden import EstadoOrden
from core.item_orden import ItemOrden
from core.precio import Precio


@dataclass(frozen=True)
class Orden:
    """Representa una orden de restaurante."""

    id: str
    items: tuple[ItemOrden, ...]
    estado: EstadoOrden = EstadoOrden.PENDIENTE

    def __post_init__(self) -> None:
        """Valida identidad y normaliza items."""
        self._validar_id()
        object.__setattr__(self, "items", tuple(self.items))

    def total(self) -> Precio:
        """Calcula el total de la orden."""
        total = Precio("0")
        for item in self.items:
            total = total.sumar(item.subtotal())
        return total

    def cambiar_estado(self, estado: EstadoOrden) -> Orden:
        """Devuelve una orden con el estado actualizado."""
        self.estado.validar_transicion_a(estado)
        return replace(self, estado=estado)

    def _validar_id(self) -> None:
        if not self.id.strip():
            raise DominioError("id de orden requerido")
