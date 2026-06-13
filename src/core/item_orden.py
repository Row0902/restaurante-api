"""Entidad de dominio ItemOrden."""

from dataclasses import dataclass

from core.cantidad import Cantidad
from core.dominio_error import DominioError
from core.precio import Precio


@dataclass(frozen=True)
class ItemOrden:
    """Representa un plato solicitado dentro de una orden."""

    plato_id: str
    cantidad: Cantidad
    precio_unitario: Precio

    def __post_init__(self) -> None:
        """Valida la referencia al plato."""
        self._validar_plato_id()

    def subtotal(self) -> Precio:
        """Calcula el subtotal del item."""
        return self.precio_unitario.multiplicar_por(self.cantidad.valor)

    def _validar_plato_id(self) -> None:
        if not self.plato_id.strip():
            raise DominioError("id de plato requerido")
