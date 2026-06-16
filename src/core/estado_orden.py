"""Estado state machine with polymorphic transition validation.

Each current estado variant implements its own puede_transicionar_a()
method — no if/match on type. Spec-granted grouping: all 6 classes
in a single file (each is 5-8 lines, separate files would create noise).
"""

from abc import ABC, abstractmethod

from core.exceptions import InvalidEstadoTransitionError


class EstadoOrden(ABC):
    """Abstract base for all order estado variants."""

    @abstractmethod
    def puede_transicionar_a(self, nuevo_estado: str) -> bool:
        """Return True if transition to nuevo_estado is allowed."""


class Pendiente(EstadoOrden):
    """Initial state. Can move to preparando or cancelado."""

    def puede_transicionar_a(self, nuevo_estado: str) -> bool:
        """Check if transition from pendiente is allowed."""
        return nuevo_estado in ("preparando", "cancelado")


class Preparando(EstadoOrden):
    """Order is being prepared. Can move to entregado or cancelado."""

    def puede_transicionar_a(self, nuevo_estado: str) -> bool:
        """Check if transition from preparando is allowed."""
        return nuevo_estado in ("entregado", "cancelado")


class Entregado(EstadoOrden):
    """Order has been delivered. Can move to pagado only."""

    def puede_transicionar_a(self, nuevo_estado: str) -> bool:
        """Check if transition from entregado is allowed."""
        return nuevo_estado in ("pagado",)


class Pagado(EstadoOrden):
    """Terminal state — no further transitions allowed."""

    def puede_transicionar_a(self, nuevo_estado: str) -> bool:
        """Terminal state — no transitions allowed."""
        return False


class Cancelado(EstadoOrden):
    """Terminal state — no further transitions allowed."""

    def puede_transicionar_a(self, nuevo_estado: str) -> bool:
        """Terminal state — no transitions allowed."""
        return False


_ESTADOS: dict[str, type[EstadoOrden]] = {
    "pendiente": Pendiente,
    "preparando": Preparando,
    "entregado": Entregado,
    "pagado": Pagado,
    "cancelado": Cancelado,
}


def validar_transicion(estado_actual: str, nuevo_estado: str) -> None:
    """Validate a state transition, raising InvalidEstadoTransitionError if forbidden."""
    estado_cls = _ESTADOS.get(estado_actual)
    if estado_cls is None:
        raise InvalidEstadoTransitionError(estado_actual, nuevo_estado)
    estado = estado_cls()
    if not estado.puede_transicionar_a(nuevo_estado):
        raise InvalidEstadoTransitionError(estado_actual, nuevo_estado)
