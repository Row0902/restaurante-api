"""Estados de dominio para una orden."""

from enum import StrEnum

from core.dominio_error import DominioError


class EstadoOrden(StrEnum):
    """Representa el ciclo de vida de una orden."""

    PENDIENTE = "pendiente"
    EN_PREPARACION = "en_preparacion"
    ENTREGADA = "entregada"
    CANCELADA = "cancelada"

    def permite_transicion_a(self, destino: EstadoOrden) -> bool:
        """Indica si la transicion al estado destino es valida."""
        return destino in TRANSICIONES_VALIDAS[self]

    def validar_transicion_a(self, destino: EstadoOrden) -> None:
        """Lanza error si la transicion al estado destino es invalida."""
        if not self.permite_transicion_a(destino):
            raise DominioError("transicion de estado invalida")


TRANSICIONES_VALIDAS: dict[EstadoOrden, set[EstadoOrden]] = {
    EstadoOrden.PENDIENTE: {EstadoOrden.EN_PREPARACION, EstadoOrden.CANCELADA},
    EstadoOrden.EN_PREPARACION: {EstadoOrden.ENTREGADA, EstadoOrden.CANCELADA},
    EstadoOrden.ENTREGADA: set(),
    EstadoOrden.CANCELADA: set(),
}
